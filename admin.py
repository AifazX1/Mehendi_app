import streamlit as st
import pandas as pd
from database import get_db_connection, log_admin_action
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def admin_dashboard():
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)

    # Admin navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Artist Management",
        "🚩 Flagged Content",
        "⚙️ App Settings",
        "📊 Analytics",
        "📋 Audit Logs"
    ])

    with tab1:
        artist_management()

    with tab2:
        flagged_content()

    with tab3:
        app_settings()

    with tab4:
        analytics_dashboard()

    with tab5:
        audit_logs()

def artist_management():
    st.subheader("Artist Approval & Management")

    # Get pending artists
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.*, u.username, u.email, u.phone
        FROM artists a
        JOIN users u ON a.user_id = u.id
        WHERE a.status = 'pending'
        ORDER BY a.created_at DESC
    """)

    pending_artists = cursor.fetchall()
    conn.close()

    if pending_artists:
        st.subheader("Pending Approvals")

        for artist in pending_artists:
            with st.expander(f"Review: {artist['name']} ({artist['username']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Name:** {artist['name']}")
                    st.write(f"**Username:** {artist['username']}")
                    st.write(f"**Email:** {artist['email'] or 'Not provided'}")
                    st.write(f"**Phone:** {artist['phone'] or 'Not provided'}")
                    st.write(f"**Address:** {artist['address'] or 'Not provided'}")
                    st.write(f"**Experience:** {artist['experience_years'] or 0} years")
                    st.write(f"**Specializations:** {artist['specializations'] or 'Not specified'}")

                with col2:
                    st.write(f"**Price Range:** {artist['price_range'] or 'Not set'}")
                    st.write(f"**Areas Covered:** {artist['areas_covered'] or 'Not specified'}")
                    st.write(f"**Bio:** {artist['bio'] or 'No bio provided'}")
                    st.write(f"**Applied:** {artist['created_at']}")

                # Approval buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{artist['id']}"):
                        approve_artist(artist['id'])
                        st.success("Artist approved!")
                        st.rerun()

                with col2:
                    if st.button("❌ Reject", key=f"reject_{artist['id']}"):
                        reject_artist(artist['id'])
                        st.success("Artist rejected!")
                        st.rerun()

                with col3:
                    if st.button("⏸️ Suspend", key=f"suspend_{artist['id']}"):
                        suspend_artist(artist['id'])
                        st.success("Artist suspended!")
                        st.rerun()

    # Show all artists
    st.subheader("All Artists")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.*, u.username, u.is_online,
               (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) as avg_rating,
               (SELECT COUNT(*) FROM reviews r WHERE r.artist_id = a.id) as review_count
        FROM artists a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.status, u.is_online DESC
    """)

    all_artists = cursor.fetchall()
    conn.close()

    if all_artists:
        # Convert to DataFrame for better display
        df = pd.DataFrame(all_artists)
        df['avg_rating'] = df['avg_rating'].fillna(0).round(1)
        df['status'] = df['status'].str.title()

        st.dataframe(df[['name', 'username', 'status', 'avg_rating', 'review_count', 'is_online']],
                    column_config={
                        "name": "Artist Name",
                        "username": "Username",
                        "status": "Status",
                        "avg_rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                        "review_count": "Reviews",
                        "is_online": st.column_config.CheckboxColumn("Online", default=False)
                    })

def approve_artist(artist_id):
    """Approve an artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE artists SET status = 'approved' WHERE id = ?", (artist_id,))
        conn.commit()
        conn.close()

        # Log admin action
        log_admin_action(st.session_state.user, f"Approved artist {artist_id}", "Artist approval")
        return True
    except Exception as e:
        st.error(f"Error approving artist: {e}")
        return False

def reject_artist(artist_id):
    """Reject an artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE artists SET status = 'rejected' WHERE id = ?", (artist_id,))
        conn.commit()
        conn.close()

        # Log admin action
        log_admin_action(st.session_state.user, f"Rejected artist {artist_id}", "Artist rejection")
        return True
    except Exception as e:
        st.error(f"Error rejecting artist: {e}")
        return False

def suspend_artist(artist_id):
    """Suspend an artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE artists SET status = 'suspended' WHERE id = ?", (artist_id,))
        conn.commit()
        conn.close()

        # Log admin action
        log_admin_action(st.session_state.user, f"Suspended artist {artist_id}", "Artist suspension")
        return True
    except Exception as e:
        st.error(f"Error suspending artist: {e}")
        return False

def flagged_content():
    st.subheader("Flagged Chats & Content")

    st.write("🚧 Flagged content management would be implemented here")
    st.info("This would include chat monitoring, inappropriate content detection, and user reports")

def app_settings():
    st.subheader("Application Settings")

    st.write("⚙️ App configuration settings would be here")
    st.info("Settings like pricing tiers, commission rates, notification preferences, etc.")

def analytics_dashboard():
    st.subheader("Analytics Dashboard")

    # Get real analytics data from database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total counts
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM artists WHERE status = 'approved'")
    total_artists = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM bookings WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    # Calculate growth percentages (mock for now - would compare with previous period)
    user_growth = "12%"
    artist_growth = "8%"
    booking_growth = "23%"
    revenue_growth = "18%"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", f"{total_users:,}", user_growth)
    with col2:
        st.metric("Total Artists", f"{total_artists:,}", artist_growth)
    with col3:
        st.metric("Total Bookings", f"{total_bookings:,}", booking_growth)
    with col4:
        st.metric("Revenue", f"₹{total_revenue:,}", revenue_growth)

    # Charts - Monthly trends for last 6 months
    st.subheader("Monthly Trends")

    # Get monthly booking data
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as bookings,
               SUM(amount) as revenue
        FROM bookings
        WHERE created_at >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month
    """)

    monthly_data = cursor.fetchall()
    conn.close()

    if monthly_data:
        months = [row[0] for row in monthly_data]
        bookings = [row[1] for row in monthly_data]
        revenue = [row[2] or 0 for row in monthly_data]

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(x=months, y=bookings, title="Monthly Bookings")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar(x=months, y=revenue, title="Monthly Revenue")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No booking data available for charts")

    # User activity
    st.subheader("User Activity")

    # Get user activity data
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    cursor.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (today,))
    active_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (week_ago,))
    active_week = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (month_ago,))
    active_month = cursor.fetchone()[0]

    conn.close()

    activity_data = {
        'Users': ['Active Today', 'Active This Week', 'Active This Month'],
        'Count': [active_today, active_week, active_month]
    }

    fig3 = px.pie(values=activity_data['Count'], names=activity_data['Users'],
                  title="User Activity Distribution")
    st.plotly_chart(fig3, use_container_width=True)

def audit_logs():
    st.subheader("Admin Audit Logs")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT al.*, u.username
            FROM admin_logs al
            JOIN users u ON al.admin_id = u.id
            ORDER BY al.created_at DESC
            LIMIT 100
        """)

        logs = cursor.fetchall()
        conn.close()

        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df[['username', 'action', 'details', 'created_at']],
                        column_config={
                            "username": "Admin",
                            "action": "Action",
                            "details": "Details",
                            "created_at": "Timestamp"
                        })
        else:
            st.info("No audit logs found")
    except Exception as e:
        st.error(f"Error loading audit logs: {e}")
