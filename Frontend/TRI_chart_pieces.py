import altair as alt
from vega_datasets import data
import TRI_data_processing as tdp

def create_state_choropleth(state_df):
    """
    Create the choropleth map layer
    
    Parameters:
        state_df: DataFrame with state_fips, total_release, state_name
    
    Returns:
        Altair chart layer
    """
    us_states = alt.topo_feature(data.us_10m.url, feature='states')
    
    choropleth = alt.Chart(us_states).mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(
            state_df, 
            key='state_fips',
            fields=['total_release', 'state_name', 'state_fips']
        )
    ).encode(
        color=alt.Color('total_release:Q',
                       scale=alt.Scale(scheme='reds', type='symlog', constant=1),
                       title="Total Waste Release (lbs)",
                       legend=alt.Legend(format='.0f', tickCount=5, titleLimit=500)),
        tooltip=[
            alt.Tooltip('state_name:N', title="State:"),
            alt.Tooltip('total_release:Q', title='Total Waste:', format=',.0f')
        ]
    )
    
    return choropleth


def create_background_map():
    """
    Create the background map layer
    
    Returns:
        Altair chart layer
    """
    us_states = alt.topo_feature(data.us_10m.url, feature='states')
    
    background = alt.Chart(us_states).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).project('albersUsa').properties(
        width=700,
        height=500
    )
    
    return background


def create_release_type_bars(bar_data, selection):
    """
    Create bar chart showing release type breakdown
    
    Parameters:
        bar_data: DataFrame with release_type and release_amount columns
        selection: Altair selection for filtering
    
    Returns:
        Altair chart
    """
    bars = alt.Chart(bar_data).mark_bar().encode(
        y=alt.Y('release_type:N', 
                title=None, 
                sort=['Air', 'Land', 'Water'],
                axis=alt.Axis(labelFontSize=12)),
        x=alt.X('release_amount(lbs):Q', 
                title='Release Amount (lbs)', 
                axis=alt.Axis(format='.1e', labelFontSize=10)),
        color=alt.Color('release_type:N',
                       scale=alt.Scale(
                           domain=['Air', 'Land', 'Water'],
                           range=['#87CEEB', '#8B4513', '#4682B4']
                       ),
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
        selection
    )
    
    return bars


def create_chemical_indicator_bars(indicator_counts, selection):
    """
    Create grouped vertical bar chart (side-by-side bars)
    This avoids the color conflict entirely
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
        title='Chemical Indicators'
    ).transform_filter(
        selection
    )
    
    return bars

def add_interactive_stroke(choropleth, selection, hover_color='yellow', default_color='white'):
    """
    Add interactive stroke to choropleth based on selection
    
    Parameters:
        choropleth: Altair choropleth chart
        selection: Altair selection object
        hover_color: Color when selected/hovered
        default_color: Default stroke color
    
    Returns:
        Altair chart with stroke encoding
    """
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


def total_waste_by_state_throughout_or_After_2020(choice=""):
    """
    Main visualization function: State waste map with release type breakdown
    """
    state_df, bar_data = tdp.get_state_waste_data(choice)
    
    print("State Waste Data Summary:")
    print(f"  States: {len(state_df)}")
    print(f"  Total Release Sum: {state_df['total_release'].sum():,.0f}")
    print(f"  Mean Release: {state_df['total_release'].mean():,.0f}")
    print(f"  Sample FIPS: {state_df['state_fips'].tolist()[:5]}")
    
    point_hover = alt.selection_point(
        fields=['state_fips'], 
        on='pointerover', 
        empty=False,
        name='hover_state'
    )
    
    background = create_background_map()
    
    choropleth = create_state_choropleth(state_df)
    choropleth = add_interactive_stroke(choropleth, point_hover)
    choropleth = choropleth.add_params(point_hover)
    choropleth = choropleth.project('albersUsa').properties(
        width=700,
        height=500,
        title='Total Waste Release by State'
    )
    
    bars = create_release_type_bars(bar_data, point_hover)
    
    final_map = alt.hconcat(
        background + choropleth,
        bars
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/total_waste_by_state_{suffix}.png')
    final_map.save(f'Frontend/chart/total_waste_by_state_{suffix}.html')
    
    return final_map


def chemical_indicators_by_state(choice=""):
    """
    Main visualization function: Chemical indicators map with click interaction
    """
    state_df, indicator_counts = tdp.get_chemical_indicator_data(choice)
    
    print("Chemical Indicators Data Summary:")
    print(f"  States: {len(state_df)}")
    print(f"  Indicator rows: {len(indicator_counts)}")
    print(f"  Indicators: {indicator_counts['indicator'].unique().tolist()}")
    
    click_select = alt.selection_point(
        fields=['state_fips'], 
        on='click', 
        empty=False,
        name='select_state'
    )
    
    background = create_background_map()
    
    choropleth = create_state_choropleth(state_df)
    choropleth = add_interactive_stroke(choropleth, click_select)
    choropleth = choropleth.add_params(click_select)
    choropleth = choropleth.project('albersUsa').properties(
        width=700,
        height=500,
        title='Total Waste Release by State (Click for Chemical Indicators)'
    )
    
    bars = create_chemical_indicator_bars(indicator_counts, click_select)
    
    final_map = alt.hconcat(
        background + choropleth,
        bars
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/chemical_indicators_{suffix}.png')
    final_map.save(f'Frontend/chart/chemical_indicators_{suffix}.html')
    
    return final_map


def combined_state_waste_dashboard(choice=""):
    """
    Combined dashboard with both release types and chemical indicators
    """
    state_df, bar_data = tdp.get_state_waste_data(choice)
    _, indicator_counts = tdp.get_chemical_indicator_data(choice)
    
    MAP_WIDTH = 800
    MAP_HEIGHT = 600
    

    point_hover = alt.selection_point(
        fields=['state_fips'], 
        on='pointerover', 
        empty=False,
        name='hover_state'
    )
    
    click_select = alt.selection_point(
        fields=['state_fips'], 
        on='click', 
        empty=False,
        name='select_state'
    )
    
    background = alt.Chart(
        alt.topo_feature(data.us_10m.url, feature='states')
    ).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).project('albersUsa').properties(
        width=MAP_WIDTH,
        height=MAP_HEIGHT  
    )
    
    choropleth = create_state_choropleth(state_df)
    
    choropleth = choropleth.transform_calculate(
        stroke_color="(select_state.state_fips && select_state.state_fips == datum.state_fips) ? 'blue' : "
                     "(hover_state.state_fips && hover_state.state_fips == datum.state_fips) ? 'yellow' : "
                     "'white'",
        stroke_width="(select_state.state_fips && select_state.state_fips == datum.state_fips) ? 3 : "
                     "(hover_state.state_fips && hover_state.state_fips == datum.state_fips) ? 2 : "
                     "0.5"
    ).encode(
        stroke=alt.Stroke('stroke_color:N', scale=None, legend=None),
        strokeWidth=alt.StrokeWidth('stroke_width:Q', scale=None, legend=None)
    )
    
    choropleth = choropleth.add_params(point_hover, click_select)
    choropleth = choropleth.project('albersUsa').properties(
        width=MAP_WIDTH,
        height=MAP_HEIGHT,  # Same as background
        title='Total Waste Release by State'
    )
    
    release_bars = create_release_type_bars(bar_data, point_hover)
    
    indicator_bars = create_chemical_indicator_bars(indicator_counts, click_select)
    
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
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_dashboard.save(f'Frontend/chart/waste_dashboard_{suffix}.png')
    final_dashboard.save(f'Frontend/chart/waste_dashboard_{suffix}.html')
    
    return final_dashboard

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