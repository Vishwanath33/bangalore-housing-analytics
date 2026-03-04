import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="Bangalore Housing Analytics",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2rem; font-weight: bold; color: #1f77b4;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('bangalore_cleaned.csv')
    return df

df = load_data()

# Header
st.markdown('<p class="main-header">🏠 Bangalore Housing Analytics Dashboard</p>', 
            unsafe_allow_html=True)
st.markdown("*Interactive analysis of 13,000+ Bangalore properties*")
st.divider()

# Sidebar
st.sidebar.header("🔍 Filters")

# BHK filter
bhk_options = sorted(df['bhk'].unique())
selected_bhk = st.sidebar.multiselect(
    "BHK Type",
    options=bhk_options,
    default=[2, 3]
)

# Price range
min_p, max_p = int(df['price'].min()), int(df['price'].max())
price_range = st.sidebar.slider(
    "Price Range (Lakhs ₹)",
    min_value=min_p,
    max_value=min(500, max_p),
    value=(min_p, 200)
)

# Location filter
top_locations = df['location'].value_counts().head(30).index.tolist()
selected_locations = st.sidebar.multiselect(
    "Locations (Top 30)",
    options=top_locations,
    default=top_locations[:10]
)

# Area type
area_types = df['area_type'].unique().tolist()
selected_area = st.sidebar.multiselect(
    "Area Type",
    options=area_types,
    default=area_types
)

# Apply filters
filtered = df[
    (df['bhk'].isin(selected_bhk)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1]) &
    (df['location'].isin(selected_locations)) &
    (df['area_type'].isin(selected_area))
]

# Metrics row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🏘️ Properties", f"{len(filtered):,}")
col2.metric("💰 Avg Price", f"₹{filtered['price'].mean():.1f}L")
col3.metric("📐 Avg Sqft", f"{filtered['total_sqft'].mean():.0f}")
col4.metric("💎 Avg Price/Sqft", f"₹{filtered['price_per_sqft'].mean():.0f}")
col5.metric("📍 Locations", f"{filtered['location'].nunique()}")

st.divider()

# Row 1: Two charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Price Distribution")
    fig1 = px.histogram(
        filtered, x='price', nbins=40,
        color_discrete_sequence=['#1f77b4'],
        labels={'price': 'Price (Lakhs ₹)', 'count': 'Number of Properties'}
    )
    fig1.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏠 BHK Distribution")
    bhk_counts = filtered['bhk'].value_counts().sort_index()
    fig2 = px.bar(
        x=bhk_counts.index,
        y=bhk_counts.values,
        color=bhk_counts.values,
        color_continuous_scale='Blues',
        labels={'x': 'BHK', 'y': 'Count'}
    )
    fig2.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Scatter + Location bar
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Price vs Size")
    fig3 = px.scatter(
        filtered.sample(min(1000, len(filtered))),
        x='total_sqft', y='price',
        color='bhk',
        opacity=0.6,
        labels={'total_sqft': 'Total Sqft', 'price': 'Price (Lakhs ₹)', 'bhk': 'BHK'},
        color_continuous_scale='Viridis'
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🗺️ Top 10 Locations by Avg Price")
    loc_price = (filtered.groupby('location')['price']
                 .mean()
                 .sort_values(ascending=True)
                 .tail(10))
    fig4 = px.bar(
        x=loc_price.values,
        y=loc_price.index,
        orientation='h',
        color=loc_price.values,
        color_continuous_scale='Blues',
        labels={'x': 'Avg Price (Lakhs ₹)', 'y': 'Location'}
    )
    fig4.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Price per sqft heatmap by BHK
st.subheader("💡 Price per Sqft by BHK and Area Type")
if len(filtered) > 0:
    pivot = filtered.groupby(['bhk', 'area_type'])['price_per_sqft'].mean().unstack(fill_value=0)
    fig5 = px.imshow(
        pivot,
        color_continuous_scale='Blues',
        labels={'color': 'Avg Price/Sqft (₹)'},
        aspect='auto'
    )
    fig5.update_layout(height=300)
    st.plotly_chart(fig5, use_container_width=True)

# Data table
st.subheader("📋 Filtered Data")
st.caption(f"Showing {min(50, len(filtered))} of {len(filtered):,} filtered properties")
display_cols = ['location', 'bhk', 'total_sqft', 'bath', 'balcony', 'price', 'price_per_sqft', 'area_type']
st.dataframe(
    filtered[display_cols].sort_values('price').head(50),
    use_container_width=True
)

# Footer
st.divider()
st.caption("Data source: Kaggle Bangalore House Price Dataset | Built with Streamlit & Plotly")
