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

def prepare_top_chemicals_per_state(df, state_df, top_n=8):
    """
    Pre-compute top chemicals for each state for dashboard visualization
    
    Parameters:
        df: DataFrame from fetch_waste_data()
        state_df: DataFrame from aggregate_by_state() (contains state_fips and state_name)
        top_n: Number of top chemicals per state
    
    Returns:
        DataFrame with top chemicals per state including 'Other Chemicals' category
    """
    df = df.copy()
    
        # Create a mapping for state names and FIPS codes
    state_info = state_df[['state', 'state_fips', 'state_name']].drop_duplicates()
    
    # Aggregate to state-chemical level (only using columns that exist in raw df)
    state_chemical = df.groupby(['state', 'tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Merge with state info to add state_fips and state_name
    state_chemical = state_chemical.merge(state_info, on='state', how='left')
    
    # Drop any rows where state_fips is NaN
    state_chemical = state_chemical.dropna(subset=['state_fips'])
    
    # Get top N chemicals per state
    top_chemicals_per_state = []
    
    for state in state_chemical['state'].unique():
        state_data = state_chemical[state_chemical['state'] == state].copy()
        
        # Ensure we have data for this state
        if len(state_data) == 0:
            continue
            
        top_n_state = state_data.nlargest(top_n, 'total_release')
        
        # Add "Other" category for remaining chemicals
        other_total = state_data[~state_data['chem_name'].isin(top_n_state['chem_name'])]['total_release'].sum()
        
        if other_total > 0:
            # Get state info for the other row - with safe access
            state_info_rows = state_info[state_info['state'] == state]
            if len(state_info_rows) > 0:
                state_info_row = state_info_rows.iloc[0]
                other_row = pd.DataFrame({
                    'state': [state],
                    'state_fips': [state_info_row['state_fips']],
                    'state_name': [state_info_row['state_name']],
                    'tri_chem_id': ['OTHER'],
                    'chem_name': ['Other Chemicals'],
                    'total_release': [other_total]
                })
                top_n_state = pd.concat([top_n_state, other_row], ignore_index=True)
        
        top_chemicals_per_state.append(top_n_state)
    
    # Combine all states
    if top_chemicals_per_state:
        result_df = pd.concat(top_chemicals_per_state, ignore_index=True)
    
    else:
        # Return empty DataFrame with expected columns if no data
        result_df = pd.DataFrame(columns=['state', 'state_fips', 'state_name', 'tri_chem_id', 'chem_name', 'total_release'])
    
    return result_df

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


#----------------COUNTY---------------------------
def aggregate_by_county(df):
    """
    Goal 1 & 2: Get total waste per county and waste type (air, water, land)
    
    Parameters:
        df: DataFrame from fetch_waste_data() - has chemical-level rows
    
    Returns:
        DataFrame with county-level aggregations: total_release, land, water, air
        Includes state and FIPS codes (combined state+county FIPS)
    """
    df = df.copy()
    
    # First aggregate to location level (state-county-city) to avoid double-counting
    location_df = df.groupby(['state', 'county', 'city'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Then aggregate to county level
    county_df = location_df.groupby(['state', 'county'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Add FIPS codes for counties
    county_df = add_county_fips_mapping(county_df)
    
    return county_df


def add_county_fips_mapping(county_df):
    """
    Add FIPS codes for counties using the addfips library
    
    Parameters:
        county_df: DataFrame with 'state' and 'county' columns
    
    Returns:
        DataFrame with added 'county_fips' and 'combined_fips' columns
    """
    try:
        import addfips
        af = addfips.AddFIPS()
        
        county_df = county_df.copy()
        
        # Convert state abbreviations to full names and get FIPS
        fips_codes = []
        state_abbr_map = get_state_abbreviation_map()
        
        for idx, row in county_df.iterrows():
            state_abbr = row['state']
            county_name = row['county']
            
            # Clean county name (remove "County", "Parish", etc.)
            county_clean = clean_county_name(county_name)
            
            try:
                # Get county FIPS using addfips
                county_fips = af.get_county_fips(county_clean, state=state_abbr)
                fips_codes.append(county_fips)
            except:
                # Try with state full name
                state_full = state_abbr_map.get(state_abbr, state_abbr)
                try:
                    county_fips = af.get_county_fips(county_clean, state=state_full)
                    fips_codes.append(county_fips)
                except:
                    print(f"Could not find FIPS for: {county_name}, {state_abbr}")
                    fips_codes.append(None)
        
        county_df['county_fips'] = fips_codes
        
        # Remove rows with no FIPS code
        null_fips = county_df['county_fips'].isna().sum()
        if null_fips > 0:
            print(f"Warning: {null_fips} counties could not be matched to FIPS codes")
            county_df = county_df.dropna(subset=['county_fips'])
        
        # Ensure FIPS is integer for matching with TopoJSON
        county_df['county_fips'] = county_df['county_fips'].astype(int)
        county_df['combined_fips'] = county_df['county_fips'].astype(str).str.zfill(5)
        
        return county_df
        
    except ImportError:
        print("addfips library not found. Install with: pip install addfips")
        print("Using fallback method...")
        return add_county_fips_mapping_fallback(county_df)

def clean_county_name(county_name):
    """Clean county name to match FIPS lookup format"""
    # Remove common suffixes
    suffixes = [' County', ' Parish', ' Borough', ' Census Area', ' Municipality',
                ' City and Borough', ' City', ' County and City']
    
    county_clean = str(county_name)
    for suffix in suffixes:
        if county_clean.lower().endswith(suffix.lower()):
            county_clean = county_clean[:-len(suffix)]
            break
    
    # Special cases
    special_cases = {
        'DEKALB': 'DeKalb',
        'DU PAGE': 'DuPage',
        'LA SALLE': 'LaSalle',
        'MCLEAN': 'McLean',
        # Add more as needed
    }
    
    if county_clean.upper() in special_cases:
        county_clean = special_cases[county_clean.upper()]
    
    return county_clean.strip()

def get_state_abbreviation_map():
    """Get mapping of state abbreviations to full names"""
    return {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia',
        'AS': 'American Samoa', 'GU': 'Guam', 'MP': 'Northern Mariana Islands',
        'PR': 'Puerto Rico', 'VI': 'Virgin Islands'
    }

def add_county_fips_mapping_fallback(county_df):
    """
    Fallback method using census data if addfips is not available
    """
    county_df = county_df.copy()
    
    # URL for census county FIPS data
    fips_url = 'https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt'
    
    try:
        # Load census county FIPS data
        fips_df = pd.read_csv(fips_url, header=None, dtype=str)
        fips_df.columns = ['state_abbr', 'state_fips', 'county_fips', 'county_name', 'class_fips']
        
        # Create full FIPS (state_fips + county_fips)
        fips_df['full_fips'] = (fips_df['state_fips'] + fips_df['county_fips']).astype(int)
        
        # Create mapping dictionary
        county_df['county_upper'] = county_df['county'].str.upper().str.strip()
        fips_df['county_upper'] = fips_df['county_name'].str.upper().str.strip()
        
        # Merge to get FIPS codes
        merged = county_df.merge(
            fips_df[['state_abbr', 'county_upper', 'full_fips']],
            left_on=['state', 'county_upper'],
            right_on=['state_abbr', 'county_upper'],
            how='left'
        )
        
        county_df['county_fips'] = merged['full_fips']
        
        # Remove rows with no FIPS code
        null_fips = county_df['county_fips'].isna().sum()
        if null_fips > 0:
            print(f"Warning: {null_fips} counties could not be matched to FIPS codes")
            county_df = county_df.dropna(subset=['county_fips'])
        
        # Ensure integer type
        county_df['county_fips'] = county_df['county_fips'].astype(int)
        county_df['combined_fips'] = county_df['county_fips'].astype(str).str.zfill(5)
        
        # Drop temporary column
        county_df = county_df.drop('county_upper', axis=1)
        
        return county_df
        
    except Exception as e:
        print(f"Error loading FIPS data: {e}")
        print("Creating manual mapping for demonstration...")
        
        # Manual mapping for common counties as last resort
        manual_fips = create_manual_fips_mapping()
        
        county_df['county_fips'] = county_df.apply(
            lambda row: manual_fips.get((row['state'], row['county'].upper()), None),
            axis=1
        )
        
        null_fips = county_df['county_fips'].isna().sum()
        if null_fips > 0:
            print(f"Warning: {null_fips} counties could not be matched")
            print("Removing unmatched counties...")
            county_df = county_df.dropna(subset=['county_fips'])
        
        county_df['county_fips'] = county_df['county_fips'].astype(int)
        county_df['combined_fips'] = county_df['county_fips'].astype(str).str.zfill(5)
        
        return county_df

def create_manual_fips_mapping():
    """Create a small manual FIPS mapping as absolute last resort"""
    # This is just a starter - you'd need to expand this significantly
    return {
        ('TX', 'HARRIS'): 48201,
        ('CA', 'LOS ANGELES'): 6037,
        ('IL', 'COOK'): 17031,
        ('AZ', 'MARICOPA'): 4013,
        ('CA', 'SAN DIEGO'): 6073,
        ('CA', 'ORANGE'): 6059,
        ('FL', 'MIAMI-DADE'): 12086,
        ('TX', 'DALLAS'): 48113,
        ('WA', 'KING'): 53033,
        ('CA', 'SAN BERNARDINO'): 6071,
        # Add more as needed...
    }

def aggregate_by_chemical_county(df):
    """
    Get total waste by chemical per county
    
    Parameters:
        df: DataFrame from fetch_waste_data()
    
    Returns:
        DataFrame with chemical-county level aggregations
    """
    df = df.copy()
    
    # Aggregate to county-chemical level
    county_chemical_df = df.groupby(['state', 'county', 'tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum',
        'total_land_release': 'sum',
        'total_water_release': 'sum',
        'total_air_release': 'sum'
    })
    
    # Sort by total release descending
    county_chemical_df = county_chemical_df.sort_values('total_release', ascending=False).reset_index(drop=True)
    
    return county_chemical_df


def aggregate_boolean_indicators_by_county(df):
    """
    Get percentage of True occurrences per county for boolean indicators
    
    Parameters:
        df: DataFrame from fetch_waste_data() with chemical info joined
    
    Returns:
        DataFrame with county and percentage of True for each indicator
    """
    df = df.copy()
    
    # Deduplicate at chemical-location level
    # Each combination of county + chemical should be counted once for boolean indicators
    unique_chemicals_per_county = df.groupby(['state', 'county', 'tri_chem_id', 'chem_name']).first().reset_index()
    
    # Calculate percentages for each boolean indicator
    boolean_cols = ['caac_ind', 'carc_ind', 'feds_ind', 'pbt_ind', 'pfas_ind']
    
    result_dfs = []
    for col in boolean_cols:
        # Convert to boolean if needed
        unique_chemicals_per_county[col] = unique_chemicals_per_county[col].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        
        # Calculate percentage of True per county
        county_stats = unique_chemicals_per_county.groupby(['state', 'county'])[col].agg(['sum', 'count'])
        county_stats['percentage'] = (county_stats['sum'] / county_stats['count'] * 100).round(2)
        county_stats = county_stats[['percentage']].rename(columns={'percentage': f'pct_{col}'})
        result_dfs.append(county_stats)
    
    # Combine all indicators
    boolean_df = result_dfs[0]
    for df_bool in result_dfs[1:]:
        boolean_df = boolean_df.join(df_bool)
    
    boolean_df = boolean_df.reset_index()
    
    # Add FIPS codes
    boolean_df = add_county_fips_mapping(boolean_df)
    
    return boolean_df


def get_complete_county_analysis(df):
    """
    Combine all goals into a single comprehensive county-level DataFrame
    
    Returns:
        DataFrame with total waste, waste types, and boolean percentages per county
    """
    # Goal 1 & 2: Total waste by county
    waste_df = aggregate_by_county(df)
    
    # Goal 4: Boolean percentages by county
    boolean_df = aggregate_boolean_indicators_by_county(df)
    
    # Combine all
    complete_df = waste_df.merge(
        boolean_df, 
        on=['state', 'county'], 
        how='left'
    )
    
    return complete_df


def get_top_chemicals_by_county(df, state_abbr, county_name, top_n=10):
    """
    Get top chemicals for a specific county
    
    Parameters:
        df: DataFrame from fetch_waste_data()
        state_abbr: State abbreviation (e.g., 'TX', 'CA')
        county_name: County name (e.g., 'HARRIS', 'LOS ANGELES')
        top_n: Number of top chemicals to return
    
    Returns:
        DataFrame with top chemicals by total release for that county
    """
    df = df.copy()
    
    # Filter for specific state and county
    county_df = df[(df['state'] == state_abbr) & (df['county'] == county_name)].copy()
    
    if len(county_df) == 0:
        print(f"No data found for {county_name}, {state_abbr}")
        return pd.DataFrame()
    
    # Aggregate to chemical level
    chemical_totals = county_df.groupby(['tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Get top N
    top_chemicals = chemical_totals.nlargest(top_n, 'total_release')
    
    return top_chemicals


def get_top_counties_by_state(df, state_abbr, top_n=10):
    """
    Get top counties by total waste for a specific state
    
    Parameters:
        df: DataFrame from fetch_waste_data()
        state_abbr: State abbreviation (e.g., 'TX', 'CA')
        top_n: Number of top counties to return
    
    Returns:
        DataFrame with top counties by total release
    """
    df = df.copy()
    
    # Filter for state
    state_df = df[df['state'] == state_abbr].copy()
    
    if len(state_df) == 0:
        print(f"No data found for {state_abbr}")
        return pd.DataFrame()
    
    # Aggregate to location level first
    location_df = state_df.groupby(['state', 'county', 'city'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Then aggregate to county level
    county_totals = location_df.groupby(['state', 'county'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Get top N counties
    top_counties = county_totals.nlargest(top_n, 'total_release')
    
    return top_counties

def prepare_top_chemicals_per_county(df, county_df, top_n=8):
    """
    Pre-compute top chemicals for each county for dashboard visualization
    
    Parameters:
        df: DataFrame from fetch_waste_data()
        county_df: DataFrame from aggregate_by_county() (contains county_fips)
        top_n: Number of top chemicals per county
    
    Returns:
        DataFrame with top chemicals per county including 'Other Chemicals' category
    """
    df = df.copy()
    
    # Create a mapping for county FIPS codes
    county_info = county_df[['state', 'county', 'county_fips']].drop_duplicates()
    
    # Aggregate to county-chemical level
    county_chemical = df.groupby(['state', 'county', 'tri_chem_id', 'chem_name'], as_index=False).agg({
        'total_release': 'sum'
    })
    
    # Merge with county info to add county_fips
    county_chemical = county_chemical.merge(county_info, on=['state', 'county'], how='left')
    
    # Drop any rows where county_fips is NaN
    county_chemical = county_chemical.dropna(subset=['county_fips'])
    
    # Get top N chemicals per county
    top_chemicals_per_county = []
    
    for (state, county) in county_chemical[['state', 'county']].drop_duplicates().values:
        county_data = county_chemical[(county_chemical['state'] == state) & (county_chemical['county'] == county)].copy()
        
        # Ensure we have data for this county
        if len(county_data) == 0:
            continue
            
        top_n_county = county_data.nlargest(top_n, 'total_release')
        
        # Add "Other" category for remaining chemicals
        other_total = county_data[~county_data['chem_name'].isin(top_n_county['chem_name'])]['total_release'].sum()
        
        if other_total > 0:
            # Get county info for the other row
            county_info_rows = county_info[(county_info['state'] == state) & (county_info['county'] == county)]
            if len(county_info_rows) > 0:
                county_info_row = county_info_rows.iloc[0]
                other_row = pd.DataFrame({
                    'state': [state],
                    'county': [county],
                    'county_fips': [county_info_row['county_fips']],
                    'tri_chem_id': ['OTHER'],
                    'chem_name': ['Other Chemicals'],
                    'total_release': [other_total]
                })
                top_n_county = pd.concat([top_n_county, other_row], ignore_index=True)
        
        top_chemicals_per_county.append(top_n_county)
    
    # Combine all counties
    if top_chemicals_per_county:
        result_df = pd.concat(top_chemicals_per_county, ignore_index=True)
    else:
        result_df = pd.DataFrame(columns=['state', 'county', 'county_fips', 'tri_chem_id', 'chem_name', 'total_release'])
    
    return result_df

def inspect_county_data(county_df):
    """Print summary of county waste data"""
    print("County Waste Data Summary:")
    print("-" * 50)
    print(f"Number of counties: {len(county_df)}")
    print(f"\nColumns: {county_df.columns.tolist()}")
    print(f"\nSample data (top 10 counties by total release):")
    top_counties = county_df.nlargest(10, 'total_release')
    print(top_counties[['state', 'county', 'total_release', 'total_air_release', 
                         'total_water_release', 'total_land_release']].to_string(index=False))
    print(f"\nTotal release stats:")
    print(f"  Sum: {county_df['total_release'].sum():,.0f}")
    print(f"  Mean: {county_df['total_release'].mean():,.0f}")
    print(f"  Max: {county_df['total_release'].max():,.0f}")
    print(f"  Median: {county_df['total_release'].median():,.0f}")