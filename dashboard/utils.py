"""
Data loading and utility functions for the dashboard.
"""
import pandas as pd
import streamlit as st
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_RAW = BASE_DIR / 'data' / 'raw'
DATA_PROCESSED = BASE_DIR / 'data' / 'processed'
REPORTS_FIGURES = BASE_DIR / 'reports' / 'figures'


@st.cache_data
def load_unified_data():
    """Load unified dataset - prefer enriched CSV from Task 1, fallback to Excel."""
    try:
        enriched_path = DATA_PROCESSED / 'ethiopia_fi_unified_data_enriched.csv'
        excel_path = DATA_RAW / 'ethiopia_fi_unified_data.xlsx'
        
        # Try enriched dataset first (includes Additional Data Points Guide indicators)
        if enriched_path.exists():
            df_main = pd.read_csv(enriched_path)
            # Extract impact links from enriched data
            df_impact = df_main[df_main['record_type'] == 'impact_link'].copy()
        else:
            # Fallback to raw Excel
            df_main = pd.read_excel(excel_path, sheet_name='ethiopia_fi_unified_data')
            try:
                df_impact = pd.read_excel(excel_path, sheet_name='Impact_sheet')
            except:
                df_impact = pd.DataFrame()
        
        # Parse dates
        if 'observation_date' in df_main.columns:
            df_main['observation_date'] = pd.to_datetime(
                df_main['observation_date'], 
                format='mixed', 
                errors='coerce'
            )
        
        return df_main, df_impact
    except Exception as e:
        st.error(f"Error loading unified data: {e}")
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def load_event_features():
    """Load event features from Task 3."""
    try:
        path = DATA_PROCESSED / 'event_features.csv'
        if not path.exists():
            st.warning("Event features not found. Run Task 3 notebook first.")
            return None
        
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df
    except Exception as e:
        st.error(f"Error loading event features: {e}")
        return None


@st.cache_data
def load_event_matrix():
    """Load event-indicator matrix from Task 3."""
    try:
        path = DATA_PROCESSED / 'event_indicator_matrix.csv'
        if not path.exists():
            st.warning("Event matrix not found. Run Task 3 notebook first.")
            return None
        
        df = pd.read_csv(path, index_col=[0, 1])
        return df
    except Exception as e:
        st.error(f"Error loading event matrix: {e}")
        return None


@st.cache_data
def load_forecasts():
    """Load forecast data from Task 4."""
    try:
        path_long = DATA_PROCESSED / 'forecast_2025_2027.csv'
        path_wide = DATA_PROCESSED / 'forecast_2025_2027_wide.csv'
        
        if not path_long.exists():
            st.warning("Forecast data not found. Run Task 4 notebook first.")
            return None, None
        
        df_long = pd.read_csv(path_long)
        df_wide = pd.read_csv(path_wide) if path_wide.exists() else None
        
        return df_long, df_wide
    except Exception as e:
        st.error(f"Error loading forecasts: {e}")
        return None, None


def get_observations(df_main):
    """Extract observations from unified data."""
    if df_main.empty:
        return pd.DataFrame()
    
    obs = df_main[df_main['record_type'] == 'observation'].copy()
    
    if 'observation_date' in obs.columns:
        obs['year'] = obs['observation_date'].dt.year
    
    return obs


def get_events(df_main):
    """Extract events from unified data."""
    if df_main.empty:
        return pd.DataFrame()
    
    events = df_main[df_main['record_type'] == 'event'].copy()
    
    # Determine date column
    if 'event_date' in events.columns and events['event_date'].notna().any():
        date_col = 'event_date'
    else:
        date_col = 'observation_date'
    
    if date_col in events.columns:
        events[date_col] = pd.to_datetime(events[date_col], format='mixed', errors='coerce')
        events['event_date_parsed'] = events[date_col]
    
    return events


def get_indicator_series(observations, indicator_code):
    """Get time series for a specific indicator."""
    if observations.empty:
        return pd.DataFrame()
    
    data = observations[observations['indicator_code'] == indicator_code].copy()
    data = data.dropna(subset=['observation_date', 'value_numeric'])
    data = data.sort_values('observation_date')
    
    return data


def get_latest_value(observations, indicator_code):
    """Get latest value for an indicator."""
    series = get_indicator_series(observations, indicator_code)
    if series.empty:
        return None
    return series['value_numeric'].iloc[-1]


def get_forecast_value(forecast_df, indicator, year, scenario='base'):
    """Get forecast value for specific indicator/year/scenario."""
    if forecast_df is None or forecast_df.empty:
        return None
    
    mask = (
        (forecast_df['indicator_code'] == indicator) &
        (forecast_df['year'] == year) &
        (forecast_df['scenario'] == scenario)
    )
    
    result = forecast_df[mask]
    if result.empty:
        return None
    
    return result['forecast_value'].iloc[0]