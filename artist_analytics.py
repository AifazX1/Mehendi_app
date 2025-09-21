import streamlit as st
from datetime import datetime, date, timedelta
from database import get_db_connection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def artist_analytics_dashboard(username):
    """Comprehensive analytics dashboard for artists"""
    st.subheader("📊 Analytics Dashboard")

    # Key Performance Indicators
    display_kpi_metrics(username)

    # Analytics tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Performance", "💰 Revenue", "👥 Customers", "🎨 Services", "📅 Trends"
    ])

    with tab1:
        try:
            display_performance_analytics(username)
        except Exception as e:
            st.error(f"Error in Performance Analytics: {e}")

    with tab2:
        try:
            display_revenue_analytics(username)
        except Exception as e:
            st.error(f"Error in Revenue Analytics: {e}")

    with tab3:
        try:
            display_customer_analytics(username)
        except Exception as e:
            st.error(f"Error in Customer Analytics: {e}")

    with tab4:
        try:
            display_service_analytics(username)
        except Exception as e:
            st.error(f"Error in Service Analytics: {e}")

    with tab5:
        try:
            display_trend_analytics(username)
        except Exception as e:
            st.error(f"Error in Trend Analytics: {e}")

# ---------------- KPI Metrics ----------------
def display_kpi_metrics(username):
    """Display key performance indicators"""
    st.subheader("🎯 Key Performance Indicators")
    kpi_data = get_kpi_data(username)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bookings", kpi_data.get('total_bookings', 0),
                  delta=f"+{kpi_data.get('monthly_bookings', 0)} this month")
    with col2:
        st.metric("Total Revenue", f"₹{kpi_data.get('total_revenue', 0):,.0f}",
                  delta=f"₹{kpi_data.get('monthly_revenue', 0):,.0f} this month")
    with col3:
        st.metric("Average Rating", f"{kpi_data.get('avg_rating', 0):.1f}⭐",
                  delta=f"{kpi_data.get('rating_trend', 0):+.1f} vs last month")
    with col4:
        st.metric("Completion Rate", f"{kpi_data.get('completion_rate', 0):.1f}%",
                  delta=f"{kpi_data.get('completion_trend', 0):+.1f}% vs last month")

# ---------------- Performance Analytics ----------------
def display_performance_analytics(username):
    st.subheader("📈 Performance Analytics")
    col1, col2 = st.columns(2)
    with col1:
        time_period = st.selectbox("Time Period",
            ["Last 7 days", "Last 30 days", "Last 3 months", "Last 6 months", "Last year"],
            key="performance_period")
    with col2:
        metric_type = st.selectbox("Metric",
            ["Bookings", "Revenue", "Rating", "Completion Rate"],
            key="performance_metric")

    chart_data = get_performance_chart_data(username, time_period, metric_type)
    if chart_data:
        df_chart = pd.DataFrame(chart_data)
        y_col = 'bookings' if metric_type=='Bookings' else 'revenue' if metric_type=='Revenue' else 'rating' if metric_type=='Rating' else 'completion_rate'
        try:
            fig = px.line(df_chart, x='date', y=y_col, title=f'{metric_type} Over Time ({time_period})')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error plotting performance chart: {e}")
    else:
        st.info("No data available for the selected period")

    st.subheader("💡 Performance Insights")
    insights = get_performance_insights(username)
    for insight in insights:
        try:
            with st.expander(f"{'📈' if insight['type']=='positive' else '📉'} {insight['title']}"):
                st.write(insight['description'])
                st.metric("Impact", insight['value'])
        except Exception as e:
            st.error(f"Error displaying insight: {e}")

# ---------------- Revenue Analytics ----------------
def display_revenue_analytics(username):
    st.subheader("💰 Revenue Analytics")
    revenue_data = get_revenue_data(username)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"₹{revenue_data.get('total',0):,.0f}")
    with col2:
        st.metric("Average per Booking", f"₹{revenue_data.get('average',0):,.0f}")
    with col3:
        st.metric("This Month", f"₹{revenue_data.get('monthly',0):,.0f}")

    st.subheader("📊 Revenue Breakdown")
    breakdown_data = get_revenue_breakdown(username)
    if breakdown_data:
        try:
            df_breakdown = pd.DataFrame(breakdown_data)
            fig = px.pie(df_breakdown, values='amount', names='category', title='Revenue by Category')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_breakdown, use_container_width=True)
        except Exception as e:
            st.error(f"Error plotting revenue breakdown: {e}")
    else:
        st.info("No revenue data available")

    st.subheader("🎯 Revenue Goals")
    col1, col2 = st.columns(2)
    with col1:
        monthly_goal = st.number_input("Monthly Revenue Goal (₹)", value=50000, step=5000)
        current_month = get_current_month_revenue(username)
        progress = (current_month / monthly_goal * 100) if monthly_goal else 0
        st.progress(min(progress/100,1.0))
        st.write(f"Progress: {progress:.1f}%")
        st.write(f"Remaining: ₹{monthly_goal - current_month:,.0f}")
    with col2:
        yearly_goal = st.number_input("Yearly Revenue Goal (₹)", value=600000, step=10000)
        current_year = get_current_year_revenue(username)
        yearly_progress = (current_year / yearly_goal * 100) if yearly_goal else 0
        st.progress(min(yearly_progress/100,1.0))
        st.write(f"Progress: {yearly_progress:.1f}%")
        st.write(f"Remaining: ₹{yearly_goal - current_year:,.0f}")

# ---------------- Customer Analytics ----------------
def display_customer_analytics(username):
    st.subheader("👥 Customer Analytics")
    customer_data = get_customer_data(username)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", customer_data.get('total_customers',0))
    with col2:
        st.metric("Repeat Customers", customer_data.get('repeat_customers',0))
    with col3:
        st.metric("New Customers (30 days)", customer_data.get('new_customers_30d',0))
    with col4:
        st.metric("Customer Retention", f"{customer_data.get('retention_rate',0):.1f}%")

    st.subheader("📊 Customer Segments")
    segments = get_customer_segments(username)
    if segments:
        for segment in segments:
            try:
                with st.expander(f"{segment['icon']} {segment['name']} ({segment['count']} customers)"):
                    st.write(f"**Average Bookings:** {segment['avg_bookings']}")
                    st.write(f"**Total Revenue:** ₹{segment['total_revenue']:,.0f}")
                    st.write(f"**Average Rating:** {segment['avg_rating']:.1f}⭐")
                    st.write(f"**Description:** {segment['description']}")
            except Exception as e:
                st.error(f"Error displaying segment: {e}")
    else:
        st.info("No customer segment data available")

    st.subheader("💎 Customer Lifetime Value")
    clv_data = get_customer_lifetime_value(username)
    if clv_data is not None and not clv_data.empty:
        try:
            if 'segment' in clv_data.columns and 'clv' in clv_data.columns:
                fig = px.bar(clv_data, x='segment', y='clv', title='Customer Lifetime Value by Segment')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Customer lifetime value data missing columns")
        except Exception as e:
            st.error(f"Error plotting CLV chart: {e}")
    else:
        st.info("No customer lifetime value data available")

# ---------------- Service Analytics ----------------
def display_service_analytics(username):
    st.subheader("🎨 Service Analytics")
    service_data = get_service_performance(username)
    if not service_data.empty:
        try:
            st.dataframe(service_data, use_container_width=True)
            fig = px.bar(service_data, x='service_name', y='booking_count', title='Service Popularity')
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.pie(service_data, values='revenue', names='service_name', title='Revenue by Service')
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Error plotting service analytics: {e}")
    else:
        st.info("No service data available")

    st.subheader("💡 Service Optimization")
    suggestions = get_service_optimization_suggestions(username)
    for suggestion in suggestions:
        try:
            with st.expander(f"{'📈' if suggestion['type']=='increase' else '⚡'} {suggestion['title']}"):
                st.write(suggestion['description'])
                st.write(f"**Expected Impact:** {suggestion['impact']}")
                if st.button(f"Apply Suggestion", key=f"suggestion_{suggestion['id']}"):
                    st.success("Suggestion applied!")
        except Exception as e:
            st.error(f"Error displaying suggestion: {e}")

# ---------------- Trend Analytics ----------------
def display_trend_analytics(username):
    st.subheader("📅 Trend Analytics")
    # Seasonal trends
    seasonal_data = get_seasonal_trends(username)
    if seasonal_data is not None and not seasonal_data.empty:
        try:
            fig = px.line(seasonal_data, x='month', y='bookings', title='Bookings by Month')
            st.plotly_chart(fig, use_container_width=True)
            st.write("**Best Performing Months:**")
            for month in seasonal_data.nlargest(3,'bookings')['month']:
                st.write(f"📅 {month}")
        except Exception as e:
            st.error(f"Error displaying seasonal trends: {e}")
    else:
        st.info("No seasonal trend data available")

    # Weekly patterns
    weekly_data = get_weekly_patterns(username)
    if weekly_data is not None and not weekly_data.empty:
        try:
            fig = px.bar(weekly_data, x='day', y='bookings', title='Bookings by Day of Week')
            st.plotly_chart(fig, use_container_width=True)
            st.write("**Peak Days:**")
            for day in weekly_data.nlargest(3,'bookings')['day']:
                st.write(f"📅 {day}")
        except Exception as e:
            st.error(f"Error displaying weekly patterns: {e}")
    else:
        st.info("No weekly pattern data available")

    # Hourly patterns
    hourly_data = get_hourly_patterns(username)
    if hourly_data is not None and not hourly_data.empty:
        try:
            fig = px.line(hourly_data, x='hour', y='bookings', title='Bookings by Hour')
            st.plotly_chart(fig, use_container_width=True)
            st.write("**Peak Hours:**")
            for hour in hourly_data.nlargest(3,'bookings')['hour']:
                st.write(f"🕐 {hour}:00")
        except Exception as e:
            st.error(f"Error displaying hourly patterns: {e}")
    else:
        st.info("No hourly pattern data available")

# ---------------- Data Fetching Functions ----------------
# All existing get_... functions remain the same as in your code
# Only ensure they return default empty DataFrames, lists, or 0 if error occurs
# This prevents ValueError when used in analytics functions
