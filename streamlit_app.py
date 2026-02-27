import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(page_title="EV vs Petrol Analytics Dashboard", layout="wide")

# Title and description
st.title("🚗 EV vs Petrol Vehicle Sales Analytics Dashboard")
st.markdown("**Comprehensive visualization of Electric Vehicles vs Combustion Engine Vehicles across regions**")
st.markdown("---")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv('ev_vs_petrol_dataset_v3.csv')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
selected_countries = st.sidebar.multiselect(
    "Select Countries", 
    sorted(df['country'].unique()),
    default=sorted(df['country'].unique())[:5]
)
selected_years = st.sidebar.slider(
    "Select Year Range",
    int(df['year'].min()),
    int(df['year'].max()),
    (int(df['year'].min()), int(df['year'].max()))
)

# Filter data based on selections
filtered_df = df[(df['country'].isin(selected_countries)) & 
                  (df['year'] >= selected_years[0]) & 
                  (df['year'] <= selected_years[1])]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Data Points: {len(filtered_df)}")

# ============= CHART 1: EV vs Petrol Sales Over Time (Line Chart) =============
st.subheader("📈 Chart 1: EV vs Petrol Sales Trend Over Time")
sales_by_year = filtered_df.groupby('year')[['ev_sales', 'petrol_car_sales']].sum().reset_index()
fig1 = px.line(sales_by_year, x='year', y=['ev_sales', 'petrol_car_sales'],
               labels={'year': 'Year', 'value': 'Sales Count', 'variable': 'Vehicle Type'},
               title='EV Sales vs Petrol Car Sales Growth',
               markers=True)
fig1.update_layout(hovermode='x unified', height=400)
st.plotly_chart(fig1, use_container_width=True)

# ============= CHART 2: Market Share Comparison (Bar Chart) =============
st.subheader("📊 Chart 2: EV Market Share by Country")
market_share_by_country = filtered_df.groupby('country')[['ev_sales', 'petrol_car_sales', 'diesel_car_sales']].sum()
market_share_by_country['total'] = market_share_by_country.sum(axis=1)
market_share_by_country['ev_share'] = (market_share_by_country['ev_sales'] / market_share_by_country['total'] * 100).round(2)
market_share_by_country = market_share_by_country.reset_index().sort_values('ev_share', ascending=False).head(15)

fig2 = px.bar(market_share_by_country, x='country', y='ev_share',
              labels={'country': 'Country', 'ev_share': 'EV Market Share (%)'},
              title='Top 15 Countries by EV Market Share',
              color='ev_share', color_continuous_scale='Viridis')
fig2.update_layout(height=450, xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# ============= CHART 3: EV vs Petrol Distribution (Pie Chart) =============
st.subheader("📍 Chart 3: Overall Vehicle Type Distribution (Latest Year)")
latest_year = filtered_df['year'].max()
latest_data = filtered_df[filtered_df['year'] == latest_year]
vehicle_dist = pd.DataFrame({
    'Vehicle Type': ['EV', 'Petrol', 'Diesel'],
    'Sales': [latest_data['ev_sales'].sum(), latest_data['petrol_car_sales'].sum(), latest_data['diesel_car_sales'].sum()]
})

col1, col2 = st.columns(2)
with col1:
    fig3 = px.pie(vehicle_dist, values='Sales', names='Vehicle Type',
                  title=f'Vehicle Type Distribution ({latest_year})',
                  color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

# ============= CHART 4: Regional Sales Trend (Area Chart) =============
with col2:
    st.subheader("📍 Chart 4: EV Sales by Region (Stacked Area)")
    regional_sales = filtered_df.groupby(['year', 'region'])['ev_sales'].sum().reset_index()
    fig4 = px.area(regional_sales, x='year', y='ev_sales', color='region',
                   title='EV Sales Trend by Region',
                   labels={'year': 'Year', 'ev_sales': 'EV Sales', 'region': 'Region'})
    fig4.update_layout(height=450)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ============= CHART 5: EV Growth Rate Scatter Plot =============
st.subheader("🔝 Chart 5: EV Growth Rate vs Time")
growth_data = filtered_df[['year', 'ev_growth_rate_yoy', 'country']].copy()

fig5 = px.scatter(growth_data, x='year', y='ev_growth_rate_yoy', 
                  color='country', 
                  title='EV Growth Rate (YoY) Across Countries',
                  labels={'year': 'Year', 'ev_growth_rate_yoy': 'Growth Rate (%)'},
                  height=450)
st.plotly_chart(fig5, use_container_width=True)

# ============= CHART 6: GDP vs EV Market Share (Scatter Plot) =============
st.subheader("💰 Chart 6: GDP Per Capita vs EV Market Share")
gdp_ev_data = filtered_df[filtered_df['year'] == latest_year].drop_duplicates('country')
gdp_ev_data['ev_market_share_pct'] = gdp_ev_data['ev_market_share'] * 100

fig6 = px.scatter(gdp_ev_data, x='gdp_per_capita', y='ev_market_share_pct',
                  size='charging_stations', color='region',
                  hover_data=['country', 'charging_stations'],
                  title='GDP Per Capita vs EV Market Share (Latest Year)',
                  labels={'gdp_per_capita': 'GDP Per Capita (USD)', 
                          'ev_market_share_pct': 'EV Market Share (%)'},
                  height=450)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

# ============= CHART 7: CO2 Emissions Trend (Line Chart) =============
with col1:
    st.subheader("🌍 Chart 7: CO2 Emissions Trend (Transport)")
    emissions_data = filtered_df.groupby('year')['co2_emissions_transport_mt'].mean().reset_index()
    fig7 = px.line(emissions_data, x='year', y='co2_emissions_transport_mt',
                   markers=True, title='Average CO2 Transport Emissions Over Time',
                   labels={'year': 'Year', 'co2_emissions_transport_mt': 'CO2 (MT)'},
                   color_discrete_sequence=['#FF6B6B'])
    fig7.update_layout(height=450)
    st.plotly_chart(fig7, use_container_width=True)

# ============= CHART 8: Charging Stations Growth (Bar/Histogram) =============
with col2:
    st.subheader("🔌 Chart 8: Charging Stations Expansion")
    charging_data = filtered_df.groupby('year')['charging_stations'].mean().reset_index()
    fig8 = px.bar(charging_data, x='year', y='charging_stations',
                  title='Average Charging Stations Growth',
                  labels={'year': 'Year', 'charging_stations': 'Avg Charging Stations'},
                  color='charging_stations', color_continuous_scale='Blues')
    fig8.update_layout(height=450)
    st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# ============= CHART 9: EV Range Improvement (Box Plot) =============
st.subheader("🔋 Chart 9: EV Range Distribution by Region (Latest Year)")
range_data = filtered_df[filtered_df['year'] == latest_year]
fig9 = px.box(range_data, x='region', y='avg_ev_range_km',
              title='EV Driving Range Distribution by Region',
              labels={'region': 'Region', 'avg_ev_range_km': 'Average EV Range (km)'},
              color='region', height=450)
st.plotly_chart(fig9, use_container_width=True)

st.markdown("---")

# ============= CHART 10: Heatmap - EV Market Share by Country & Year =============
st.subheader("🔥 Chart 10: EV Market Share Heatmap (Country × Year)")
heatmap_data = filtered_df.groupby(['country', 'year'])['ev_market_share'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='country', columns='year', values='ev_market_share')

fig10 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values * 100,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='YlOrRd',
    colorbar=dict(title='EV Market<br>Share (%)')
))
fig10.update_layout(
    title='EV Market Share Heatmap: Country × Year',
    xaxis_title='Year',
    yaxis_title='Country',
    height=600,
    yaxis={'autorange': 'reversed'}
)
st.plotly_chart(fig10, use_container_width=True)

st.markdown("---")

# Summary Statistics
st.subheader("📊 Key Metrics Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_ev = filtered_df['ev_sales'].sum()
    st.metric("Total EV Sales", f"{total_ev:,.0f}", delta="Latest Period")

with col2:
    total_petrol = filtered_df['petrol_car_sales'].sum()
    st.metric("Total Petrol Sales", f"{total_petrol:,.0f}", delta="Latest Period")

with col3:
    avg_ev_share = filtered_df['ev_market_share'].mean() * 100
    st.metric("Avg EV Market Share", f"{avg_ev_share:.2f}%", delta="+Growth")

with col4:
    total_charging = filtered_df['charging_stations'].max()
    st.metric("Max Charging Stations", f"{total_charging:,.0f}", delta="Peak Year")

# Data Table
with st.expander("📋 View Raw Data"):
    st.dataframe(filtered_df.sort_values('year', ascending=False), use_container_width=True)

st.markdown("---")
st.caption("🔬 Data Visualization Dashboard | EV vs Petrol Market Analysis | Updated: 2025")
