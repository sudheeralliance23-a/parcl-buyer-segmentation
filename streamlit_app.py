import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Parcl Buyer Intelligence", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('final_segmented_clients.csv')
    return df

df = load_data()

st.title("Buyer Segmentation & Investment Profiling Dashboard")

st.sidebar.header("Filters")
country_filter = st.sidebar.multiselect("Country", options=sorted(df['country'].unique()), default=None)
region_filter = st.sidebar.multiselect("Region", options=sorted(df['region'].unique()), default=None)
purpose_filter = st.sidebar.multiselect("Acquisition Purpose", options=sorted(df['acquisition_purpose'].unique()), default=None)
type_filter = st.sidebar.multiselect("Client Type", options=sorted(df['client_type'].unique()), default=None)

filtered = df.copy()
if country_filter:
    filtered = filtered[filtered['country'].isin(country_filter)]
if region_filter:
    filtered = filtered[filtered['region'].isin(region_filter)]
if purpose_filter:
    filtered = filtered[filtered['acquisition_purpose'].isin(purpose_filter)]
if type_filter:
    filtered = filtered[filtered['client_type'].isin(type_filter)]

tab1, tab2, tab3, tab4 = st.tabs([
    "Buyer Segmentation Overview",
    "Investor Behavior Dashboard",
    "Geographic Buyer Analysis",
    "Segment Insights Panel"
])

with tab1:
    st.subheader("Cluster Distribution")
    col1, col2 = st.columns(2)
    with col1:
        seg_counts = filtered['buyer_segment'].value_counts().reset_index()
        seg_counts.columns = ['buyer_segment', 'count']
        fig = px.pie(seg_counts, names='buyer_segment', values='count', title='Buyer Segment Share')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(seg_counts, x='buyer_segment', y='count', title='Clients per Segment')
        st.plotly_chart(fig2, use_container_width=True)
    st.metric("Total Clients (filtered)", len(filtered))

with tab2:
    st.subheader("Investment Patterns by Cluster")
    fig3 = px.box(filtered, x='buyer_segment', y='total_spend', title='Total Spend Distribution by Segment')
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.bar(
        filtered.groupby('buyer_segment')['loan_applied'].apply(lambda x: (x == 'Yes').mean() * 100).reset_index(name='loan_pct'),
        x='buyer_segment', y='loan_pct', title='% Clients Who Applied for Loan by Segment'
    )
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.scatter(filtered, x='age', y='total_spend', color='buyer_segment',
                       title='Age vs Total Spend by Segment', hover_data=['client_id'])
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.subheader("Buyer Segments by Region")
    geo_summary = filtered.groupby(['country', 'buyer_segment']).size().reset_index(name='count')
    fig6 = px.bar(geo_summary, x='country', y='count', color='buyer_segment', title='Segment Distribution by Country', barmode='stack')
    st.plotly_chart(fig6, use_container_width=True)

    region_summary = filtered.groupby(['region', 'buyer_segment']).size().reset_index(name='count')
    fig7 = px.bar(region_summary, x='region', y='count', color='buyer_segment', title='Segment Distribution by Region', barmode='stack')
    st.plotly_chart(fig7, use_container_width=True)

with tab4:
    st.subheader("Descriptive Statistics per Segment")
    stats = filtered.groupby('buyer_segment').agg(
        num_clients=('client_id', 'count'),
        avg_age=('age', 'mean'),
        avg_satisfaction=('satisfaction_score', 'mean'),
        avg_total_spend=('total_spend', 'mean'),
        avg_units_bought=('total_units_bought', 'mean'),
        pct_investment_purpose=('acquisition_purpose', lambda x: (x == 'Investment').mean() * 100),
        pct_loan_applied=('loan_applied', lambda x: (x == 'Yes').mean() * 100),
    ).reset_index()
    st.dataframe(stats, use_container_width=True)

    st.subheader("Raw Filtered Data")
    st.dataframe(filtered, use_container_width=True)
