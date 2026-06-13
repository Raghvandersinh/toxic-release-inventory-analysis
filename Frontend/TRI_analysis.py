import altair as alt
from vega_datasets import data
import pandas as pd 
from sqlalchemy import create_engine
from dotenv import load_dotenv
import time
import os 
import json
from us import states
import requests
from io import StringIO
from census import Census
import addfips
import TRI_data_processing
import TRI_chart_pieces as tcp
start_time = time.time()

alt.renderers.enable("mimetype")

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
with open('queries.json', 'r') as f:
    queries = json.load(f)



def total_waste_througout_from_top_10_facility_chart_generator():
    '''
    Outputs the line chart with the Top 10 facility with the most waste dumped throughout the years.
    Reads the Total_Waste_Throughout_top_10 query from queries.json. Outputs a line chart png with reporting_year as the X-axis and
    total_release as the Y-axis.
    '''
    
    total_waste_throught_from_top_10_df = pd.read_sql(queries["Total_Waste_Throughout_top_10"], con=engine)

    print(total_waste_throught_from_top_10_df.columns.to_list())
    print(f"DataFrame shape: {total_waste_throught_from_top_10_df.shape}")
    print(f"DataFrame memory usage: {total_waste_throught_from_top_10_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Unique names: {total_waste_throught_from_top_10_df['name'].nunique()}")

    total_waste_throughout_top_10_chart = alt.Chart(total_waste_throught_from_top_10_df).mark_line(
        strokeWidth=2,
        point=False  # Remove points for cleaner lines
    ).encode(
        x=alt.X('reporting_year:N', 
                axis=alt.Axis(labelAngle=-45, title='Date'),
                title=None),
        y=alt.Y('total_release:Q', 
                axis=alt.Axis(format=',.0f', title='Total Release (lbs)'),
                scale=alt.Scale(zero=False)),  # Don't force y-axis to start at 0
        color=alt.Color('name:N', 
                        legend=alt.Legend(title='Facility', orient='bottom', columns=2),
                        sort='-y')  # Sort legend by highest values
    ).properties(
        title={
            'text': 'Top 10 Facilities - Waste Release Trends',
            'subtitle': 'Monthly aggregated releases in pounds',
            'fontSize': 16,
            'anchor': 'start'
        },
        width=800,
        height=400
    ).configure_axis(
        grid=True,
        gridColor='lightgray',
        gridOpacity=0.5
    ).configure_view(
        strokeWidth=0  
    )

    total_waste_throughout_top_10_chart.save('Frontend/chart/total_waste_throughout_top_10.png')

def total_waste_by_state_throughout_or_After_2020(choice = ""):
    '''
    Outputs the geographical map displaying total waste released in specific US states, It also shows what is the release type 
    (Air, Water, or Land release) and if the checmical is Presistent, Cancer causing or forever living.   
    '''
    
    tcp.final_state_map_output(choices = choice)

def total_waste_by_counties_throughout_or_After_2020(choices = ""):
    '''
    Outputs the geographical map displaying total waste released in specific US counties, It also shows what is the release type 
    (Air, Water, or Land release) and if the checmical is Presistent, Cancer causing or forever living.  
    '''
    tcp.final_county_map_output(choices = choices)
    

def total_waste_througout_from_top_10_facility_chart_generator_interactive():
    
    '''
    Outputs a line chart with the Top 10 Facility who dumped the most waste throughout the years.
    Reads the Total_Waste_Throughout_top_10 query from queries.json. Outputs a line chart with reporting_year as the X-axis and
    total_release as the Y-axis with 'interactivity'.
    '''
    total_waste_throught_from_top_10_df = pd.read_sql(queries["Total_Waste_Throughout_top_10"], con=engine)

    # Just use one selection for legend filtering
    selection = alt.selection_point(
        fields=['name'],
        bind='legend',
        name='facility_select'
    )
    
    total_waste_throughout_top_10_chart = alt.Chart(total_waste_throught_from_top_10_df).mark_line(
        strokeWidth=2,
        point=alt.OverlayMarkDef(
            filled=True,
            size=50
        )
    ).encode(
        x=alt.X('reporting_year:N', 
                axis=alt.Axis(labelAngle=-45, title='Date'),
                title=None),
        y=alt.Y('total_release:Q', 
                axis=alt.Axis(format=',.0f', title='Total Release (lbs)'),
                scale=alt.Scale(zero=False)),
        color=alt.Color('name:N', 
                        legend=alt.Legend(title='Facility (click to filter)', orient='bottom', columns=2),
                        sort='-y'),
        tooltip=[
            alt.Tooltip('name:N', title='Facility'),
            alt.Tooltip('reporting_year:N', title='Date'),
            alt.Tooltip('total_release:Q', title='Total Release', format=',.0f'),
        ],
        # Only use opacity change based on legend selection
        opacity=alt.condition(selection, alt.value(1), alt.value(0))
    ).transform_filter(
        selection
    ).add_params(
        selection
    ).properties(
        title={
            'text': 'Top 10 Facilities - Waste Release Trends',
            'subtitle': 'Click legend to filter • Hover for details',
            'fontSize': 16,
            'anchor': 'start'
        },
        width=800,
        height=400
    ).configure_axis(
        grid=True,
        gridColor='lightgray',
        gridOpacity=0.5
    ).configure_view(
        strokeWidth=0  
    ).interactive()

    total_waste_throughout_top_10_chart.save('Frontend/chart/total_waste_throughout_top_10.html')
    
    return total_waste_throughout_top_10_chart


def total_waste_top_10_vs_rest_facilities_pie_chart():
    df = pd.read_sql(queries['Total_Waste_Top_10_Vs_Rest_Facilities'], con=engine)
    top_10_vs_rest_df = df.drop(index=2)  # Remove TOTAL row
    total = df.drop(index=[0, 1])  # Keep TOTAL row for reference
    
    print(df.head())
    
    # Calculate the midpoint angle for each slice to center the text
    top_10_vs_rest_df['mid_angle'] = top_10_vs_rest_df['percentage_of_total'].cumsum() - top_10_vs_rest_df['percentage_of_total'] / 2
    
    pie = alt.Chart(top_10_vs_rest_df).mark_arc(
        innerRadius=0,  
        stroke='white',
        strokeWidth=2
    ).encode(
        theta=alt.Theta('percentage_of_total:Q', stack=True),
        color=alt.Color('category:N',
                       scale=alt.Scale(scheme='category10'),
                       legend=alt.Legend(title='Facility Category', orient='right')),
        tooltip=[
            alt.Tooltip('category:N', title='Category'),
            alt.Tooltip('num_facilities:Q', title='Number of Facilities', format=','),
            alt.Tooltip('total_release:Q', title='Total Waste (lbs)', format=',.0f'),
            alt.Tooltip('percentage_of_total:Q', title='% of Total', format='.1f')
        ]
    ).properties(
        width=400,
        height=400,
        title={
            "text": "Top 10 Facilities vs All Others",
            "subtitle": f"Total Waste: {total['total_release'].values[0]:,.0f} lbs",
            "fontSize": 16,
            "anchor": "middle"
        }
    )
    
    # Add category labels OUTSIDE the pie
    text_labels = alt.Chart(top_10_vs_rest_df).mark_text(
        radius=140,  # Further outside
        fontSize=12,
        fontWeight='bold',
        align='center'
    ).encode(
        theta=alt.Theta('percentage_of_total:Q', stack=True),
        text=alt.Text('category:N'),
        color=alt.value('black')
    )
    
    # Add percentage labels CENTERED inside each pie slice
    percentage_labels = alt.Chart(top_10_vs_rest_df).mark_text(
        radius=70,  # Half of outer radius to center in the slice
        fontSize=16,
        fontWeight='bold',
        fill='white',
        align='center',
        baseline='middle'
    ).encode(
        theta=alt.Theta('percentage_of_total:Q', stack=True),
        text=alt.Text('percentage_of_total:Q', format='.1f'),
        order=alt.Order('percentage_of_total:Q', sort='descending')
    )
    
    # Add "%" sign to the percentage labels
    percentage_with_sign = alt.Chart(top_10_vs_rest_df).mark_text(
        radius=55,  # Slightly inside from the number
        fontSize=12,
        fill='white',
        align='center',
        baseline='middle'
    ).encode(
        theta=alt.Theta('percentage_of_total:Q', stack=True),
    )
    
    # Combine all layers
    pie_chart = pie + text_labels + percentage_labels + percentage_with_sign
    
    pie_chart.save('Frontend/chart/pie_chart/top_10_vs_rest.png')
    return pie_chart
    
total_waste_top_10_vs_rest_facilities_pie_chart()
#def top_10_vs_rest_waste_release_facilities_by_pie_chart()
#total_waste_by_counties_throughout_or_After_2020(choice = 'After')
#total_waste_througout_from_top_10_facility_chart_generator()
#total_waste_througout_from_top_10_facility_chart_generator_interactive()
#total_waste_by_counties_throughout_or_After_2020(choices='')
#total_waste_by_state_throughout_or_After_2020()
end_time = time.time()
print(f"Runtime {end_time - start_time} Seconds.")
