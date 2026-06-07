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
import pycountry
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
with open('queries.json', 'r') as f:
    queries = json.load(f)

import pandas as pd
import us

def fetch_waste_data(choice=""):
    """
    Fetch raw waste data from database
    
    Parameters:
        choice: "" for all time, "After" for post-2020
    
    Returns:
        DataFrame with columns: city, county, state, unique_chemical_count,
        total_release, total_land_release, total_water_release, total_air_release, chemical_ids
    """
    if choice == 'After':
        df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine)
    else:
        df = pd.read_sql(queries['Waste_By_Location'], con=engine)
    
    state_mapping = {
        'GE': 'GA', 'IK': 'OK', 'IO': 'IA', 'TE': 'TX', 'W': 'WA', 'KA': 'KS'
    }
    df['state'] = df['state'].replace(state_mapping)
    df = df.dropna(subset=['state'])
    return df

def create_state_fips_mapping():
    """
    Create mapping of state abbreviations to FIPS codes and names
    
    Returns:
        DataFrame with columns: state, state_fips, state_name
    """
    states_data = []
    for state in us.states.STATES:
        states_data.append({
            'state': state.abbr,
            'state_fips': state.fips,
            'state_name': state.name
        })
    
    return pd.DataFrame(states_data)


def aggregate_by_state(df):
    """
    Goal 1 & 2: Get total waste per state and waste type (air, water, land)
    
    Parameters:
        df: DataFrame from fetch_waste_data() - has chemical-level rows
    
    Returns:
        DataFrame with state-level aggregations: total_release, land, water, air
    """
    
    
    df = df.copy()
    
    # First aggregate to location level (state-county-city) to avoid double-counting
    location_df = df.groupby(['state', 'county', 'city'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Then aggregate to state level
    state_df = location_df.groupby('state', as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Add FIPS codes
    fips_mapping = create_state_fips_mapping()
    state_df = state_df.merge(fips_mapping, on='state', how='left')
    state_df = state_df.dropna(subset=['state_fips'])
    state_df['state_fips'] = state_df['state_fips'].astype(str).str.zfill(2)
    
    return state_df


def aggregate_by_chemical(df):
    """
    Goal 3: Get total waste by chemical (chem_name)
    
    Parameters:
        df: DataFrame from fetch_waste_data()
    
    Returns:
        DataFrame with chemical-level aggregations across all states
    """
    df = df.copy()
    
    # Aggregate to location level first
    location_df = df.groupby(['state', 'county', 'city', 'tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Then aggregate by chemical across all locations
    chemical_df = location_df.groupby(['tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Sort by total release descending
    chemical_df = chemical_df.sort_values('total_release', ascending=False).reset_index(drop=True)
    
    return chemical_df


def aggregate_boolean_indicators_by_state(df):
    """
    Goal 4: Get percentage of True occurrences per state for boolean indicators
    
    Parameters:
        df: DataFrame from fetch_waste_data() with chemical info joined
    
    Returns:
        DataFrame with state and percentage of True for each indicator
    """
  
    df = df.copy()
    # First deduplicate at chemical-location level
    # Each combination of state + chemical should be counted once for boolean indicators
    unique_chemicals_per_state = df.groupby(['state', 'tri_chem_id', 'chem_name']).first().reset_index()
    
    # Calculate percentages for each boolean indicator
    boolean_cols = ['caac_ind', 'carc_ind', 'feds_ind', 'pbt_ind', 'pfas_ind']
    
    result_dfs = []
    for col in boolean_cols:
        # Convert to boolean if needed (handle potential string 'True'/'False' or 1/0)
        unique_chemicals_per_state[col] = unique_chemicals_per_state[col].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        
        # Calculate percentage of True per state
        state_stats = unique_chemicals_per_state.groupby('state')[col].agg(['sum', 'count'])
        state_stats['percentage'] = (state_stats['sum'] / state_stats['count'] * 100).round(2)
        state_stats = state_stats[['percentage']].rename(columns={'percentage': f'pct_{col}'})
        result_dfs.append(state_stats)
    
    # Combine all indicators
    boolean_df = result_dfs[0]
    for df_bool in result_dfs[1:]:
        boolean_df = boolean_df.join(df_bool)
    
    boolean_df = boolean_df.reset_index()
    
    # Add FIPS codes
    fips_mapping = create_state_fips_mapping()
    boolean_df = boolean_df.merge(fips_mapping, on='state', how='left')
    boolean_df = boolean_df.dropna(subset=['state_fips'])
    boolean_df['state_fips'] = boolean_df['state_fips'].astype(str).str.zfill(2)
    
    return boolean_df


def get_complete_state_analysis(df):
    """
    Combine all goals into a single comprehensive state-level DataFrame
    
    Returns:
        DataFrame with total waste, waste types, and boolean percentages per state
    """
    # Goal 1 & 2: Total waste by state
    waste_df = aggregate_by_state(df)
    
    # Goal 4: Boolean percentages by state
    boolean_df = aggregate_boolean_indicators_by_state(df)
    
    # Combine all
    complete_df = waste_df.merge(boolean_df, on=['state', 'state_fips', 'state_name'], how='left')
    
    return complete_df


def get_top_chemicals_by_state(df, state_abbr, top_n=10):
    """
    Bonus: Get top chemicals for a specific state
    
    Parameters:
        df: DataFrame from fetch_waste_data()
        state_abbr: State abbreviation (e.g., 'TX', 'CA')
        top_n: Number of top chemicals to return
    
    Returns:
        DataFrame with top chemicals by total release for that state
    """

    df = df.copy()

    # Filter for specific state
    state_df = df[df['state'] == state_abbr].copy()
    
    # Aggregate to location-chemical level then sum
    location_chem = state_df.groupby(['county', 'city', 'tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Sum by chemical
    chemical_totals = location_chem.groupby(['tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Get top N
    top_chemicals = chemical_totals.nlargest(top_n, 'total_release')
    
    return top_chemicals


def inspect_state_data(state_df):
    """Print summary of state waste data"""
    print("State Waste Data Summary:")
    print("-" * 50)
    print(f"Number of states: {len(state_df)}")
    print(f"\nColumns: {state_df.columns.tolist()}")
    print(f"\nSample data:")
    print(state_df.head(10))
    print(f"\nFIPS dtype: {state_df['state_fips'].dtype}")
    print(f"Sample FIPS: {state_df['state_fips'].tolist()[:5]}")
    print(f"\nTotal release stats:")
    print(f"  Sum: {state_df['total_release'].sum():,.0f}")
    print(f"  Mean: {state_df['total_release'].mean():,.0f}")
    print(f"  Max: {state_df['total_release'].max():,.0f}")
    print(f"  Unique values: {state_df['total_release'].nunique()}")

def state_waste_analysis():
    # Test the complete workflow
    print("=" * 60)
    print("TESTING WASTE DATA ANALYSIS FUNCTIONS")
    print("=" * 60)

    # Fetch data - this now includes all chemical info from the SQL join
    df = fetch_waste_data('After')  # or fetch_waste_data() for all years
    print(f"\n✓ Fetched {len(df)} rows of waste data")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Unique states: {sorted(df['state'].unique())}")
    print(f"  Boolean indicators present: {[col for col in df.columns if col.endswith('_ind')]}")

    # Test Goal 1 & 2: State-level waste totals
    print("\n" + "=" * 60)
    print("GOAL 1 & 2: Total Waste Per State by Type")
    print("=" * 60)

    state_waste = aggregate_by_state(df)
    print(f"\nShape: {state_waste.shape}")
    print(f"\nFirst 10 states by total release:")
    top_states = state_waste.nlargest(10, 'total_release')[['state', 'state_name', 'total_release', 'total_air_release', 'total_water_release', 'total_land_release']]
    print(top_states.to_string(index=False))

    # Test Goal 3: Chemical-level totals
    print("\n" + "=" * 60)
    print("GOAL 3: Total Waste by Chemical")
    print("=" * 60)

    chemical_waste = aggregate_by_chemical(df)
    print(f"\nShape: {chemical_waste.shape}")
    print(f"\nTop 10 chemicals by total release:")
    top_chemicals = chemical_waste.head(10)[['chem_name', 'total_release', 'total_air_release', 'total_water_release', 'total_land_release']]
    print(top_chemicals.to_string(index=False))

    # Test Goal 4: Boolean indicators by state
    print("\n" + "=" * 60)
    print("GOAL 4: Boolean Indicator Percentages by State")
    print("=" * 60)

    boolean_stats = aggregate_boolean_indicators_by_state(df)
    print(f"\nShape: {boolean_stats.shape}")
    print(f"\nFirst 10 states with indicator percentages:")
    bool_cols = [col for col in boolean_stats.columns if col.startswith('pct_')]
    display_cols = ['state', 'state_name'] + bool_cols
    print(boolean_stats.head(10)[display_cols].to_string(index=False))

    # Test complete analysis
    print("\n" + "=" * 60)
    print("COMPLETE STATE ANALYSIS (All Goals Combined)")
    print("=" * 60)

    complete_analysis = get_complete_state_analysis(df)
    print(f"\nShape: {complete_analysis.shape}")
    print(f"\nColumns: {complete_analysis.columns.tolist()}")
    print(f"\nSample for Texas:")
    tx_data = complete_analysis[complete_analysis['state'] == 'TX']
    if len(tx_data) > 0:
        print(tx_data.to_string(index=False))

    # Test bonus: Top chemicals by state
    print("\n" + "=" * 60)
    print("BONUS: Top Chemicals by State")
    print("=" * 60)

    for state in ['TX', 'CA', 'FL', 'NY']:
        top_chems = get_top_chemicals_by_state(df, state, top_n=5)
        if len(top_chems) > 0:
            print(f"\nTop 5 chemicals in {state}:")
            print(top_chems[['chem_name', 'total_release']].to_string(index=False))
        else:
            print(f"\nNo data found for {state}")

    # Test inspection function
    print("\n" + "=" * 60)
    print("STATE DATA INSPECTION")
    print("=" * 60)
    inspect_state_data(state_waste)

    # Validation checks
    print("\n" + "=" * 60)
    print("VALIDATION CHECKS")
    print("=" * 60)

    # Check for data completeness
    print("\n1. State coverage:")
    from us import states
    expected_states = set([state.abbr for state in states.STATES])
    actual_states = set(state_waste['state'].unique())
    missing_states = expected_states - actual_states
    print(f"   States in data: {len(actual_states)}")
    print(f"   Expected states: {len(expected_states)}")
    if missing_states:
        print(f"   Missing states: {sorted(missing_states)[:10]}...")

    # Check for negative values
    print("\n2. Value validation:")
    for col in ['total_release', 'total_land_release', 'total_water_release', 'total_air_release']:
        negative_count = (state_waste[col] < 0).sum()
        if negative_count > 0:
            print(f"   WARNING: {negative_count} negative values in {col}")
        else:
            print(f"   ✓ No negative values in {col}")

    # Check percentage ranges
    print("\n3. Boolean percentage validation:")
    for col in bool_cols:
        pct_range = boolean_stats[col].min(), boolean_stats[col].max()
        print(f"   {col}: range {pct_range[0]:.1f}% - {pct_range[1]:.1f}%")

    print("\n" + "=" * 60)
    print("TESTING COMPLETE ✓")
    print("=" * 60)
state_waste_analysis()

def map_db_counties_to_fips_code(location_db):
    print("Starting function...")
    print(f"Loaded {len(location_db)} rows")
    
    def safe_state_lookup(abbr):
        result = states.lookup(abbr)
        return result.name if result is not None else pd.NA 
    
    location_db['state_name'] = location_db['state'].apply(safe_state_lookup)
    print("State names added")
    
    af = addfips.AddFIPS()
    
    unique_counties = location_db[['county', 'state']].drop_duplicates()
    print(f"Processing {len(unique_counties)} unique county-state combinations")
    
    county_fips_map = {}
    for _, row in unique_counties.iterrows():
        try:
            county_fips_map[(row['county'], row['state'])] = af.get_county_fips(row['county'], state=row['state'])
        except Exception as e:
            print(f"Error looking up {row['county']}, {row['state']}: {e}")
            county_fips_map[(row['county'], row['state'])] = pd.NA
    
    print(f"Created FIPS map with {len(county_fips_map)} entries")

    location_db['county_fips'] = location_db.apply(
        lambda row: county_fips_map.get((row['county'], row['state']), pd.NA), 
        axis=1
    )

    return location_db

def get_county_waste_data(choice=""):
    """
    Fetch and process county-level waste data
    
    Parameters:
        choice: "" for all time, "After" for post-2020
    
    Returns:
        county_df: DataFrame with county-level aggregations and FIPS codes
    """
    if choice == 'After':
        df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine)
    else:
        df = pd.read_sql(queries['Waste_By_Location'], con=engine)
    
    df = map_db_counties_to_fips_code(location_db=df)
    
    county_df = df.groupby('county_fips').agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum',
        'county': 'first',
        'state_name': 'first',
        'state': 'first'
    }).reset_index()
    
    county_df = county_df.dropna(subset=['county_fips'])
    county_df['county_fips'] = county_df['county_fips'].astype(str).str.zfill(5)
    
    return county_df


def get_county_chemical_indicator_data(choice=""):
    """
    Process chemical indicator data at county level
    
    Returns:
        county_df: DataFrame for map
        indicator_counts: DataFrame for indicator bars
    """
    if choice == 'After':
        df = pd.read_sql(queries['Waste_By_Location_2020s'], con=engine)
    else:
        df = pd.read_sql(queries['Waste_By_Location'], con=engine)
    
    chem_info_df = fetch_chemical_info()
    
    df = map_db_counties_to_fips_code(location_db=df)
    
    county_df = df.groupby('county_fips').agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum',
        'county': 'first',
        'state_name': 'first',
        'state': 'first'
    }).reset_index()
    
    county_df = county_df.dropna(subset=['county_fips'])
    county_df['county_fips'] = county_df['county_fips'].astype(str).str.zfill(5)
    

    chem_data = df[['county_fips', 'chemical_ids']].copy()
    chem_data['chem_str'] = chem_data['chemical_ids'].apply(
        lambda x: ','.join(sorted([str(i) for i in x])) if isinstance(x, list) else str(x)
    )
    chem_data = chem_data.drop_duplicates(subset=['county_fips', 'chem_str'])
    chem_data = chem_data.drop(columns=['chem_str'])
    
    chem_data = chem_data.explode('chemical_ids')
    chem_data = chem_data.rename(columns={'chemical_ids': 'tri_chem_id'})
    chem_data['tri_chem_id'] = chem_data['tri_chem_id'].astype(str)
    chem_data = chem_data.dropna(subset=['tri_chem_id'])
    
    chem_info_subset = chem_info_df[[
        'tri_chem_id', 'caac_ind', 'carc_ind', 'feds_ind', 
        'pbt_ind', 'pfas_ind'
    ]]
    
    chem_data = chem_data.merge(chem_info_subset, on='tri_chem_id', how='left')
    
    indicator_cols = ['caac_ind', 'carc_ind', 'feds_ind', 'pbt_ind', 'pfas_ind']
    
    indicator_data = chem_data.melt(
        id_vars=['county_fips'],
        value_vars=indicator_cols,
        var_name='indicator',
        value_name='has_indicator'
    )
    
    indicator_data['indicator'] = indicator_data['indicator'].str.replace('_ind', '').str.upper()
    
    indicator_counts = indicator_data.groupby(
        ['county_fips', 'indicator', 'has_indicator']
    ).size().reset_index(name='count')
    
    return county_df, indicator_counts


def get_county_release_type_data(county_df):
    """
    Transform county data for release type bar chart
    
    Returns:
        DataFrame in long format
    """
    bar_data = county_df.melt(
        id_vars=['county_fips', 'county', 'state_name', 'total_release'],
        value_vars=['total_land_release', 'total_water_release', 'total_air_release'],
        var_name='release_type',
        value_name='release_amount(lbs)'
    )
    
    bar_data['release_type'] = (
        bar_data['release_type']
        .str.replace('total_', '')
        .str.replace('_release', '')
        .str.title()
    )
    
    return bar_data

# state_df, bar_data = get_state_waste_data(choice='After')
# inspect_state_data(state_df)

# state_df, indicator_counts = get_chemical_indicator_data(choice='After')
# inspect_indicator_data(indicator_counts)
