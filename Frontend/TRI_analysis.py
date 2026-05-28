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
start_time = time.time()

alt.renderers.enable("mimetype")

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
with open('queries.json', 'r') as f:
    queries = json.load(f)

def total_waste_througout_from_top_10_facility_chart_generator():
    total_waste_throught_from_top_10_df = pd.read_sql(queries["Total_Waste_Throughout_top_10"], con=engine)

    print(total_waste_throught_from_top_10_df.columns.to_list())
    print(f"DataFrame shape: {total_waste_throught_from_top_10_df.shape}")
    print(f"DataFrame memory usage: {total_waste_throught_from_top_10_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Unique names: {total_waste_throught_from_top_10_df['name'].nunique()}")

    total_waste_throughout_top_10_chart = alt.Chart(total_waste_throught_from_top_10_df).mark_line(
        strokeWidth=2,
        point=False  # Remove points for cleaner lines
    ).encode(
        x=alt.X('reporting_year:T', 
                axis=alt.Axis(format='%Y', labelAngle=-45, title='Date'),
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
    
    if choice == 'After':
        state_waste_df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine) 
    else:
        state_waste_df = pd.read_sql(queries["Waste_By_Location"], con=engine)
    print(state_waste_df.columns.to_list())
    state_waste_df = state_waste_df.drop(columns = ['city', 'county'])
    state_waste_df = state_waste_df.drop_duplicates()

    state_waste_df = state_waste_df.groupby('state').agg(
        {
            'total_release': 'sum',
            'total_land_release':'sum',
            'total_water_release':'sum',
            'total_air_release':'sum'
        }
    ).reset_index()

    state_waste_df['state_fips'] = state_waste_df['state'].apply(lambda x:states.lookup(str(x)).fips if states.lookup(str(x)) else pd.NA)
    state_waste_df['state_name'] = state_waste_df['state_fips'].apply(lambda x:states.lookup(str(x)).name if states.lookup(str(x)) else pd.NA)

    state_waste_df = state_waste_df.dropna()
    
    # Ensure state_fips is properly formatted as string
    state_waste_df['state_fips'] = state_waste_df['state_fips'].astype(str).str.zfill(2)
    
    us_states = alt.topo_feature(data.us_10m.url, feature = 'states')
    
    print("State waste df sample:")
    print(state_waste_df.head(10))
    print(f"\nFIPS dtype: {state_waste_df['state_fips'].dtype}")
    print(f"FIPS values: {state_waste_df['state_fips'].tolist()[:10]}")

    # Check if total_release has the same value everywhere
    print(f"\nUnique total_release values: {state_waste_df['total_release'].nunique()}")
    print(f"Total sum: {state_waste_df['total_release'].sum()}")
    
    # Prepare bar data
    bar_data = state_waste_df.melt(
        id_vars = ['state', 'state_fips', 'state_name', 'total_release'],
        value_vars= ['total_land_release', 'total_water_release', 'total_air_release'],
        var_name = 'release_type',
        value_name= 'release_amount(lbs)'
    )
    
    bar_data['release_type'] = bar_data['release_type'].str.replace('total_','').str.replace('_release', '').str.title()
    
    point_hover = alt.selection_point(fields=['state_fips'], on='pointerover', empty=False)    

    background = alt.Chart(us_states).mark_geoshape(
        fill='lightgray',
        stroke = 'white'
    ).project('albersUsa').properties(
        width = 700,
        height = 500
    )
    
    choropleth = alt.Chart(us_states).mark_geoshape().transform_lookup(
        lookup = 'id',
        from_ = alt.LookupData(state_waste_df, key='state_fips', 
                              fields = ['total_release', 'state_name', 'state_fips'])
    ).properties(
        width = 700,
        height = 500
    ).project('albersUsa'
    ).add_params(
        point_hover
    ).encode(
        color = alt.Color('total_release:Q',
                 scale = alt.Scale(scheme = 'reds', type = 'symlog', constant = 1),
                 title = "Total Waste Release",
                 legend = alt.Legend(format = '.0f', tickCount=5, titleLimit=500)),
        tooltip= [
            alt.Tooltip('state_name:N', title = "State:"),
            alt.Tooltip('total_release:Q', title = 'Total Waste:', format=',.0f')
        ],
        stroke= alt.condition(
            point_hover,
            alt.value('yellow'),
            alt.value('white')
        ),
        strokeWidth= alt.condition(
            point_hover,
            alt.value(2),
            alt.value(0.5)
        )
    )
    

    bars = alt.Chart(bar_data).mark_bar().encode(
        y = alt.Y('release_type:N', 
                  title = None, 
                  sort = ['Air', 'Land', 'Water'],
                  axis=alt.Axis(labelFontSize=12)),
        x = alt.X('release_amount(lbs):Q', 
                  title = 'Release Amount (lbs)', 
                  axis = alt.Axis(format='.1e', labelFontSize=10)),
        color = alt.Color('release_type:N',
                          scale = alt.Scale(domain=['Air', 'Land', 'Water'],
                                            range=['#87CEEB', '#8B4513', '#4682B4']),
                          legend = None),
        tooltip= [
            alt.Tooltip('release_type:N', title ='Type: '),
            alt.Tooltip('release_amount(lbs):Q', title = 'Amount:', format = ',.0f')
        ]
    ).properties(
        width = 300,
        height = 200,
        title = 'Release Breakdown by Type'  
    ).transform_filter(
        point_hover
    )
    
    final_map = alt.hconcat(
        background + choropleth, 
        bars
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    )
    
    if choice == 'After':
        final_map.save('Frontend/chart/total_waste_by_state_2020s.png')
        final_map.save('Frontend/chart/total_waste_by_state_2020s.html')
    else:
        final_map.save('Frontend/chart/total_waste_by_state.png')
        final_map.save('Frontend/chart/total_waste_by_state.html')

def total_waste_by_counties_throughout_or_After_2020(choice = ""):
    if choice == 'After':
        total_waste_df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine) 
    else:
        total_waste_df = pd.read_sql(queries["Waste_By_Location"], con=engine)

    total_waste_df = map_db_counties_to_fips_code(location_db=total_waste_df)
    counties = alt.topo_feature(data.us_10m.url, feature = 'counties')
    
    # County-level aggregation with all release types
    county_releases = total_waste_df.groupby('county_fips').agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum',
        'county': 'first',
        'state_name': 'first'
    }).reset_index()
    
    county_releases = county_releases.dropna(subset=['county_fips'])
    
    # Ensure county_fips is properly formatted as string
    county_releases['county_fips'] = county_releases['county_fips'].astype(str).str.zfill(5)
    
    print(county_releases.head())
    
    # Prepare bar data for the breakdown chart
    bar_data = county_releases.melt(
        id_vars=['county_fips', 'county', 'state_name', 'total_release'],
        value_vars=['total_land_release', 'total_water_release', 'total_air_release'],
        var_name='release_type',
        value_name='release_amount(lbs)'
    )
    
    bar_data['release_type'] = bar_data['release_type'].str.replace('total_','').str.replace('_release', '').str.title()
    
    # Create selection for hover interaction
    point_hover = alt.selection_point(fields=['county_fips'], on='pointerover', empty=False)
    
    # Background map
    background = alt.Chart(counties).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).project('albersUsa').properties(
        width=700,
        height=500
    )
    
    # Choropleth map
    choropleth = alt.Chart(counties).mark_geoshape().transform_lookup(
        lookup='id',  # FIPS code in the TopoJSON
        from_=alt.LookupData(
            county_releases,
            key='county_fips',  # Your FIPS column
            fields=['total_release', 'county', 'state_name', 'county_fips', 
                   'total_land_release', 'total_water_release', 'total_air_release']
        )
    ).encode(
        color=alt.Color(
            'total_release:Q',
            scale=alt.Scale(scheme='reds', type='symlog', constant=1),  
            title='Total Waste Release',
            legend=alt.Legend(format='.0f', tickCount=5, titleLimit=500)
        ),
        tooltip=[
            alt.Tooltip('county:N', title='County'),
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Release', format=',.0f')
        ],
        stroke=alt.condition(
            point_hover,
            alt.value('yellow'),
            alt.value('white')
        ),
        strokeWidth=alt.condition(
            point_hover,
            alt.value(2),
            alt.value(0.5)
        )
    ).add_params(
        point_hover
    ).project(
        type='albersUsa'
    ).properties(
        width=700,
        height=500,
        title='Total Waste Release by County'
    )
    
    # Horizontal bar chart for release breakdown
    bars = alt.Chart(bar_data).mark_bar().encode(
        y=alt.Y('release_type:N', 
                title=None, 
                sort=['Air', 'Land', 'Water'],
                axis=alt.Axis(labelFontSize=12)),
        x=alt.X('release_amount(lbs):Q', 
                title='Release Amount (lbs)', 
                axis=alt.Axis(format='.1e', labelFontSize=10)),
        color=alt.Color('release_type:N',
                        scale=alt.Scale(domain=['Air', 'Land', 'Water'],
                                      range=['#87CEEB', '#8B4513', '#4682B4']),
                        legend=None),
        tooltip=[
            alt.Tooltip('release_type:N', title='Type: '),
            alt.Tooltip('release_amount(lbs):Q', title='Amount:', format=',.0f')
        ]
    ).properties(
        width=300,
        height=200,
        title='Release Breakdown by Type'
    ).transform_filter(
        point_hover
    )
    
    # Combine map and bar chart
    final_map = alt.hconcat(
        background + choropleth, 
        bars
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    )
    
    if choice == 'After':
        final_map.save('Frontend/chart/total_waste_by_counties_2020s.html')
        final_map.save('Frontend/chart/total_waste_by_counties_2020s.png')
    else:
        final_map.save('Frontend/chart/total_waste_by_counties.html')
        final_map.save('Frontend/chart/total_waste_by_counties.png')
    
def map_db_counties_to_fips_code(location_db):
    print("Starting function...")
    print(f"Loaded {len(location_db)} rows")
    
    def safe_state_lookup(abbr):
        result = states.lookup(abbr)
        return result.name if result is not None else pd.NA 
    
    location_db['state_name'] = location_db['state'].apply(safe_state_lookup)
    print("State names added")
    
    af = addfips.AddFIPS()
    
    # First, get unique county-state combinations to avoid redundant API calls
    unique_counties = location_db[['county', 'state']].drop_duplicates()
    print(f"Processing {len(unique_counties)} unique county-state combinations")
    
    # Create a lookup dictionary for unique combinations
    county_fips_map = {}
    for _, row in unique_counties.iterrows():
        try:
            county_fips_map[(row['county'], row['state'])] = af.get_county_fips(row['county'], state=row['state'])
        except Exception as e:
            print(f"Error looking up {row['county']}, {row['state']}: {e}")
            county_fips_map[(row['county'], row['state'])] = pd.NA
    
    print(f"Created FIPS map with {len(county_fips_map)} entries")

    # Map the FIPS codes back to the original DataFrame
    location_db['county_fips'] = location_db.apply(
        lambda row: county_fips_map.get((row['county'], row['state']), pd.NA), 
        axis=1
    )

    return location_db

def total_waste_througout_from_top_10_facility_chart_generator_interactive():
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
        x=alt.X('reporting_year:T', 
                axis=alt.Axis(format='%Y', labelAngle=-45, title='Date'),
                title=None),
        y=alt.Y('total_release:Q', 
                axis=alt.Axis(format=',.0f', title='Total Release (lbs)'),
                scale=alt.Scale(zero=False)),
        color=alt.Color('name:N', 
                        legend=alt.Legend(title='Facility (click to filter)', orient='bottom', columns=2),
                        sort='-y'),
        tooltip=[
            alt.Tooltip('name:N', title='Facility'),
            alt.Tooltip('reporting_year:T', title='Date', format='%Y'),
            alt.Tooltip('total_release:Q', title='Total Release', format=',.0f'),
        ],
        # Only use opacity change based on legend selection
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1))
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

#def top_10_vs_rest_waste_release_facilities_by_pie_chart()

total_waste_by_counties_throughout_or_After_2020(choice = 'After')

#total_waste_througout_from_top_10_facility_chart_generator()
#total_waste_througout_from_top_10_facility_chart_generator_interactive()
#total_waste_by_counties_throughout_or_After_2020()

#total_waste_by_state_throughout_or_After_2020()
end_time = time.time()
print(f"Runtime {end_time - start_time} Seconds.")
