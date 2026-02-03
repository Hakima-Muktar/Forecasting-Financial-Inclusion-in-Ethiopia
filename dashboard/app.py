"""
Financial Inclusion Dashboard for Ethiopia
Forecasting Access and Usage (2025-2027)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Add dashboard directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    load_unified_data, load_event_features, load_event_matrix, 
    load_forecasts, get_observations, get_events, 
    get_indicator_series, get_latest_value, get_forecast_value
)

# Page config
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Overview", "Data Coverage", "Trends", "Events & Impact", "Forecasts"]
)

# Load data
df_main, df_impact = load_unified_data()
observations = get_observations(df_main)
events = get_events(df_main)
event_features = load_event_features()
event_matrix = load_event_matrix()
forecast_long, forecast_wide = load_forecasts()

# Sidebar filters
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# Year range filter
if not observations.empty and 'year' in observations.columns:
    years = sorted(observations['year'].dropna().unique())
    if len(years) > 0:
        year_range = st.sidebar.slider(
            "Year Range",
            min_value=int(min(years)),
            max_value=2027,
            value=(int(min(years)), 2027)
        )
    else:
        year_range = (2014, 2027)
else:
    year_range = (2014, 2027)

# Scenario filter (for forecast page)
scenario_filter = st.sidebar.selectbox(
    "Forecast Scenario",
    ["base", "optimistic", "pessimistic"]
)

#############################################################################
# PAGE: OVERVIEW
#############################################################################
if page == "Overview":
    st.markdown('<p class="main-header">Ethiopia Financial Inclusion Dashboard</p>', unsafe_allow_html=True)
    st.markdown("**Forecasting Access and Usage (2025-2027)**")
    
    # KPI Cards
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        latest_access = get_latest_value(observations, 'ACC_OWNERSHIP')
        if latest_access:
            st.metric(
                "Latest Account Ownership",
                f"{latest_access:.1f}%",
                delta=None,
                help="Most recent Findex data"
            )
        else:
            st.metric("Latest Account Ownership", "N/A")
    
    with col2:
        latest_mm = get_latest_value(observations, 'ACC_MM_ACCOUNT')
        if latest_mm:
            st.metric(
                "Mobile Money Accounts",
                f"{latest_mm:.1f}%",
                delta=None
            )
        else:
            st.metric("Mobile Money Accounts", "N/A")
    
    with col3:
        latest_usage = get_latest_value(observations, 'USG_DIGITAL_PAYMENT')
        if latest_usage:
            st.metric(
                "Digital Payment Usage",
                f"{latest_usage:.1f}%",
                delta=None
            )
        else:
            st.metric("Digital Payment Usage", "N/A")
    
    with col4:
        forecast_2027 = get_forecast_value(forecast_long, 'ACC_OWNERSHIP', 2027, 'base')
        if forecast_2027:
            target_gap = 60 - forecast_2027
            st.metric(
                "2027 Forecast (Access)",
                f"{forecast_2027:.1f}%",
                delta=f"{-target_gap:.1f}pp to 60% target" if target_gap > 0 else "✓ Target met"
            )
        else:
            st.metric("2027 Forecast", "N/A")
    
    # Quick insights
    st.markdown("---")
    st.subheader("🔍 Key Insights")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**📊 Current State**")
        if latest_access and latest_mm:
            st.write(f"- Account ownership: {latest_access:.1f}%")
            st.write(f"- Mobile money penetration: {latest_mm:.1f}%")
            st.write(f"- Traditional banking dominates: {latest_access - latest_mm:.1f}pp gap")
        st.write(f"- Total events tracked: {len(events)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_b:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**🎯 Forecast Outlook**")
        if forecast_2027:
            st.write(f"- 2027 base forecast: {forecast_2027:.1f}%")
            if forecast_wide is not None and not forecast_wide.empty:
                access_2027 = forecast_wide[
                    (forecast_wide['year'] == 2027) & 
                    (forecast_wide['indicator_code'] == 'ACC_OWNERSHIP')
                ]
                if not access_2027.empty and 'lower' in access_2027.columns:
                    lower = access_2027['lower'].iloc[0]
                    upper = access_2027['upper'].iloc[0]
                    st.write(f"- Uncertainty range: {lower:.1f}% - {upper:.1f}%")
        st.write("- Key drivers: Telebirr, M-Pesa, NFIS-II")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick trend chart
    st.markdown("---")
    st.subheader("📉 Historical Trend + Forecast")
    
    if not observations.empty:
        acc_series = get_indicator_series(observations, 'ACC_OWNERSHIP')
        
        fig = go.Figure()
        
        # Historical
        if not acc_series.empty:
            fig.add_trace(go.Scatter(
                x=acc_series['observation_date'],
                y=acc_series['value_numeric'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10)
            ))
        
        # Forecast
        if forecast_long is not None:
            forecast_access = forecast_long[
                (forecast_long['indicator_code'] == 'ACC_OWNERSHIP') &
                (forecast_long['scenario'] == scenario_filter)
            ].sort_values('year')
            
            if not forecast_access.empty:
                forecast_dates = pd.to_datetime(forecast_access['year'].astype(str) + '-01-01')
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=forecast_access['forecast_value'],
                    mode='lines+markers',
                    name=f'Forecast ({scenario_filter})',
                    line=dict(color='#ff7f0e', width=2, dash='dash'),
                    marker=dict(size=8, symbol='triangle-up')
                ))
        
        fig.update_layout(
            title="Account Ownership: Historical + Forecast",
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

#############################################################################
# PAGE: DATA COVERAGE
#############################################################################
elif page == "Data Coverage":
    st.markdown('<p class="main-header">Data Coverage & Quality</p>', unsafe_allow_html=True)
    
    # Dataset summary
    st.subheader("📋 Dataset Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_obs = len(observations)
        st.metric("Total Observations", f"{n_obs:,}")
    
    with col2:
        n_events = len(events)
        st.metric("Total Events", f"{n_events:,}")
    
    with col3:
        n_impact = len(df_impact) if not df_impact.empty else 0
        st.metric("Impact Links", f"{n_impact:,}")
    
    # Coverage by indicator
    st.markdown("---")
    st.subheader("📊 Indicator Coverage Over Time")
    
    if not observations.empty and 'year' in observations.columns:
        # Create coverage matrix
        coverage = observations.pivot_table(
            index='indicator_code',
            columns='year',
            values='value_numeric',
            aggfunc='count',
            fill_value=0
        )
        
        # Heatmap
        fig = px.imshow(
            coverage,
            labels=dict(x="Year", y="Indicator", color="Count"),
            color_continuous_scale="Blues",
            aspect="auto"
        )
        fig.update_layout(
            title="Data Availability Heatmap",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Table view
        with st.expander("📄 View Coverage Table"):
            st.dataframe(coverage, use_container_width=True)
    else:
        st.info("No observation data available")
    
    # Event coverage
    st.markdown("---")
    st.subheader("📅 Event Coverage")
    
    if not events.empty:
        col_a, col_b = st.columns(2)
        
        with col_a:
            if 'category' in events.columns:
                category_counts = events['category'].value_counts()
                fig = px.bar(
                    x=category_counts.index,
                    y=category_counts.values,
                    labels={'x': 'Category', 'y': 'Count'},
                    title="Events by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            if 'event_date_parsed' in events.columns:
                events_with_dates = events['event_date_parsed'].notna().sum()
                events_without_dates = events['event_date_parsed'].isna().sum()
                
                fig = px.pie(
                    values=[events_with_dates, events_without_dates],
                    names=['With Date', 'Without Date'],
                    title="Event Date Availability"
                )
                st.plotly_chart(fig, use_container_width=True)

#############################################################################
# PAGE: TRENDS
#############################################################################
elif page == "Trends":
    st.markdown('<p class="main-header">Financial Inclusion Trends</p>', unsafe_allow_html=True)
    
    # Indicator selector
    available_indicators = observations['indicator_code'].unique().tolist() if not observations.empty else []
    
    selected_indicators = st.multiselect(
        "Select Indicators to Display",
        options=available_indicators,
        default=['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT'] if 'ACC_OWNERSHIP' in available_indicators else available_indicators[:2]
    )
    
    if selected_indicators and not observations.empty:
        fig = go.Figure()
        
        for indicator in selected_indicators:
            series = get_indicator_series(observations, indicator)
            if not series.empty:
                fig.add_trace(go.Scatter(
                    x=series['observation_date'],
                    y=series['value_numeric'],
                    mode='lines+markers',
                    name=indicator,
                    line=dict(width=2),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title="Indicator Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Value (%)",
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("📄 View Data Table"):
            for indicator in selected_indicators:
                series = get_indicator_series(observations, indicator)
                if not series.empty:
                    st.subheader(indicator)
                    display_cols = ['observation_date', 'value_numeric', 'year']
                    display_cols = [c for c in display_cols if c in series.columns]
                    st.dataframe(series[display_cols], use_container_width=True)
    else:
        st.info("Select indicators to display trends")

#############################################################################
# PAGE: EVENTS & IMPACT
#############################################################################
elif page == "Events & Impact":
    st.markdown('<p class="main-header">Events & Impact Analysis</p>', unsafe_allow_html=True)
    
    # Event timeline
    st.subheader("📅 Event Timeline")
    
    if not events.empty and 'event_date_parsed' in events.columns:
        events_with_dates = events[events['event_date_parsed'].notna()].copy()
        
        if not events_with_dates.empty:
            # Category filter
            categories = events_with_dates['category'].unique().tolist() if 'category' in events_with_dates.columns else []
            selected_categories = st.multiselect(
                "Filter by Category",
                options=categories,
                default=categories
            )
            
            filtered_events = events_with_dates[events_with_dates['category'].isin(selected_categories)] if selected_categories else events_with_dates
            
            # Timeline chart
            fig = px.scatter(
                filtered_events,
                x='event_date_parsed',
                y='category' if 'category' in filtered_events.columns else 'indicator',
                color='category' if 'category' in filtered_events.columns else None,
                hover_data=['indicator'],
                title="Event Timeline",
                labels={'event_date_parsed': 'Date', 'category': 'Category'}
            )
            fig.update_traces(marker=dict(size=12))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Event list
            with st.expander("📋 View Event List"):
                display_cols = ['indicator', 'category', 'event_date_parsed']
                display_cols = [c for c in display_cols if c in filtered_events.columns]
                st.dataframe(filtered_events[display_cols].sort_values('event_date_parsed', ascending=False), use_container_width=True)
        else:
            st.warning("No events with valid dates found")
    else:
        st.warning("No event data available")
    
    # Event-Indicator Matrix
    st.markdown("---")
    st.subheader("🔗 Event-Indicator Impact Matrix")
    
    if event_matrix is not None:
        fig = px.imshow(
            event_matrix,
            labels=dict(x="Indicator/Pillar", y="Event", color="Impact Weight"),
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            aspect="auto"
        )
        fig.update_layout(
            title="Event Impact Weights by Indicator",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📄 View Matrix Data"):
            st.dataframe(event_matrix, use_container_width=True)
    else:
        st.info("Event matrix not available. Run Task 3 notebook to generate.")
    
    # Event effects over time
    if event_features is not None:
        st.markdown("---")
        st.subheader("📈 Cumulative Event Effects Over Time")
        
        fig = go.Figure()
        
        effect_cols = [c for c in event_features.columns if 'event_effect' in c]
        for col in effect_cols[:4]:  # Limit to 4 for readability
            fig.add_trace(go.Scatter(
                x=event_features.index,
                y=event_features[col],
                mode='lines',
                name=col.replace('event_effect_', ''),
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Event Effects Timeline",
            xaxis_title="Date",
            yaxis_title="Cumulative Effect",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

#############################################################################
# PAGE: FORECASTS
#############################################################################
elif page == "Forecasts":
    st.markdown('<p class="main-header">Financial Inclusion Forecasts (2025-2027)</p>', unsafe_allow_html=True)
    
    if forecast_long is None:
        st.error("Forecast data not available. Run Task 4 notebook to generate forecasts.")
    else:
        # Scenario comparison
        st.subheader("📊 Scenario Comparison")
        
        # Indicator selector
        available_forecast_indicators = forecast_long['indicator_code'].unique().tolist()
        selected_forecast_indicator = st.selectbox(
            "Select Indicator",
            options=available_forecast_indicators,
            index=0 if available_forecast_indicators else None
        )
        
        if selected_forecast_indicator:
            # Get historical data
            historical = get_indicator_series(observations, selected_forecast_indicator)
            
            # Get forecast data
            forecast_data = forecast_long[forecast_long['indicator_code'] == selected_forecast_indicator]
            
            # Plot
            fig = go.Figure()
            
            # Historical
            if not historical.empty:
                fig.add_trace(go.Scatter(
                    x=historical['observation_date'],
                    y=historical['value_numeric'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10)
                ))
            
            # Forecasts by scenario
            colors = {'base': '#ff7f0e', 'optimistic': '#2ca02c', 'pessimistic': '#d62728'}
            for scenario in ['base', 'optimistic', 'pessimistic']:
                scenario_data = forecast_data[forecast_data['scenario'] == scenario].sort_values('year')
                if not scenario_data.empty:
                    forecast_dates = pd.to_datetime(scenario_data['year'].astype(str) + '-01-01')
                    fig.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=scenario_data['forecast_value'],
                        mode='lines+markers',
                        name=scenario.capitalize(),
                        line=dict(color=colors.get(scenario, '#999'), width=2, dash='dash'),
                        marker=dict(size=8, symbol='triangle-up')
                    ))
            
            # Uncertainty band
            if forecast_wide is not None:
                wide_data = forecast_wide[forecast_wide['indicator_code'] == selected_forecast_indicator].sort_values('year')
                if not wide_data.empty and 'lower' in wide_data.columns and 'upper' in wide_data.columns:
                    forecast_dates = pd.to_datetime(wide_data['year'].astype(str) + '-01-01')
                    fig.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=wide_data['upper'],
                        mode='lines',
                        name='Upper Bound',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=wide_data['lower'],
                        mode='lines',
                        name='Uncertainty Band',
                        line=dict(width=0),
                        fillcolor='rgba(68, 68, 68, 0.2)',
                        fill='tonexty'
                    ))
            
            fig.update_layout(
                title=f"{selected_forecast_indicator}: Historical + Forecast Scenarios",
                xaxis_title="Year",
                yaxis_title="Percentage (%)",
                hovermode='x unified',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Forecast table
        st.markdown("---")
        st.subheader("📋 Forecast Data Table")
        
        if forecast_wide is not None:
            st.dataframe(forecast_wide, use_container_width=True)
        else:
            st.dataframe(forecast_long, use_container_width=True)
        
        # Download button
        st.markdown("---")
        st.subheader("💾 Download Forecasts")
        
        csv = forecast_long.to_csv(index=False)
        st.download_button(
            label="Download Forecast CSV",
            data=csv,
            file_name="ethiopia_fi_forecast_2025_2027.csv",
            mime="text/csv"
        )
        
        # Key findings
        st.markdown("---")
        st.subheader("🔍 Key Findings")
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Forecast Interpretation**")
        
        # Access forecast
        access_2027_base = get_forecast_value(forecast_long, 'ACC_OWNERSHIP', 2027, 'base')
        if access_2027_base:
            st.write(f"- **Account Ownership 2027 (base)**: {access_2027_base:.1f}%")
            gap_to_60 = 60 - access_2027_base
            if gap_to_60 > 0:
                st.write(f"  - Gap to 60% target: {gap_to_60:.1f}pp")
            else:
                st.write("  - ✓ On track to meet 60% target")
        
        # Usage forecast
        usage_2027_base = get_forecast_value(forecast_long, 'USG_DIGITAL_PAYMENT', 2027, 'base')
        if usage_2027_base:
            st.write(f"- **Digital Payment Usage 2027 (base)**: {usage_2027_base:.1f}%")
        
        st.write("\n**Key Drivers:**")
        st.write("- Telebirr expansion (54M+ users)")
        st.write("- M-Pesa Ethiopia + EthSwitch integration")
        st.write("- NFIS-II policy implementation")
        st.write("- Fayda Digital ID rollout")
        
        st.write("\n**Risks & Uncertainties:**")
        st.write("- Survey methodology vs operator data discrepancy")
        st.write("- Account overlap (multiple accounts per person)")
        st.write("- Cash culture and trust barriers")
        st.write("- Affordability constraints")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Ethiopia Financial Inclusion Dashboard | Data: World Bank Findex, NBE, Operator Reports | 
    Forecasts: 2025-2027
    </div>
    """,
    unsafe_allow_html=True
)