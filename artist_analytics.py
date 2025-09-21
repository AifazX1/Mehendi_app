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
        display_performance_analytics(username)

    with tab2:
        display_revenue_analytics(username)

    with tab3:
        display_customer_analytics(username)

    with tab4:
        display_service_analytics(username)

    with tab5:
        display_trend_analytics(username)

def display_kpi_metrics(username):
    """Display key performance indicators"""
    st.subheader("🎯 Key Performance Indicators")

    # Get KPI data
    kpi_data = get_kpi_data(username)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Bookings",
            kpi_data['total_bookings'],
            delta=f"+{kpi_data['monthly_bookings']} this month"
        )

    with col2:
        st.metric(
            "Total Revenue",
            f"₹{kpi_data['total_revenue']:,.0f}",
            delta=f"₹{kpi_data['monthly_revenue']:,.0f} this month"
        )

    with col3:
        st.metric(
            "Average Rating",
            f"{kpi_data['avg_rating']:.1f}⭐",
            delta=f"{kpi_data['rating_trend']:+.1f} vs last month"
        )

    with col4:
        st.metric(
            "Completion Rate",
            f"{kpi_data['completion_rate']:.1f}%",
            delta=f"{kpi_data['completion_trend']:+.1f}% vs last month"
        )

def display_performance_analytics(username):
    """Display performance analytics"""
    st.subheader("📈 Performance Analytics")

    # Time period selection
    col1, col2 = st.columns(2)

    with col1:
        time_period = st.selectbox("Time Period",
            ["Last 7 days", "Last 30 days", "Last 3 months", "Last 6 months", "Last year"],
            key="performance_period")

    with col2:
        metric_type = st.selectbox("Metric",
            ["Bookings", "Revenue", "Rating", "Completion Rate"],
            key="performance_metric")

    # Generate performance chart
    chart_data = get_performance_chart_data(username, time_period, metric_type)

    if chart_data:
        if metric_type == "Bookings":
            fig = px.line(chart_data, x='date', y='bookings', title=f'Bookings Over Time ({time_period})')
        elif metric_type == "Revenue":
            fig = px.line(chart_data, x='date', y='revenue', title=f'Revenue Over Time ({time_period})')
        elif metric_type == "Rating":
            fig = px.line(chart_data, x='date', y='rating', title=f'Rating Over Time ({time_period})')
        else:
            fig = px.line(chart_data, x='date', y='completion_rate', title=f'Completion Rate Over Time ({time_period})')

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected period")

    # Performance insights
    st.subheader("💡 Performance Insights")

    insights = get_performance_insights(username, time_period)

    for insight in insights:
        with st.expander(f"{'📈' if insight['type'] == 'positive' else '📉'} {insight['title']}"):
            st.write(insight['description'])
            st.metric("Impact", insight['value'])

def display_revenue_analytics(username):
    """Display revenue analytics"""
    st.subheader("💰 Revenue Analytics")

    # Revenue summary
    revenue_data = get_revenue_data(username)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Revenue", f"₹{revenue_data['total']:,.0f}")

    with col2:
        st.metric("Average per Booking", f"₹{revenue_data['average']:,.0f}")

    with col3:
        st.metric("This Month", f"₹{revenue_data['monthly']:,.0f}")

    # Revenue breakdown
    st.subheader("📊 Revenue Breakdown")

    breakdown_data = get_revenue_breakdown(username)

    if breakdown_data:
        # Create pie chart for revenue sources
        fig = px.pie(breakdown_data, values='amount', names='category', title='Revenue by Category')
        st.plotly_chart(fig, use_container_width=True)

        # Display breakdown table
        st.dataframe(breakdown_data, use_container_width=True)
    else:
        st.info("No revenue data available")

    # Revenue goals
    st.subheader("🎯 Revenue Goals")

    col1, col2 = st.columns(2)

    with col1:
        monthly_goal = st.number_input("Monthly Revenue Goal (₹)", value=50000, step=5000)
        current_month = get_current_month_revenue(username)
        progress = (current_month / monthly_goal) * 100

        st.progress(min(progress / 100, 1.0))
        st.write(f"Progress: {progress:.1f}%")
        st.write(f"Remaining: ₹{monthly_goal - current_month:,.0f}")

    with col2:
        yearly_goal = st.number_input("Yearly Revenue Goal (₹)", value=600000, step=10000)
        current_year = get_current_year_revenue(username)
        yearly_progress = (current_year / yearly_goal) * 100

        st.progress(min(yearly_progress / 100, 1.0))
        st.write(f"Progress: {yearly_progress:.1f}%")
        st.write(f"Remaining: ₹{yearly_goal - current_year:,.0f}")

def display_customer_analytics(username):
    """Display customer analytics"""
    st.subheader("👥 Customer Analytics")

    # Customer metrics
    customer_data = get_customer_data(username)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", customer_data['total_customers'])

    with col2:
        st.metric("Repeat Customers", customer_data['repeat_customers'])

    with col3:
        st.metric("New Customers (30 days)", customer_data['new_customers_30d'])

    with col4:
        st.metric("Customer Retention", f"{customer_data['retention_rate']:.1f}%")

    # Customer segments
    st.subheader("📊 Customer Segments")

    segments = get_customer_segments(username)

    if segments:
        for segment in segments:
            with st.expander(f"{segment['icon']} {segment['name']} ({segment['count']} customers)"):
                st.write(f"**Average Bookings:** {segment['avg_bookings']}")
                st.write(f"**Total Revenue:** ₹{segment['total_revenue']:,.0f}")
                st.write(f"**Average Rating:** {segment['avg_rating']:.1f}⭐")
                st.write(f"**Description:** {segment['description']}")
    else:
        st.info("No customer segment data available")

    # Customer lifetime value
    st.subheader("💎 Customer Lifetime Value")

    clv_data = get_customer_lifetime_value(username)

    if clv_data:
        fig = px.bar(clv_data, x='segment', y='clv', title='Customer Lifetime Value by Segment')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer lifetime value data available")

def display_service_analytics(username):
    """Display service analytics"""
    st.subheader("🎨 Service Analytics")

    # Service performance
    service_data = get_service_performance(username)

    if service_data:
        # Service performance table
        st.dataframe(service_data, use_container_width=True)

        # Service popularity chart
        fig = px.bar(service_data, x='service_name', y='booking_count', title='Service Popularity')
        st.plotly_chart(fig, use_container_width=True)

        # Revenue by service
        fig2 = px.pie(service_data, values='revenue', names='service_name', title='Revenue by Service')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No service data available")

    # Service optimization suggestions
    st.subheader("💡 Service Optimization")

    suggestions = get_service_optimization_suggestions(username)

    for suggestion in suggestions:
        with st.expander(f"{'📈' if suggestion['type'] == 'increase' else '⚡'} {suggestion['title']}"):
            st.write(suggestion['description'])
            st.write(f"**Expected Impact:** {suggestion['impact']}")
            if st.button(f"Apply Suggestion", key=f"suggestion_{suggestion['id']}"):
                st.success("Suggestion applied!")

def display_trend_analytics(username):
    """Display trend analytics"""
    st.subheader("📅 Trend Analytics")

    # Seasonal trends
    st.subheader("🌊 Seasonal Trends")

    seasonal_data = get_seasonal_trends(username)

    if seasonal_data:
        fig = px.line(seasonal_data, x='month', y='bookings', title='Bookings by Month')
        st.plotly_chart(fig, use_container_width=True)

        # Best performing months
        st.write("**Best Performing Months:**")
        for month in seasonal_data.nlargest(3, 'bookings')['month']:
            st.write(f"📅 {month}")
    else:
        st.info("No seasonal trend data available")

    # Weekly patterns
    st.subheader("📅 Weekly Patterns")

    weekly_data = get_weekly_patterns(username)

    if weekly_data:
        fig = px.bar(weekly_data, x='day', y='bookings', title='Bookings by Day of Week')
        st.plotly_chart(fig, use_container_width=True)

        st.write("**Peak Days:**")
        for day in weekly_data.nlargest(3, 'bookings')['day']:
            st.write(f"📅 {day}")
    else:
        st.info("No weekly pattern data available")

    # Hourly patterns
    st.subheader("🕐 Hourly Patterns")

    hourly_data = get_hourly_patterns(username)

    if hourly_data:
        fig = px.line(hourly_data, x='hour', y='bookings', title='Bookings by Hour')
        st.plotly_chart(fig, use_container_width=True)

        st.write("**Peak Hours:**")
        for hour in hourly_data.nlargest(3, 'bookings')['hour']:
            st.write(f"🕐 {hour}:00")
    else:
        st.info("No hourly pattern data available")

# Data fetching functions
def get_kpi_data(username):
    """Get KPI data for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total bookings
        cursor.execute("""
            SELECT COUNT(*) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
        """, (username,))
        total_bookings = cursor.fetchone()[0]

        # Monthly bookings
        cursor.execute("""
            SELECT COUNT(*) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')
        """, (username,))
        monthly_bookings = cursor.fetchone()[0]

        # Total revenue
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND b.status = 'completed'
        """, (username,))
        total_revenue = cursor.fetchone()[0]

        # Monthly revenue
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')
              AND b.status = 'completed'
        """, (username,))
        monthly_revenue = cursor.fetchone()[0]

        # Average rating (mock)
        avg_rating = 4.5
        rating_trend = 0.2

        # Completion rate
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
            FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
        """, (username,))
        completion_rate = cursor.fetchone()[0] or 0
        completion_trend = 5.0

        conn.close()

        return {
            'total_bookings': total_bookings,
            'monthly_bookings': monthly_bookings,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'avg_rating': avg_rating,
            'rating_trend': rating_trend,
            'completion_rate': completion_rate,
            'completion_trend': completion_trend
        }
    except Exception as e:
        st.error(f"Error getting KPI data: {e}")
        return {
            'total_bookings': 0,
            'monthly_bookings': 0,
            'total_revenue': 0,
            'monthly_revenue': 0,
            'avg_rating': 0,
            'rating_trend': 0,
            'completion_rate': 0,
            'completion_trend': 0
        }

def get_performance_chart_data(username, time_period, metric_type):
    """Get performance chart data"""
    try:
        # Mock data - would be implemented with real database queries
        if time_period == "Last 7 days":
            dates = [(date.today() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        elif time_period == "Last 30 days":
            dates = [(date.today() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
        else:
            dates = [(date.today() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(89, -1, -1)]

        data = []
        for i, date_str in enumerate(dates):
            if metric_type == "Bookings":
                value = 5 + i + (i % 3)  # Mock data
            elif metric_type == "Revenue":
                value = 2500 + i * 100 + (i % 500)  # Mock data
            elif metric_type == "Rating":
                value = 4.0 + (i % 10) * 0.1  # Mock data
            else:
                value = 85 + (i % 15)  # Mock data

            data.append({'date': date_str, 'bookings' if metric_type == 'Bookings' else 'revenue' if metric_type == 'Revenue' else 'rating' if metric_type == 'Rating' else 'completion_rate': value})

        return data
    except Exception as e:
        st.error(f"Error getting performance chart data: {e}")
        return []

def get_performance_insights(username, time_period):
    """Get performance insights"""
    try:
        # Mock insights
        return [
            {
                'type': 'positive',
                'title': 'Increased Bookings',
                'description': 'Your bookings have increased by 25% compared to last month',
                'value': '+25%'
            },
            {
                'type': 'positive',
                'title': 'High Customer Satisfaction',
                'description': 'Customer ratings are consistently above 4.5 stars',
                'value': '4.7⭐'
            },
            {
                'type': 'negative',
                'title': 'Weekend Availability',
                'description': 'Consider being available on weekends for more bookings',
                'value': '-30% potential'
            }
        ]
    except Exception as e:
        st.error(f"Error getting performance insights: {e}")
        return []

def get_revenue_data(username):
    """Get revenue data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total revenue
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND b.status = 'completed'
        """, (username,))
        total = cursor.fetchone()[0]

        # Monthly revenue
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')
              AND b.status = 'completed'
        """, (username,))
        monthly = cursor.fetchone()[0]

        # Average per booking
        cursor.execute("""
            SELECT AVG(amount) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND amount > 0 AND b.status = 'completed'
        """, (username,))
        average = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total': total,
            'monthly': monthly,
            'average': average
        }
    except Exception as e:
        st.error(f"Error getting revenue data: {e}")
        return {'total': 0, 'monthly': 0, 'average': 0}

def get_revenue_breakdown(username):
    """Get revenue breakdown by category"""
    try:
        # Mock data - would be implemented with real categorization
        return [
            {'category': 'Bridal Mehndi', 'amount': 45000},
            {'category': 'Arabic Design', 'amount': 25000},
            {'category': 'Traditional Design', 'amount': 15000},
            {'category': 'Party Mehndi', 'amount': 10000}
        ]
    except Exception as e:
        st.error(f"Error getting revenue breakdown: {e}")
        return []

def get_current_month_revenue(username):
    """Get current month revenue"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')
              AND b.status = 'completed'
        """, (username,))

        revenue = cursor.fetchone()[0]
        conn.close()
        return revenue
    except Exception as e:
        st.error(f"Error getting current month revenue: {e}")
        return 0

def get_current_year_revenue(username):
    """Get current year revenue"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y', b.appointment_date) = strftime('%Y', 'now')
              AND b.status = 'completed'
        """, (username,))

        revenue = cursor.fetchone()[0]
        conn.close()
        return revenue
    except Exception as e:
        st.error(f"Error getting current year revenue: {e}")
        return 0

def get_customer_data(username):
    """Get customer analytics data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total customers
        cursor.execute("""
            SELECT COUNT(DISTINCT b.user_id) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
        """, (username,))
        total_customers = cursor.fetchone()[0]

        # Repeat customers
        cursor.execute("""
            SELECT COUNT(DISTINCT b.user_id) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
            GROUP BY b.user_id
            HAVING COUNT(*) > 1
        """, (username,))
        repeat_customers = cursor.fetchone()[0] if cursor.fetchone() else 0

        # New customers in last 30 days
        cursor.execute("""
            SELECT COUNT(DISTINCT b.user_id) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND b.appointment_date >= date('now', '-30 days')
        """, (username,))
        new_customers_30d = cursor.fetchone()[0]

        # Retention rate (mock)
        retention_rate = 75.0

        conn.close()

        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'new_customers_30d': new_customers_30d,
            'retention_rate': retention_rate
        }
    except Exception as e:
        st.error(f"Error getting customer data: {e}")
        return {
            'total_customers': 0,
            'repeat_customers': 0,
            'new_customers_30d': 0,
            'retention_rate': 0
        }

def get_customer_segments(username):
    """Get customer segments"""
    try:
        # Mock data
        return [
            {
                'icon': '👰',
                'name': 'Bridal Customers',
                'count': 25,
                'avg_bookings': 1.5,
                'total_revenue': 45000,
                'avg_rating': 4.8,
                'description': 'Customers booking for weddings and special occasions'
            },
            {
                'icon': '🎉',
                'name': 'Party Customers',
                'count': 18,
                'avg_bookings': 1.2,
                'total_revenue': 25000,
                'avg_rating': 4.6,
                'description': 'Customers booking for parties and celebrations'
            },
            {
                'icon': '🎨',
                'name': 'Regular Customers',
                'count': 12,
                'avg_bookings': 3.2,
                'total_revenue': 35000,
                'avg_rating': 4.9,
                'description': 'Repeat customers who book regularly'
            }
        ]
    except Exception as e:
        st.error(f"Error getting customer segments: {e}")
        return []

def get_customer_lifetime_value(username):
    """Get customer lifetime value data"""
    try:
        # Mock data
        return pd.DataFrame({
            'segment': ['Bridal', 'Party', 'Regular', 'Festival'],
            'clv': [2500, 1500, 4000, 800]
        })
    except Exception as e:
        st.error(f"Error getting customer lifetime value: {e}")
        return pd.DataFrame()

def get_service_performance(username):
    """Get service performance data"""
    try:
        # Mock data
        return pd.DataFrame({
            'service_name': ['Bridal Mehndi', 'Arabic Design', 'Traditional Design', 'Party Mehndi'],
            'booking_count': [25, 18, 12, 8],
            'revenue': [45000, 25000, 15000, 10000],
            'avg_rating': [4.8, 4.6, 4.7, 4.5],
            'completion_rate': [95, 92, 98, 90]
        })
    except Exception as e:
        st.error(f"Error getting service performance: {e}")
        return pd.DataFrame()

def get_service_optimization_suggestions(username):
    """Get service optimization suggestions"""
    try:
        # Mock suggestions
        return [
            {
                'id': 1,
                'type': 'increase',
                'title': 'Increase Bridal Mehndi Pricing',
                'description': 'Your bridal mehndi services are in high demand. Consider increasing prices by 15-20%.',
                'impact': '+₹15,000/month'
            },
            {
                'id': 2,
                'type': 'increase',
                'title': 'Add Package Deals',
                'description': 'Create package deals combining multiple services for better value.',
                'impact': '+25% bookings'
            },
            {
                'id': 3,
                'type': 'optimize',
                'title': 'Optimize Traditional Design',
                'description': 'Traditional designs have lower completion rate. Consider streamlining the process.',
                'impact': '+8% efficiency'
            }
        ]
    except Exception as e:
        st.error(f"Error getting service optimization suggestions: {e}")
        return []

def get_seasonal_trends(username):
    """Get seasonal trends data"""
    try:
        # Mock data
        return pd.DataFrame({
            'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'bookings': [15, 12, 18, 22, 28, 25, 20, 18, 24, 30, 35, 28]
        })
    except Exception as e:
        st.error(f"Error getting seasonal trends: {e}")
        return pd.DataFrame()

def get_weekly_patterns(username):
    """Get weekly patterns data"""
    try:
        # Mock data
        return pd.DataFrame({
            'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'bookings': [12, 15, 18, 20, 22, 25, 8]
        })
    except Exception as e:
        st.error(f"Error getting weekly patterns: {e}")
        return pd.DataFrame()

def get_hourly_patterns(username):
    """Get hourly patterns data"""
    try:
        # Mock data
        return pd.DataFrame({
            'hour': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            'bookings': [5, 8, 12, 10, 6, 15, 18, 12, 8, 4]
        })
    except Exception as e:
        st.error(f"Error getting hourly patterns: {e}")
        return pd.DataFrame()
