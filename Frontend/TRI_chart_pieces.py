import altair as alt
from vega_datasets import data
import TRI_data_processing as tdp
import pandas as pd


def create_chemical_pie_chart_from_state_df(state_df, selection, top_n=8):
    """
    Create a pie chart showing top chemicals for selected state
    This requires pre-computing top chemicals per state
    """
    # This is a placeholder - you'll need to compute top chemicals per state
    # One approach: create a separate function that pre-computes this
    
    # For now, create a placeholder chart
    placeholder_data = pd.DataFrame({
        'chemical': ['Click a state', 'to see', 'top chemicals'],
        'amount': [1, 1, 1]
    })
    
    pie_chart = alt.Chart(placeholder_data).mark_arc().encode(
        theta='amount:Q',
        color='chemical:N',
        tooltip=['chemical:N', 'amount:Q']
    ).properties(
        width=400,
        height=300,
        title='Top Chemicals in Selected State'
    )
    
    return pie_chart


def create_chemical_pie_chart_from_chemical_df(chemical_df, selection, top_n=8):
    """
    Create a pie chart showing top chemicals for selected state using pre-computed data
    
    This function requires that chemical_df has state-level chemical aggregations
    """
    # Filter based on selection - this is tricky in Altair
    # Alternative: Pre-compute for all states and filter in the chart
    
    pie_chart = alt.Chart(chemical_df).mark_arc().encode(
        theta='total_release:Q',
        color=alt.Color('chem_name:N', 
                       scale=alt.Scale(scheme='tableau20'),
                       legend=alt.Legend(title='Chemical', orient='right')),
        tooltip=['chem_name:N', 'total_release:Q']
    ).transform_filter(
        selection
    ).transform_window(
        rank='rank(total_release)',
        sort=[alt.SortField('total_release', order='descending')]
    ).transform_filter(
        alt.datum.rank <= top_n
    ).properties(
        width=400,
        height=300,
        title=f'Top {top_n} Chemicals in Selected State'
    )
    
    return pie_chart


def create_enhanced_interactive_dashboard(df, state_df, top_n_chemicals=8):
    """
    Create the complete enhanced dashboard with chemical pie chart
    """
    # Pre-compute top chemicals per state
    top_chemicals_df = tdp.prepare_top_chemicals_per_state(df, state_df, top_n_chemicals)
    
    # Create selection
    selection = alt.selection_point(fields=['state_fips'], empty='all')
    
    # Prepare waste type data
    waste_data = []
    for _, row in state_df.iterrows():
        waste_data.append({'state': row['state_name'], 'state_fips': row['state_fips'], 
                          'type': 'Air', 'amount': row['total_air_release']})
        waste_data.append({'state': row['state_name'], 'state_fips': row['state_fips'], 
                          'type': 'Water', 'amount': row['total_water_release']})
        waste_data.append({'state': row['state_name'], 'state_fips': row['state_fips'], 
                          'type': 'Land', 'amount': row['total_land_release']})
    
    waste_df = pd.DataFrame(waste_data)
    us_states = alt.topo_feature(data.us_10m.url, feature='states')
    
    # Base choropleth map
    base_map = alt.Chart(us_states).mark_geoshape(
        stroke='black',
        strokeWidth=0.5
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(state_df, key='state_fips', 
                           fields=['total_release', 'state_name', 'state_fips'])
    ).encode(
        color=alt.Color('total_release:Q',
                       scale=alt.Scale(scheme='reds', type='symlog', constant=1),
                       title="Total Waste Release (lbs)",
                       legend=alt.Legend(format='.0f')),
        tooltip=[
            alt.Tooltip('state_name:N', title="State:"),
            alt.Tooltip('total_release:Q', title='Total Waste:', format=',.0f')
        ],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.4))
    ).add_params(
        selection
    ).properties(
        width=900,
        height=500,
        title={
            "text": "US Toxic Waste Release Interactive Dashboard",
            "subtitle": "Click on any state to see waste breakdown and top chemicals",
            "fontSize": 16,
            "anchor": "middle"
        }
    ).project('albersUsa')
    
    # Stacked bar chart for waste type
    stacked_chart = alt.Chart(waste_df).mark_bar().encode(
        x=alt.X('type:N', title='Waste Type'),
        y=alt.Y('amount:Q', title='Release Amount (lbs)', axis=alt.Axis(format='.0f')),
        color=alt.Color('type:N', scale=alt.Scale(scheme='category10'), title='Waste Type', legend=None),
        tooltip=['state:N', 'type:N', 'amount:Q']
    ).transform_filter(
        selection
    ).properties(
        width=300,
        height=350,
        title='Waste Type Breakdown'
    )
    
    # Top states bar chart
    top_states = state_df.nlargest(15, 'total_release').copy()
    
    bar_chart = alt.Chart(top_states).mark_bar(
        cornerRadiusTopRight=5,
        cornerRadiusBottomRight=5
    ).encode(
        x=alt.X('total_release:Q', title='Total Waste Release (lbs)', axis=alt.Axis(format='.0f')),
        y=alt.Y('state_name:N', sort='-x', title='State'),
        color=alt.condition(selection, alt.Color('total_release:Q', scale=alt.Scale(scheme='reds')), alt.value('lightgray')),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.5)),
        tooltip=['state_name:N', alt.Tooltip('total_release:Q', format=',.0f')]
    ).add_params(
        selection
    ).properties(
        width=350,
        height=350,
        title='Top 15 States (Click to select)'
    )
    
    # Dynamic state title for pie chart
    pie_title = alt.Chart(state_df).mark_text(
        align='center',
        fontSize=14,
        fontWeight='bold'
    ).encode(
        text=alt.condition(selection, alt.Text('state_name:N'), alt.value('Select a State'))
    ).transform_filter(
        selection
    ).properties(
        width=350,
        height=30
    )
    
    # Pie chart for top chemicals
    if len(top_chemicals_df) > 0:
        pie_chart = alt.Chart(top_chemicals_df).mark_arc(
            innerRadius=50,
            stroke='white'
        ).encode(
            theta=alt.Theta('total_release:Q', stack=True),
            color=alt.Color('chem_name:N', 
                           scale=alt.Scale(scheme='tableau20'),
                           legend=alt.Legend(title='Chemical', orient='right', columns=1)),
            tooltip=['chem_name:N', alt.Tooltip('total_release:Q', format=',.0f')]
        ).transform_filter(
            selection
        ).properties(
            width=350,
            height=320,
            title=f'Top {top_n_chemicals} Chemicals'
        )
    else:
        placeholder_data = pd.DataFrame({
            'chem_name': ['No Data Available'],
            'total_release': [1]
        })
        pie_chart = alt.Chart(placeholder_data).mark_arc().encode(
            theta='total_release:Q',
            color=alt.Color('chem_name:N', title='Chemical'),
            tooltip=['chem_name:N']
        ).properties(
            width=350,
            height=320,
            title='No Chemical Data Available'
        )
    
    # Combine bar chart and pie chart horizontally
    middle_row = alt.hconcat(bar_chart, alt.vconcat(pie_title, pie_chart))
    
    # Combine stacked chart with the bar+pie combo
    bottom_row = alt.hconcat(stacked_chart, middle_row)
    
    # Final dashboard
    dashboard = alt.vconcat(
        base_map,
        bottom_row
    ).configure_view(
        stroke=None
    ).configure_legend(
        titleFontSize=11,
        labelFontSize=10,
        orient='right'
    )
    
    return dashboard


# Main execution
def final_state_map_output(choices = 'After'):
    # Fetch and process data
    df = tdp.fetch_waste_data(choice=choices)
    state_df = tdp.aggregate_by_state(df)
    
    # Debug: Check if states match
    print("States in raw data:", sorted(df['state'].unique()))
    print("States in aggregated data:", sorted(state_df['state'].unique()))
    
    # Create enhanced dashboard with chemical pie chart
    enhanced_dashboard = create_enhanced_interactive_dashboard(df, state_df, top_n_chemicals=8)
    enhanced_dashboard.show()
    
    # Save
    if choices == 'After':
        enhanced_dashboard.save('Frontend/chart/state_map/TRI_State_Map_Dashboard_2020s.html')
        enhanced_dashboard.save('Frontend/chart/state_map/TRI_State_Map_Dashboard_2020s.png')

    else:
        enhanced_dashboard.save('Frontend/chart/state_map/TRI_State_Map_Dashboard_Throughout.html')
        enhanced_dashboard.save('Frontend/chart/state_map/TRI_State_Map_Dashboard_Throughout.png')



#--------------------------------------COUNTY--------------------------------------------
import altair as alt
from vega_datasets import data
import pandas as pd
import TRI_data_processing as tdp
import json
import requests

def create_county_dashboard(df, county_df, top_n_counties=15, top_n_chemicals=8):
    """
    Create an interactive county-level dashboard for the entire US showing ALL counties
    with connected map, charts, and pie chart
    """
    
    # Pre-compute top chemicals per county
    top_chemicals_df = tdp.prepare_top_chemicals_per_county(df, county_df, top_n_chemicals)
    
    print(f"Counties with waste data: {len(county_df)}")
    print(f"States with data: {sorted(county_df['state'].unique())}")
    
    # Load the TopoJSON data and extract all county IDs
    topo_url = data.us_10m.url
    topo_response = requests.get(topo_url)
    topo_data = topo_response.json()
    
    # Get all county geometries and their IDs
    county_geoms = topo_data['objects']['counties']['geometries']
    all_county_ids = [g['id'] for g in county_geoms]
    
    print(f"Total counties in TopoJSON: {len(all_county_ids)}")
    
    # Create a complete dataframe with ALL counties
    all_counties_list = []
    for county_id in all_county_ids:
        # Check if this county has data
        county_data = county_df[county_df['county_fips'] == county_id]
        
        if len(county_data) > 0:
            row = county_data.iloc[0]
            all_counties_list.append({
                'id': county_id,
                'total_release': float(row['total_release']),
                'total_land_release': float(row['total_land_release']),
                'total_water_release': float(row['total_water_release']),
                'total_air_release': float(row['total_air_release']),
                'county': row['county'],
                'state': row['state'],
                'has_data': True
            })
        else:
            all_counties_list.append({
                'id': county_id,
                'total_release': 0,
                'total_land_release': 0,
                'total_water_release': 0,
                'total_air_release': 0,
                'county': f'County {county_id}',
                'state': 'No Data',
                'has_data': False
            })
    
    all_counties_df = pd.DataFrame(all_counties_list)
    
    # Create a SINGLE selection that all components will share
    county_selection = alt.selection_point(
        fields=['id'],
        empty='all',
        on='click',
        clear='dblclick',
        name='county_select'
    )
    
    # Prepare waste type data
    waste_data = []
    for _, row in county_df.iterrows():
        waste_data.append({'county_name': f"{row['county']}, {row['state']}", 
                          'id': row['county_fips'],
                          'type': 'Air', 'amount': row['total_air_release']})
        waste_data.append({'county_name': f"{row['county']}, {row['state']}", 
                          'id': row['county_fips'], 
                          'type': 'Water', 'amount': row['total_water_release']})
        waste_data.append({'county_name': f"{row['county']}, {row['state']}", 
                          'id': row['county_fips'], 
                          'type': 'Land', 'amount': row['total_land_release']})
    
    waste_df = pd.DataFrame(waste_data)
    
    # Load US counties TopoJSON
    counties_topo = alt.topo_feature(topo_url, 'counties')
    
    # County choropleth map
    county_map = alt.Chart(counties_topo).mark_geoshape(
        stroke='white',
        strokeWidth=0.5
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(
            all_counties_df, 
            key='id',
            fields=['total_release', 'county', 'state', 'has_data', 'total_land_release', 
                   'total_water_release', 'total_air_release']
        )
    ).encode(
        color=alt.condition(
            alt.datum.has_data == True,
            alt.Color('total_release:Q',
                     scale=alt.Scale(
                         scheme='blues', 
                         type='symlog', 
                         constant=1
                     ),
                     title="Total Waste Release (lbs)",
                     legend=alt.Legend(format='.0f')),
            alt.value('#f0f0f0')
        ),
        tooltip=[
            alt.Tooltip('county:N', title="County:"),
            alt.Tooltip('state:N', title="State:"),
            alt.Tooltip('total_release:Q', title='Total Waste:', format=',.0f'),
            alt.Tooltip('has_data:N', title="Has Data:")
        ],
        strokeWidth=alt.condition(county_selection, alt.value(3), alt.value(0.5)),
        stroke=alt.condition(county_selection, alt.value('red'), alt.value('white')),
        opacity=alt.condition(county_selection, alt.value(1), alt.value(1))
    ).add_params(
        county_selection
    ).properties(
        width=1100,
        height=650,
        title={
            "text": "US County Toxic Waste Release - All 50 States",
            "subtitle": "Gray counties have no reported waste | Click any blue county or bar for details | Double-click to clear",
            "fontSize": 16,
            "anchor": "middle"
        }
    ).project(
        type='albersUsa'
    )
    
    # Stacked bar chart for waste type
    stacked_chart = alt.Chart(waste_df).mark_bar().encode(
        x=alt.X('type:N', title='Waste Type'),
        y=alt.Y('amount:Q', title='Release Amount (lbs)', axis=alt.Axis(format='.0f')),
        color=alt.Color('type:N', scale=alt.Scale(scheme='category10'), title='Waste Type', legend=None),
        tooltip=['county_name:N', 'type:N', alt.Tooltip('amount:Q', format=',.0f')]
    ).transform_filter(
        county_selection
    ).properties(
        width=400,
        height=350,
        title='Waste Type Breakdown for Selected County'
    )
    
    # Top counties bar chart
    top_counties = county_df.nlargest(top_n_counties, 'total_release').copy()
    top_counties['county_label'] = top_counties['county'] + ', ' + top_counties['state']
    top_counties['id'] = top_counties['county_fips']
    
    bar_chart = alt.Chart(top_counties).mark_bar(
        cornerRadiusTopRight=5,
        cornerRadiusBottomRight=5
    ).encode(
        x=alt.X('total_release:Q', title='Total Waste Release (lbs)', axis=alt.Axis(format='.0f')),
        y=alt.Y('county_label:N', sort='-x', title='County'),
        color=alt.condition(county_selection, alt.value('steelblue'), alt.value('lightgray')),
        opacity=alt.condition(county_selection, alt.value(1), alt.value(0.7)),
        tooltip=[
            alt.Tooltip('county:N', title='County'),
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Waste:', format=',.0f')
        ]
    ).add_params(
        county_selection
    ).properties(
        width=450,
        height=450,
        title=f'Top {top_n_counties} Counties by Waste (Click to select)'
    )
    
    # Dynamic title for pie chart
    selected_county_text = alt.Chart(all_counties_df).mark_text(
        align='center',
        fontSize=14,
        fontWeight='bold'
    ).encode(
        text=alt.condition(county_selection, alt.Text('county:N'), alt.value('Select a County'))
    ).transform_filter(
        county_selection
    ).properties(
        width=450,  # Match the width of the pie chart
        height=30
    )
    
    # Pie chart for top chemicals
    if len(top_chemicals_df) > 0:
        top_chemicals_for_pie = top_chemicals_df.copy()
        top_chemicals_for_pie['id'] = top_chemicals_for_pie['county_fips']
        
        pie_chart = alt.Chart(top_chemicals_for_pie).mark_arc(
            innerRadius=50,
            stroke='white'
        ).encode(
            theta=alt.Theta('total_release:Q', stack=True),
            color=alt.Color('chem_name:N', 
                           scale=alt.Scale(scheme='tableau20'),
                           legend=alt.Legend(title='Chemical', orient='right', columns=1)),
            tooltip=['chem_name:N', alt.Tooltip('total_release:Q', format=',.0f')]
        ).transform_filter(
            county_selection
        ).properties(
            width=450,
            height=370,  # Reduced height to fit better
            title=f'Top {top_n_chemicals} Chemicals'
        )
    else:
        placeholder_data = pd.DataFrame({
            'chem_name': ['No Data Available'],
            'total_release': [1],
            'id': [0]
        })
        pie_chart = alt.Chart(placeholder_data).mark_arc().encode(
            theta='total_release:Q',
            color=alt.Color('chem_name:N', title='Chemical'),
            tooltip=['chem_name:N']
        ).properties(
            width=450,
            height=370,
            title='No Chemical Data Available'
        )
    
    # NEW LAYOUT: Horizontal arrangement similar to state dashboard
    # Bar chart on the left, Title + Pie chart on the right
    middle_row = alt.hconcat(
        bar_chart, 
        alt.vconcat(selected_county_text, pie_chart)
    )
    
    # Combine stacked chart with the middle row
    bottom_row = alt.hconcat(stacked_chart, middle_row)
    
    # Final dashboard
    dashboard = alt.vconcat(
        county_map,
        bottom_row
    ).configure_view(
        stroke=None
    ).configure_legend(
        titleFontSize=11,
        labelFontSize=10,
        orient='right'
    )
    
    return dashboard

def debug_county_ids():
    """
    Debug function to check the TopoJSON county IDs
    """
    import requests
    import json
    
    # Load the TopoJSON data
    url = data.us_10m.url
    response = requests.get(url)
    topojson_data = response.json()
    
    # Extract county geometries
    counties = topojson_data['objects']['counties']['geometries']
    
    # Get a sample of county IDs
    print("Sample of TopoJSON county IDs:")
    for county in counties[:10]:
        print(f"  ID: {county['id']}")
    
    print(f"\nTotal counties in TopoJSON: {len(counties)}")
    print(f"ID type: {type(counties[0]['id'])}")
    
    # Check if IDs are strings or integers
    id_types = set(type(c['id']) for c in counties)
    print(f"ID types found: {id_types}")
    
    # Check if our data FIPS codes match
    print("\nChecking ID format compatibility...")
    print(f"First TopoJSON ID: {counties[0]['id']} (type: {type(counties[0]['id'])})")


# Main execution
def final_county_map_output(choices = ''):
    print("Fetching data...")
    df = tdp.fetch_waste_data(choice=choices)
    county_df = tdp.aggregate_by_county(df)
    
    print(f"Counties with waste data: {len(county_df)}")
    print(f"States with data: {sorted(county_df['state'].unique())}")
    
    # Debug: Check county FIPS format
    print(f"\nSample county FIPS codes:")
    print(county_df['county_fips'].head())
    print(f"FIPS code type: {type(county_df['county_fips'].iloc[0])}")
    print(f"Sample FIPS values: {county_df['county_fips'].head().tolist()}")
    
    # Run debug to check TopoJSON IDs
    print("\nDebugging TopoJSON county IDs:")
    debug_county_ids()
    
    # Check if FIPS codes match TopoJSON ID format
    import requests
    import json
    topo_url = data.us_10m.url
    topo_response = requests.get(topo_url)
    topo_data = topo_response.json()
    topo_ids = set(g['id'] for g in topo_data['objects']['counties']['geometries'])
    
    data_fips = set(county_df['county_fips'].dropna().unique())
    
    # Check for matches
    matches = data_fips.intersection(topo_ids)
    print(f"\nFIPS matching check:")
    print(f"  TopoJSON IDs: {len(topo_ids)}")
    print(f"  Data FIPS codes: {len(data_fips)}")
    print(f"  Matches: {len(matches)}")
    
    if len(matches) == 0:
        print("\nNO MATCHES FOUND! This is why the map isn't working.")
        print(f"  Sample TopoJSON IDs: {list(topo_ids)[:5]}")
        print(f"  Sample Data FIPS: {list(data_fips)[:5]}")
        print("\n  The FIPS codes don't match. Check your add_county_fips_mapping function!")
    else:
        print(f"  Sample matches: {list(matches)[:5]}")
    
    # Create dashboard
    print("\nCreating county dashboard (showing ALL counties)...")
    dashboard = create_county_dashboard(df, county_df, top_n_counties=15, top_n_chemicals=8)
    
    if choices == 'After':    
        dashboard.save('Frontend/chart/county_map/TRI_County_Map_Dashboard_2020s.html')
        dashboard.save('Frontend/chart/county_map/TRI_County_Map_Dashboard_2020s.png')
    else:
        dashboard.save('Frontend/chart/county_map/TRI_County_Map_Dashboard_Throughout.html')
        dashboard.save('Frontend/chart/county_map/TRI_County_Map_Dashboard_Throughout.png')

    
    dashboard.show()