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
    
    return df


def fetch_chemical_info():
    """
    Fetch chemical reference information
    
    Returns:
        DataFrame with chemical properties and indicators
    """
    df = pd.read_sql(queries['Chemical_Info'], con=engine)
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
    Aggregate waste data from city/county level to state level
    
    Parameters:
        df: DataFrame from fetch_waste_data()
    
    Returns:
        DataFrame with state-level aggregations and FIPS codes
    """
    state_df = df.drop(columns=['city', 'county', 'chemical_ids', 'unique_chemical_count'])
    state_df = state_df.drop_duplicates()
    
    state_df = state_df.groupby('state').agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    }).reset_index()
    
    fips_mapping = create_state_fips_mapping()
    state_df = state_df.merge(fips_mapping, on='state', how='left')
    
    state_df = state_df.dropna(subset=['state_fips'])
    state_df['state_fips'] = state_df['state_fips'].astype(str).str.zfill(2)
    
    return state_df

def get_chemicals_by_state(df, chem_info_df):
    """
    Simplified version - converts array to string for deduplication
    """
    chem_data = df[['state', 'chemical_ids']].copy()
    
    chem_data['chem_str'] = chem_data['chemical_ids'].apply(
        lambda x: ','.join(sorted([str(i) for i in x])) if isinstance(x, list) else str(x)
    )
    
    chem_data = chem_data.drop_duplicates(subset=['state', 'chem_str'])
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
    
    return chem_data

def create_indicator_counts(chem_data):
    """
    Create summary counts of chemical indicators by state
    
    Parameters:
        chem_data: DataFrame from get_chemicals_by_state()
    
    Returns:
        DataFrame with indicator counts (True/False) per state
    """
    indicator_cols = ['caac_ind', 'carc_ind', 'feds_ind', 'pbt_ind', 'pfas_ind']
    
    indicator_data = chem_data.melt(
        id_vars=['state'],
        value_vars=indicator_cols,
        var_name='indicator',
        value_name='has_indicator'
    )
    
    indicator_data['indicator'] = indicator_data['indicator'].str.replace('_ind', '').str.upper()
    
    fips_mapping = create_state_fips_mapping()
    indicator_data = indicator_data.merge(fips_mapping[['state', 'state_fips']], on='state')
    
    indicator_counts = indicator_data.groupby(
        ['state', 'state_fips', 'indicator', 'has_indicator']
    ).size().reset_index(name='count')
    
    return indicator_counts


def create_release_type_data(state_df):
    """
    Transform state waste data for release type visualization
    
    Parameters:
        state_df: DataFrame from aggregate_by_state()
    
    Returns:
        DataFrame in long format with release types
    """
    bar_data = state_df.melt(
        id_vars=['state', 'state_fips', 'state_name', 'total_release'],
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


def get_state_waste_data(choice=""):
    """
    Main data processing function for state waste map
    
    Returns: state_df (for map), bar_data (for release type bars)
    """
    df = fetch_waste_data(choice)
    
    state_df = aggregate_by_state(df)
    
    bar_data = create_release_type_data(state_df)
    
    return state_df, bar_data


def get_chemical_indicator_data(choice=""):
    """
    Main data processing function for chemical indicators
    
    Returns: state_df (for map), indicator_counts (for indicator bars)
    """
    df = fetch_waste_data(choice)
    chem_info_df = fetch_chemical_info()
    
    state_df = aggregate_by_state(df)
    
    chem_data = get_chemicals_by_state(df, chem_info_df)
    indicator_counts = create_indicator_counts(chem_data)
    
    return state_df, indicator_counts


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


def inspect_indicator_data(indicator_counts):
    """Print summary of indicator data"""
    print("Chemical Indicator Data Summary:")
    print("-" * 50)
    print(f"Number of rows: {len(indicator_counts)}")
    print(f"\nColumns: {indicator_counts.columns.tolist()}")
    print(f"\nIndicators: {indicator_counts['indicator'].unique().tolist()}")
    print(f"\nSample data:")
    print(indicator_counts.head(10))
    print(f"\nCounts by indicator:")
    summary = indicator_counts.groupby('indicator')['count'].sum()
    print(summary)



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
state_df, bar_data = get_state_waste_data(choice='After')
inspect_state_data(state_df)

state_df, indicator_counts = get_chemical_indicator_data(choice='After')
inspect_indicator_data(indicator_counts)