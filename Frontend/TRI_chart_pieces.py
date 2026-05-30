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
    Create bar chart showing chemical indicators
    
    Parameters:
        indicator_counts: DataFrame with indicator counts
        selection: Altair selection for filtering
    
    Returns:
        Altair chart
    """
    bars = alt.Chart(indicator_counts).mark_bar().encode(
        y=alt.Y('indicator:N', 
                title=None,
                sort=['CAAC', 'CARC', 'FEDS', 'PBT', 'PFAS'],
                axis=alt.Axis(labelFontSize=12)),
        x=alt.X('count:Q', 
                title='Number of Chemicals',
                axis=alt.Axis(format='d')),
        color=alt.Color('has_indicator:N',
                       scale=alt.Scale(
                           domain=[False, True],
                           range=['#D3D3D3', '#006837']
                       ),
                       legend=alt.Legend(
                           title='Has Indicator',
                           labelExpr="datum.value ? 'Yes' : 'No'"
                       )),
        tooltip=[
            alt.Tooltip('indicator:N', title='Indicator'),
            alt.Tooltip('has_indicator:N', title='Present'),
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
    # ---- Data Processing ----
    state_df, bar_data = tdp.get_state_waste_data(choice)
    
    # Debug info
    print("State Waste Data Summary:")
    print(f"  States: {len(state_df)}")
    print(f"  Total Release Sum: {state_df['total_release'].sum():,.0f}")
    print(f"  Mean Release: {state_df['total_release'].mean():,.0f}")
    print(f"  Sample FIPS: {state_df['state_fips'].tolist()[:5]}")
    
    # ---- Create Visualization ----
    # Selection
    point_hover = alt.selection_point(
        fields=['state_fips'], 
        on='pointerover', 
        empty=False,
        name='hover_state'
    )
    
    # Background
    background = create_background_map()
    
    # Choropleth with interactivity
    choropleth = create_state_choropleth(state_df)
    choropleth = add_interactive_stroke(choropleth, point_hover)
    choropleth = choropleth.add_params(point_hover)
    choropleth = choropleth.project('albersUsa').properties(
        width=700,
        height=500,
        title='Total Waste Release by State'
    )
    
    # Release type bars
    bars = create_release_type_bars(bar_data, point_hover)
    
    # Combine
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
    
    # ---- Save ----
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/total_waste_by_state_{suffix}.png')
    final_map.save(f'Frontend/chart/total_waste_by_state_{suffix}.html')
    
    return final_map


def chemical_indicators_by_state(choice=""):
    """
    Main visualization function: Chemical indicators map with click interaction
    """
    # ---- Data Processing ----
    state_df, indicator_counts = tdp.get_chemical_indicator_data(choice)
    
    # Debug info
    print("Chemical Indicators Data Summary:")
    print(f"  States: {len(state_df)}")
    print(f"  Indicator rows: {len(indicator_counts)}")
    print(f"  Indicators: {indicator_counts['indicator'].unique().tolist()}")
    
    # ---- Create Visualization ----
    # Selection
    click_select = alt.selection_point(
        fields=['state_fips'], 
        on='click', 
        empty=False,
        name='select_state'
    )
    
    # Background
    background = create_background_map()
    
    # Choropleth with interactivity
    choropleth = create_state_choropleth(state_df)
    choropleth = add_interactive_stroke(choropleth, click_select)
    choropleth = choropleth.add_params(click_select)
    choropleth = choropleth.project('albersUsa').properties(
        width=700,
        height=500,
        title='Total Waste Release by State (Click for Chemical Indicators)'
    )
    
    # Chemical indicator bars
    bars = create_chemical_indicator_bars(indicator_counts, click_select)
    
    # Combine
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
    
    # ---- Save ----
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_map.save(f'Frontend/chart/chemical_indicators_{suffix}.png')
    final_map.save(f'Frontend/chart/chemical_indicators_{suffix}.html')
    
    return final_map


def combined_waste_dashboard(choice=""):
    """
    Combined dashboard with both release types and chemical indicators
    """
    # ---- Data Processing ----
    state_df, bar_data = tdp.get_state_waste_data(choice)
    _, indicator_counts = tdp.get_chemical_indicator_data(choice)
    
    # ---- Create Visualization ----
    # Selections
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
    
    # Background
    background = create_background_map()
    
    # Choropleth with both interactions
    choropleth = create_state_choropleth(state_df)
    
    # Add hover stroke (yellow for hover, click overrides to blue)
    choropleth = choropleth.encode(
        stroke=alt.condition(
            click_select,
            alt.value('blue'),  # Clicked state
            alt.condition(
                point_hover,
                alt.value('yellow'),  # Hovered state
                alt.value('white')   # Default
            )
        ),
        strokeWidth=alt.condition(
            click_select,
            alt.value(3),
            alt.condition(
                point_hover,
                alt.value(2),
                alt.value(0.5)
            )
        )
    )
    
    choropleth = choropleth.add_params(point_hover, click_select)
    choropleth = choropleth.project('albersUsa').properties(
        width=700,
        height=500,
        title='Total Waste Release by State'
    )
    
    # Release type bars (hover)
    release_bars = create_release_type_bars(bar_data, point_hover)
    
    # Chemical indicator bars (click)
    indicator_bars = create_chemical_indicator_bars(indicator_counts, click_select)
    
    # Stack the bar charts vertically
    bar_column = alt.vconcat(
        release_bars,
        indicator_bars
    ).resolve_legend(
        color='independent'
    )
    
    # Combine everything
    final_dashboard = alt.hconcat(
        background + choropleth,
        bar_column
    ).resolve_legend(
        color='independent'
    ).configure_concat(
        spacing=20
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
    
    # ---- Save ----
    suffix = '2020s' if choice == 'After' else 'all_time'
    final_dashboard.save(f'Frontend/chart/waste_dashboard_{suffix}.png')
    final_dashboard.save(f'Frontend/chart/waste_dashboard_{suffix}.html')
    
    return final_dashboard

combined_waste_dashboard(choice = 'After')    