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
        x=alt.X('create_month:T', 
                axis=alt.Axis(format='%b %Y', labelAngle=-45, title='Date'),
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

    total_waste_throughout_top_10_chart.save('Frontend/total_waste_throughout_top_10.png')


def total_waste_by_location_throughout_or_After_2020(choice = ""):
    if choice == 'After':
        total_waste_df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine) 
    else:
        total_waste_df = pd.read_sql(queries["Waste_By_Location"], con=engine)

    
    print("Sample of data:")
    print(total_waste_df[['state', 'county']].head(10))
    print(f"\nTotal rows: {len(total_waste_df)}")
    
    print(total_waste_df.head(10))    
    states  = alt.topo_feature(data.us_10m.url, feature = 'states')
    state_waste = total_waste_df.groupby('state', as_index=False)['total_release'].sum()
    print('\nState Waste:', state_waste.head())
    # Use the us library to get state names and map IDs
    def get_state_info(abbrev):
        state = states.lookup(abbrev)
        if state:
            return pd.Series({
                'state_name': state.name,
                # The topo feature uses the FIPS code as the ID (but as string without leading zero for single digits)
                'id': int(state.fips)  # Convert FIPS to int to match topo feature format
            })
        return pd.Series({'state_name': abbrev, 'id': None})
    
    # Apply the mapping
    state_info = state_waste['state'].apply(get_state_info)
    print(f'\nState Info: {state_info}')
    state_waste = pd.concat([state_waste, state_info], axis=1)
    print(f'\nState Waste Updated: {state_waste}')

    # Check for unmapped states
    unmapped = state_waste[state_waste['id'].isna()]
    if len(unmapped) > 0:
        print(f"Warning: Could not map IDs for states: {unmapped['state'].tolist()}")
        # Remove unmapped states
        state_waste = state_waste.dropna(subset=['id'])
    
    # Convert id to integer for proper matching
    state_waste['id'] = state_waste['id'].astype(int)
    
    background = alt.Chart(states).mark_geoshape(
        fill = 'lightgray',
        stroke = 'white'
    ).project('albersUsa').properties(
        width = 700,
        height = 500
    )
    
    waste_map = alt.Chart(states).mark_geoshape(
        stroke = 'white'
    ).project(
        'albersUsa'
    ).encode(
        color = alt.Color('total_release:Q',
                          scale = alt.Scale(scheme = 'reds', type = 'log'),
                          title='Total Waste Released' if choice != 'After' else 'Total Waste Released 2020s'),
        tooltip=[
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Waste', format=',.0f')
        ]
    ).transform_lookup(
        lookup = 'id',
        from_=alt.LookupData(state_waste, 'id', ['total_release', 'state_name'])
    ).properties(
        width = 700,
        height=500,
        title = 'Waste Release By State' if choice != 'After' else "Waste Release By State 2020s"
    )
    
    chart = background + waste_map
    if choice == 'After':
        chart.save('Frontend/chart/total_waste_By_States_2020s.png')
    else:
        chart.save('Frontend/chart/total_waste_By_States.png')
    
    return chart

def total_waste_by_counties_throughout_or_After_2020(choice = ""):
    if choice == 'After':
        total_waste_df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine) 
    else:
        total_waste_df = pd.read_sql(queries["Waste_By_Location"], con=engine)

    total_waste_df = map_db_counties_to_fips_code(location_db=total_waste_df)
    counties = alt.topo_feature(data.us_10m.url, feature = 'counties')
    county_releases = total_waste_df.groupby('county_fips').agg({
        'total_release': 'sum',
        'county': 'first',
        'state_name': 'first'
    }).reset_index()
    print(county_releases.head())
    county_releases = county_releases.dropna(subset=['county_fips'])
    print(county_releases.head())
    click_select = alt.selection_point(fields=['county_fips'], name='select_county')
    choropleth = alt.Chart(counties).mark_geoshape().transform_lookup(
        lookup='id',  # FIPS code in the TopoJSON
        from_=alt.LookupData(
            county_releases,
            key='county_fips',  # Your FIPS column
            fields=['total_release', 'county', 'state_name']
        )
    ).encode(
        color=alt.Color(
            'total_release:Q',
            scale=alt.Scale(scheme='reds', type='symlog', constant=1),  # Log scale for better visualization
            title='Total Waste Release',
            legend=alt.Legend(format = '.0f', tickCount=5, titleLimit=500)
        ),
        tooltip=[
            alt.Tooltip('county:N', title='County'),
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Release', format=',.0f')
        ],
        stroke= alt.condition(
            click_select,
            alt.value('yellow'),
            alt.value('white')
        ),
        strokeWidth= alt.condition(
            click_select,
            alt.value(0.05),
            alt.value(0.05)
        )
    ).add_params(
        click_select
    ).project(
        type='albersUsa'
    ).properties(
        width=700,
        height=500,
        title='Total Waste Release by County'
    )
    
    background = alt.Chart(counties).mark_geoshape(
        fill = 'lightgray',
        stroke = 'white'
    ).project('albersUsa').properties(
        width = 700,
        height = 500
    )
    final_map = background + choropleth
    if choice == 'After':
        final_map.save('Frontend/chart/total_waste_by_counties_2020s.html')
    else:
        final_map.save('Frontend/chart/total_waste_by_counties.html')

    
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


#total_waste_by_location_throughout_or_After_2020(choice = 'After')
#total_waste_by_counties_throughout_or_After_2020()

total_waste_by_counties_throughout_or_After_2020()

end_time = time.time()
print(f"Runtime {end_time - start_time} Seconds.")
