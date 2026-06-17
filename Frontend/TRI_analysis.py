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
import tabulate
import matplotlib
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
    

def total_waste_by_industries_interactive_treemap():
    import squarify
    import numpy as np
    import pandas as pd
    
    df = pd.read_sql(queries["Total_Waste_By_Industry"], con=engine)
    
    # Create subsector treemap
    industry_subsector_df = df.groupby(['industry_name', 'national_industry']).agg({
        'total_release': 'sum'
    }).reset_index()
    
    # Filter out zero or negative values
    industry_subsector_df = industry_subsector_df[industry_subsector_df['total_release'] > 0]
    
    if len(industry_subsector_df) == 0:
        print("No data to display")
        return None
    
    industry_subsector_df = industry_subsector_df.sort_values('total_release', ascending=False)
    
    # Handle very small values
    min_value = industry_subsector_df['total_release'].max() * 0.0001
    industry_subsector_df['total_release'] = industry_subsector_df['total_release'].clip(lower=min_value)
    
    # Generate coordinates
    values = industry_subsector_df['total_release'].values
    
    try:
        sizes = squarify.normalize_sizes(values, 100, 100)
        rects = squarify.squarify(sizes, 0, 0, 100, 100)
    except Exception as e:
        print(f"Error in squarify: {e}")
        # Fallback grid layout
        n = len(values)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        rects = []
        for i in range(n):
            row = i // cols
            col = i % cols
            rects.append({
                'x': col * (100/cols),
                'y': row * (100/rows),
                'dx': 100/cols,
                'dy': 100/rows
            })
    
    # Create dataframe and EXPLICITLY calculate x2 and y2
    treemap_df = pd.DataFrame(rects, columns=['x', 'y', 'dx', 'dy'])
    treemap_df['industry_name'] = industry_subsector_df['industry_name'].values
    treemap_df['national_industry'] = industry_subsector_df['national_industry'].values
    treemap_df['total_release'] = values
    treemap_df['percentage'] = (values / values.sum() * 100).round(2)
    
    # CRITICAL: Calculate x2 and y2 as actual columns
    treemap_df['x2'] = treemap_df['x'] + treemap_df['dx']
    treemap_df['y2'] = treemap_df['y'] + treemap_df['dy']
    
    # Calculate center points for text
    treemap_df['x_center'] = treemap_df['x'] + treemap_df['dx'] / 2
    treemap_df['y_center'] = treemap_df['y'] + treemap_df['dy'] / 2
    
    # Debug: Print first few rows to verify coordinates
    print("Treemap coordinates sample:")
    print(treemap_df[['x', 'y', 'dx', 'dy', 'x2', 'y2', 'industry_name']].head())
    
    # Create chart with EXPLICIT column references
    treemap = alt.Chart(treemap_df).mark_rect(
        stroke='white',
        strokeWidth=1
    ).encode(
        x=alt.X('x:Q', 
                axis=None, 
                scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('y:Q', 
                axis=None, 
                scale=alt.Scale(domain=[0, 100])),
        x2=alt.X2('x2:Q'),  # Use explicit column name
        y2=alt.Y2('y2:Q'),  # Use explicit column name
        color=alt.Color('national_industry:N',
                       scale=alt.Scale(scheme='tableau20'),
                       legend=alt.Legend(title='National Industry', orient='bottom')),
        tooltip=[
            alt.Tooltip('national_industry:N', title='National Industry'),
            alt.Tooltip('industry_name:N', title='Subsector'),
            alt.Tooltip('total_release:Q', title='Total Waste', format=',.0f'),
            alt.Tooltip('percentage:Q', title='% of Total', format='.1f')
        ]
    )
    
    # Labels for larger sections only
    labels = alt.Chart(treemap_df).mark_text(
        align='center',
        baseline='middle',
        fontSize=8,
        fontWeight='bold',
        limit=80
    ).encode(
        x='x_center:Q',
        y='y_center:Q',
        text='industry_name:N',
        color=alt.condition(
            alt.datum.total_release > treemap_df['total_release'].median(),
            alt.value('white'),
            alt.value('black')
        )
    ).transform_filter(
        (alt.datum.dx > 8) & (alt.datum.dy > 8)
    )
    
    # Interactivity
    highlight = alt.selection_point(
        fields=['national_industry'],
        name='highlight_industry',
        empty='none'
    )
    
    final_chart = (treemap + labels).add_params(
        highlight
    ).encode(
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.5)),
        strokeWidth=alt.condition(highlight, alt.value(3), alt.value(1))
    ).properties(
        title={
            "text": "Total Waste by Industry Subsector",
            "subtitle": f"Click legend to highlight • Hover for details • Total: {values.sum():,.0f}",
            "fontSize": 16
        },
        width=900,
        height=700
    ).configure_view(
        strokeWidth=0
    )
    
    import os
    os.makedirs('Frontend/chart/tree_map', exist_ok=True)
    
    final_chart.save('Frontend/chart/tree_map/industries_tree_map.html')
    
    return final_chart

def total_waste_hierarchical_treemap():
    import squarify
    import numpy as np
    import pandas as pd
    
    df = pd.read_sql(queries["Total_Waste_By_Industry"], con=engine)
    
    # Aggregate at subsector level first (outer rectangles)
    subsector_df = df.groupby('industry_name').agg({
        'total_release': 'sum'
    }).reset_index()
    
    subsector_df = subsector_df[subsector_df['total_release'] > 0]
    subsector_df = subsector_df.sort_values('total_release', ascending=False)
    
    # Keep top 10 subsectors, group rest into "Other"
    top_10_subsectors = subsector_df.head(10)
    other_subsectors = subsector_df.iloc[10:]
    
    if len(other_subsectors) > 0:
        other_total = other_subsectors['total_release'].sum()
        other_row = pd.DataFrame([{'industry_name': 'Other Subsectors', 'total_release': other_total}])
        subsector_df = pd.concat([top_10_subsectors, other_row], ignore_index=True)
    else:
        subsector_df = top_10_subsectors
    
    # Handle very small values
    min_value = subsector_df['total_release'].max() * 0.0001
    subsector_df['total_release'] = subsector_df['total_release'].clip(lower=min_value)
    
    # For national industries within "Other" subsector, group them too
    top_10_names = top_10_subsectors['industry_name'].tolist()
    df_filtered = df[df['industry_name'].isin(top_10_names)].copy()
    
    # Generate outer treemap layout for subsectors
    subsector_values = subsector_df['total_release'].values
    
    try:
        sizes = squarify.normalize_sizes(subsector_values, 100, 100)
        outer_rects = squarify.squarify(sizes, 0, 0, 100, 100)
    except Exception as e:
        print(f"Error in outer squarify: {e}")
        n = len(subsector_values)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        outer_rects = []
        for i in range(n):
            row = i // cols
            col = i % cols
            outer_rects.append({
                'x': col * (100/cols),
                'y': row * (100/rows),
                'dx': 100/cols,
                'dy': 100/rows
            })
    
    # Generate inner treemaps for national industries within each subsector
    all_rects = []
    
    for idx, (_, subsector_row) in enumerate(subsector_df.iterrows()):
        subsector_name = subsector_row['industry_name']
        outer_rect = outer_rects[idx]
        
        if subsector_name == 'Other Subsectors':
            # For "Other", just show one aggregated rectangle
            all_rects.append({
                'x': outer_rect['x'] + 1.5,
                'y': outer_rect['y'] + 1.5,
                'dx': max(outer_rect['dx'] - 3, 1),
                'dy': max(outer_rect['dy'] - 3, 1),
                'subsector_name': 'Other Subsectors',
                'national_industry': 'Other',
                'total_release': subsector_row['total_release'],
                'level': 'national_industry'
            })
            continue
        
        # Get national industries within this subsector (top 10 only)
        national_df = df_filtered[df_filtered['industry_name'] == subsector_name].groupby('national_industry').agg({
            'total_release': 'sum'
        }).reset_index()
        
        national_df = national_df[national_df['total_release'] > 0]
        national_df = national_df.sort_values('total_release', ascending=False)
        
        # Keep top 10 national industries per subsector, group rest
        top_10_national = national_df.head(10)
        other_national = national_df.iloc[10:]
        
        if len(other_national) > 0:
            other_total = other_national['total_release'].sum()
            other_row = pd.DataFrame([{'national_industry': 'Other', 'total_release': other_total}])
            national_df = pd.concat([top_10_national, other_row], ignore_index=True)
        else:
            national_df = top_10_national
        
        national_values = national_df['total_release'].values
        
        # Calculate inner rectangle area with padding
        padding = 1.5
        inner_x = outer_rect['x'] + padding
        inner_y = outer_rect['y'] + padding
        inner_w = max(outer_rect['dx'] - 2 * padding, 1)
        inner_h = max(outer_rect['dy'] - 2 * padding, 1)
        
        try:
            inner_sizes = squarify.normalize_sizes(national_values, inner_w, inner_h)
            inner_rects = squarify.squarify(inner_sizes, inner_x, inner_y, inner_w, inner_h)
        except Exception as e:
            n = len(national_values)
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))
            inner_rects = []
            for i in range(n):
                row = i // cols
                col = i % cols
                inner_rects.append({
                    'x': inner_x + col * (inner_w/cols),
                    'y': inner_y + row * (inner_h/rows),
                    'dx': inner_w/cols,
                    'dy': inner_h/rows
                })
        
        # Add national industry rectangles
        for j, (_, national_row) in enumerate(national_df.iterrows()):
            inner_rect = inner_rects[j]
            all_rects.append({
                'x': inner_rect['x'],
                'y': inner_rect['y'],
                'dx': inner_rect['dx'],
                'dy': inner_rect['dy'],
                'subsector_name': subsector_name,
                'national_industry': national_row['national_industry'],
                'total_release': national_row['total_release'],
                'level': 'national_industry'
            })
    
    # Add outer rectangles for subsector backgrounds
    for idx, (_, subsector_row) in enumerate(subsector_df.iterrows()):
        outer_rect = outer_rects[idx]
        all_rects.append({
            'x': outer_rect['x'],
            'y': outer_rect['y'],
            'dx': outer_rect['dx'],
            'dy': outer_rect['dy'],
            'subsector_name': subsector_row['industry_name'],
            'national_industry': subsector_row['industry_name'],
            'total_release': subsector_row['total_release'],
            'level': 'subsector'
        })
    
    # Create final dataframe
    treemap_df = pd.DataFrame(all_rects)
    treemap_df['x2'] = treemap_df['x'] + treemap_df['dx']
    treemap_df['y2'] = treemap_df['y'] + treemap_df['dy']
    treemap_df['x_center'] = treemap_df['x'] + treemap_df['dx'] / 2
    treemap_df['y_center'] = treemap_df['y'] + treemap_df['dy'] / 2
    treemap_df['area'] = treemap_df['dx'] * treemap_df['dy']
    
    total_all = treemap_df[treemap_df['level'] == 'national_industry']['total_release'].sum()
    treemap_df['percentage'] = (treemap_df['total_release'] / total_all * 100).round(2)
    
    national_df = treemap_df[treemap_df['level'] == 'national_industry'].copy()
    
    # Create background layer for subsectors
    subsector_layer = alt.Chart(treemap_df[treemap_df['level'] == 'subsector']).mark_rect(
        stroke='black',
        strokeWidth=3,
        opacity=0.15
    ).encode(
        x=alt.X('x:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('y:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        x2=alt.X2('x2:Q'),
        y2=alt.Y2('y2:Q'),
        color=alt.value('lightgray'),
        tooltip=[
            alt.Tooltip('subsector_name:N', title='Industry/Subsector'),
            alt.Tooltip('total_release:Q', title='Total Waste', format=',.0f'),
            alt.Tooltip('percentage:Q', title='% of Total', format='.1f')
        ]
    )
    
    # Create foreground layer for national industries
    national_layer = alt.Chart(national_df).mark_rect(
        stroke='white',
        strokeWidth=0.5
    ).encode(
        x=alt.X('x:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('y:Q', axis=None, scale=alt.Scale(domain=[0, 100])),
        x2=alt.X2('x2:Q'),
        y2=alt.Y2('y2:Q'),
        color=alt.Color('subsector_name:N',
                       scale=alt.Scale(scheme='tableau20'),
                       legend=None),
        tooltip=[
            alt.Tooltip('subsector_name:N', title='Industry/Subsector'),
            alt.Tooltip('national_industry:N', title='National Industry (NAICS)'),
            alt.Tooltip('total_release:Q', title='Total Waste', format=',.0f'),
            alt.Tooltip('percentage:Q', title='% of Total', format='.1f')
        ]
    )
    
    # Labels for national industries only
    national_labels = alt.Chart(national_df).mark_text(
        align='center',
        baseline='middle',
        fontSize=8,
        limit=60,
        lineHeight=12
    ).encode(
        x='x_center:Q',
        y='y_center:Q',
        text='national_industry:N',
        color=alt.condition(
            alt.datum.total_release > national_df['total_release'].median(),
            alt.value('white'),
            alt.value('black')
        )
    ).transform_filter(
        (alt.datum.dx > 6) & (alt.datum.dy > 4)
    )
    
    # Add interactivity
    highlight = alt.selection_point(
        fields=['subsector_name'],
        name='highlight_subsector',
        empty='none'
    )
    
    # Combine all layers
    final_chart = (subsector_layer + national_layer + national_labels).add_params(
        highlight
    ).encode(
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.7))
    ).properties(
        title={
            "text": "Hierarchical Treemap: Top 10 National Industries within Top 10 Subsectors",
            "subtitle": f"Hover over rectangles for Industry/Subsector details • Total Waste: {total_all:,.0f}",
            "fontSize": 16
        },
        width=1000,
        height=800
    ).configure_view(
        strokeWidth=0
    )
    
    import os
    os.makedirs('Frontend/chart/tree_map', exist_ok=True)
    
    final_chart.save('Frontend/chart/tree_map/hierarchical_industries_tree_map.html')
    
    return final_chart

def most_used_chemical():
    most_used_chemical_df = pd.read_sql(queries['Most_Dumped_Chemical'], con = engine)
    bar_chart = alt.Chart(most_used_chemical_df).mark_bar().encode(
        x = 'chem_name',
        y = 'reported_chem_count'
    )
    bar_chart.save('Frontend/chart/specific_query_results/most_used_chemical.png')
    
most_used_chemical()
#total_waste_top_10_vs_rest_facilities_pie_chart()
#total_waste_by_industries_interactive_treemap()
#total_waste_hierarchical_treemap()
#def top_10_vs_rest_waste_release_facilities_by_pie_chart()
#total_waste_by_counties_throughout_or_After_2020(choice = 'After')
#total_waste_througout_from_top_10_facility_chart_generator()
#total_waste_througout_from_top_10_facility_chart_generator_interactive()
#total_waste_by_counties_throughout_or_After_2020(choices='')
#total_waste_by_state_throughout_or_After_2020()
end_time = time.time()
print(f"Runtime {end_time - start_time} Seconds.")
