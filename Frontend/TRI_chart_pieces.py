import altair as alt
from vega_datasets import data
import TRI_data_processing as tdp
import pandas as pd

def create_interactive_state_dashboard(state_df, chemical_df=None, top_chemicals_n=8):
    """
    Create an interactive dashboard with state map, waste type breakdown, and chemical composition
    
    Parameters:
        state_df: DataFrame with state_fips, total_release, total_air_release, 
                  total_water_release, total_land_release, state_name
        chemical_df: DataFrame from aggregate_by_chemical() or get_top_chemicals_by_state()
        top_chemicals_n: Number of top chemicals to show in pie chart (default: 8)
    
    Returns:
        Interactive Altair dashboard
    """
    # Create selection for states
    selection = alt.selection_point(fields=['state_fips'], empty='all')
    
    # Prepare waste type data for all states (for linked bar chart)
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
        width=700,
        height=500,
        title={
            "text": "US Toxic Waste Release Interactive Dashboard",
            "subtitle": "Click on any state to see detailed waste type breakdown and chemical composition",
            "fontSize": 16,
            "anchor": "middle"
        }
    ).project('albersUsa')
    
    # Stacked bar chart for waste type breakdown (filtered by selection)
    stacked_chart = alt.Chart(waste_df).mark_bar().encode(
        x=alt.X('type:N', 
                title='Waste Type',
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y('amount:Q', 
                title='Release Amount (lbs)',
                axis=alt.Axis(format='.0f')),
        color=alt.Color('type:N', 
                       scale=alt.Scale(scheme='category10'),
                       title='Waste Type',
                       legend=None),
        tooltip=['state:N', 'type:N', 'amount:Q']
    ).transform_filter(
        selection
    ).properties(
        width=300,
        height=250,
        title='Waste Type Breakdown for Selected State'
    )
    
    # Dynamic title showing selected state for chemical pie chart
    selected_state_text = alt.Chart(state_df).mark_text(
        align='center',
        fontSize=14,
        fontWeight='bold'
    ).encode(
        text=alt.condition(selection, alt.Text('state_name:N'), alt.value('No State Selected'))
    ).transform_filter(
        selection
    ).properties(
        width=400,
        height=30
    )
    
    # Create chemical pie chart (filtered by selection)
    # We need to pre-calculate top chemicals for each state or compute on the fly
    if chemical_df is None:
        # Option 1: Pre-calculate top chemicals for all states
        chemical_pie_chart = create_chemical_pie_chart_from_state_df(state_df, selection, top_chemicals_n)
    else:
        # Option 2: Use provided chemical_df
        chemical_pie_chart = create_chemical_pie_chart_from_chemical_df(chemical_df, selection, top_chemicals_n)
    
    # Horizontal bar chart for top states (highlighting selection)
    top_states = state_df.nlargest(15, 'total_release').copy()
    
    bar_chart = alt.Chart(top_states).mark_bar(
        cornerRadiusTopRight=5,
        cornerRadiusBottomRight=5
    ).encode(
        x=alt.X('total_release:Q', 
                title='Total Waste Release (lbs)',
                axis=alt.Axis(format='.0f')),
        y=alt.Y('state_name:N', 
                sort='-x', 
                title='State',
                axis=alt.Axis(labelLimit=300)),
        color=alt.condition(selection, 
                           alt.Color('total_release:Q', scale=alt.Scale(scheme='reds')), 
                           alt.value('lightgray')),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.5)),
        tooltip=[
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Waste:', format=',.0f')
        ]
    ).add_params(
        selection
    ).properties(
        width=350,
        height=350,
        title='Top 15 States by Total Waste (Click to select)'
    )
    
    # Combine right panel (bar chart + chemical pie)
    right_panel = alt.vconcat(
        bar_chart,
        selected_state_text,
        chemical_pie_chart
    )
    
    # Combine all charts in a dashboard layout
    dashboard = alt.vconcat(
        base_map,
        alt.hconcat(stacked_chart, right_panel)
    ).configure_view(
        stroke=None
    ).configure_legend(
        titleFontSize=12,
        labelFontSize=11
    )
    
    return dashboard


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
    else:
        enhanced_dashboard.save('Frontend/chart/state_map/TRI_State_Map_Dashboard_Throughout.html')


#--------------------------------------COUNTY--------------------------------------------
def create_county_background_map(width=800, height=600):
    """Create county background map"""
    counties = alt.topo_feature(data.us_10m.url, feature='counties')
    
    background = alt.Chart(counties).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).project('albersUsa').properties(
        width=width,
        height=height
    )
    
    return background


def create_county_choropleth(county_df, width=800, height=600):
    """Create county-level choropleth map"""
    counties = alt.topo_feature(data.us_10m.url, feature='counties')
    
    choropleth = alt.Chart(counties).mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(
            county_df,
            key='county_fips',
            fields=['total_release', 'county', 'state_name', 'county_fips']
        )
    ).properties(
        width=width,
        height=height
    ).encode(
        color=alt.Color('total_release:Q',
                       scale=alt.Scale(scheme='reds', type='symlog', constant=1),
                       title='Total Waste Release (lbs)',
                       legend=alt.Legend(format='.0f', tickCount=5, titleLimit=500)),
        tooltip=[
            alt.Tooltip('county:N', title='County'),
            alt.Tooltip('state_name:N', title='State'),
            alt.Tooltip('total_release:Q', title='Total Release', format=',.0f')
        ]
    )
    
    return choropleth


def add_county_interactive_stroke(choropleth, selection, hover_color='yellow', default_color='white'):
    """Add interactive stroke to county choropleth"""
    return choropleth.encode(
        stroke=alt.condition(
            selection,
            alt.value(hover_color),
            alt.value(default_color)
        ),
        strokeWidth=alt.condition(
            selection,
            alt.value(2),
            alt.value(0.5)
        )
    )


def total_waste_by_counties(choice=""):
    """
    County-level waste map with release type breakdown
    """
    county_df = tdp.get_county_waste_data(choice)
    bar_data = tdp.get_county_release_type_data(county_df)
    
    print(f"Counties loaded: {len(county_df)}")
    print(f"Total release sum: {county_df['total_release'].sum():,.0f}")
    
    MAP_WIDTH = 800
    MAP_HEIGHT = 600
    
    point_hover = alt.selection_point(
        fields=['county_fips'],
        on='pointerover',
        empty=False,
        name='hover_county'
    )
    
    background = create_county_background_map(MAP_WIDTH, MAP_HEIGHT)
    
    choropleth = create_county_choropleth(county_df, MAP_WIDTH, MAP_HEIGHT)
    choropleth = add_county_interactive_stroke(choropleth, point_hover)
    choropleth = choropleth.add_params(point_hover)
    choropleth = choropleth.project('albersUsa').properties(
        title='Total Waste Release by County'
    )
    
    bars = create_release_type_bars(bar_data, point_hover).properties(
        width=350,
        height=250
    )
    
    final_map = alt.hconcat(
        background + choropleth,
        bars
    ).resolve_scale(
        color='independent'
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/total_waste_by_counties_{suffix}.html')
    final_map.save(f'Frontend/chart/total_waste_by_counties_{suffix}.png')
    
    return final_map


def chemical_indicators_by_county(choice=""):
    """
    County-level map with chemical indicators on click
    """
    county_df, indicator_counts = tdp.get_county_chemical_indicator_data(choice)
    
    print(f"Counties loaded: {len(county_df)}")
    print(f"Indicator rows: {len(indicator_counts)}")
    
    MAP_WIDTH = 800
    MAP_HEIGHT = 600
    
    click_select = alt.selection_point(
        fields=['county_fips'],
        on='click',
        empty=False,
        name='select_county'
    )
    
    background = create_county_background_map(MAP_WIDTH, MAP_HEIGHT)
    
    choropleth = create_county_choropleth(county_df, MAP_WIDTH, MAP_HEIGHT)
    choropleth = add_county_interactive_stroke(choropleth, click_select, hover_color='blue')
    choropleth = choropleth.add_params(click_select)
    choropleth = choropleth.project('albersUsa').properties(
        title='Total Waste Release by County (Click for Chemical Indicators)'
    )
    
    bars = create_chemical_indicator_bars_county(indicator_counts, click_select)
    
    final_map = alt.hconcat(
        background + choropleth,
        bars
    ).resolve_scale(
        color='independent'
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/chemical_indicators_counties_{suffix}.html')
    final_map.save(f'Frontend/chart/chemical_indicators_counties_{suffix}.png')
    
    return final_map


def create_chemical_indicator_bars_county(indicator_counts, selection):
    """
    Create chemical indicator bars for county-level data
    """
    indicator_counts = indicator_counts.copy()
    indicator_counts['has_indicator_label'] = indicator_counts['has_indicator'].map({
        True: 'Yes',
        False: 'No'
    })
    
    bars = alt.Chart(indicator_counts).mark_bar().encode(
        x=alt.X('indicator:N',
                title=None,
                sort=['CAAC', 'CARC', 'FEDS', 'PBT', 'PFAS'],
                axis=alt.Axis(labelFontSize=12, labelAngle=0)),
        y=alt.Y('count:Q',
                title='Number of Chemicals',
                axis=alt.Axis(format='d')),
        color=alt.Color('has_indicator_label:N',
                       scale=alt.Scale(
                           domain=['No', 'Yes'],
                           range=['#D3D3D3', '#006837']
                       ),
                       legend=alt.Legend(
                           title='Has Indicator',
                           symbolType='square'
                       )),
        xOffset=alt.XOffset('has_indicator_label:N',
                           sort=['No', 'Yes']),
        tooltip=[
            alt.Tooltip('indicator:N', title='Indicator'),
            alt.Tooltip('has_indicator_label:N', title='Present'),
            alt.Tooltip('count:Q', title='Count', format='d')
        ]
    ).properties(
        width=350,
        height=300,
        title='Chemical Indicators (Click a County)'
    ).transform_filter(
        selection
    )
    
    return bars

def combined_county_waste_dashboard(choice=""):
    """
    Combined county dashboard with both release types and chemical indicators
    Hover: Shows release breakdown (Air, Land, Water)
    Click: Shows chemical indicators (CAAC, CARC, FEDS, PBT, PFAS)
    """
    print("Loading county data...")
    county_df = tdp.get_county_waste_data(choice)
    bar_data = tdp.get_county_release_type_data(county_df)
    
    print("Loading chemical indicator data...")
    _, indicator_counts = tdp.get_county_chemical_indicator_data(choice)
    
    print(f"\nDashboard Summary:")
    print(f"  Counties: {len(county_df)}")
    print(f"  Total Release: {county_df['total_release'].sum():,.0f} lbs")
    print(f"  Indicator rows: {len(indicator_counts)}")
    
    MAP_WIDTH = 900
    MAP_HEIGHT = 650
    BAR_WIDTH = 400
    RELEASE_BAR_HEIGHT = 250
    INDICATOR_BAR_HEIGHT = 350
    
    point_hover = alt.selection_point(
        fields=['county_fips'], 
        on='pointerover', 
        empty=False,
        name='hover_county'
    )
    
    click_select = alt.selection_point(
        fields=['county_fips'], 
        on='click', 
        empty=False,
        name='select_county'
    )
    
    background = create_county_background_map(width=MAP_WIDTH, height=MAP_HEIGHT)
    
    choropleth = create_county_choropleth(county_df, width=MAP_WIDTH, height=MAP_HEIGHT)
    
    choropleth = choropleth.transform_calculate(
        stroke_color="(select_county.county_fips && select_county.county_fips == datum.county_fips) ? 'blue' : "
                     "(hover_county.county_fips && hover_county.county_fips == datum.county_fips) ? 'yellow' : "
                     "'white'",
        stroke_width="(select_county.county_fips && select_county.county_fips == datum.county_fips) ? 3 : "
                     "(hover_county.county_fips && hover_county.county_fips == datum.county_fips) ? 2 : "
                     "0.5"
    ).encode(
        stroke=alt.Stroke('stroke_color:N', scale=None, legend=None),
        strokeWidth=alt.StrokeWidth('stroke_width:Q', scale=None, legend=None)
    )
    
    choropleth = choropleth.add_params(point_hover, click_select)
    choropleth = choropleth.project('albersUsa').properties(
        title=alt.TitleParams(
            text='Total Waste Release by County',
            subtitle=['Hover for release breakdown | Click for chemical indicators'],
            fontSize=16,
            anchor='start'
        )
    )
    
    release_bars = create_release_type_bars(
        bar_data, point_hover
    ).properties(
        width=BAR_WIDTH,
        height=RELEASE_BAR_HEIGHT
    )
    
    indicator_bars = create_chemical_indicator_bars_county(
        indicator_counts, click_select
    ).properties(
        width=BAR_WIDTH,
        height=INDICATOR_BAR_HEIGHT
    )
    
    bar_column = alt.vconcat(
        release_bars,
        indicator_bars
    ).resolve_scale(
        color='independent'
    ).resolve_legend(
        color='independent'
    )
    
    final_dashboard = alt.hconcat(
        background + choropleth,
        bar_column
    ).resolve_scale(
        color='independent'
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=30
    ).configure_title(
        fontSize=16,
        anchor='start'
    ).configure_axis(
        labelFontSize=11,
        titleFontSize=13
    ).configure_legend(
        labelFontSize=11,
        titleFontSize=13
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    
    print(f"\nSaving county dashboard...")
    final_dashboard.save(
        f'Frontend/chart/county_waste_dashboard_{suffix}.html'
    )
    final_dashboard.save(
        f'Frontend/chart/county_waste_dashboard_{suffix}.png',
        scale_factor=2.0
    )
    
    print("County dashboard saved successfully!")
    
    return final_dashboard

#combined_state_waste_dashboard()    

#combined_county_waste_dashboard()