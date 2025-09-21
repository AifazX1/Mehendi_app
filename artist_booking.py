import streamlit as st
from datetime import datetime, date, time, timedelta
from database import get_db_connection, get_user_bookings
import pandas as pd

def artist_booking_management(username):
    """Artist booking management interface"""
    st.subheader("📋 Booking Management")

    # Booking tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Today's Bookings", "🔄 Pending Requests", "📊 All Bookings", "📈 Booking Analytics"])

    with tab1:
        display_today_bookings(username)

    with tab2:
        display_pending_requests(username)

    with tab3:
        display_all_bookings(username)

    with tab4:
        display_booking_analytics(username)

def display_today_bookings(username):
    """Display today's bookings for the artist"""
    st.write("**Today's Appointments**")

    today_bookings = get_today_bookings(username)

    if today_bookings:
        for booking in today_bookings:
            with st.expander(f"{'✅' if booking['status'] == 'confirmed' else '⏳'} {booking['customer_name']} - {booking['start_time']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Customer:** {booking['customer_name']}")
                    st.write(f"**Service:** {booking['service_type']}")
                    st.write(f"**Time:** {booking['start_time']} - {booking['end_time']}")
                    st.write(f"**Amount:** ₹{booking['amount']}")
                    if booking['notes']:
                        st.write(f"**Notes:** {booking['notes']}")

                with col2:
                    # Status badge
                    status_color = {
                        'pending': '🟡',
                        'confirmed': '🟢',
                        'completed': '✅',
                        'cancelled': '❌'
                    }
                    st.write(f"**Status:** {status_color.get(booking['status'], '❓')} {booking['status'].title()}")

                    # Action buttons
                    if booking['status'] == 'pending':
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Accept", key=f"accept_{booking['id']}"):
                                update_booking_status(booking['id'], 'confirmed')
                                st.success("Booking accepted!")
                                st.rerun()
                        with col_b:
                            if st.button("❌ Reject", key=f"reject_{booking['id']}"):
                                update_booking_status(booking['id'], 'cancelled')
                                st.error("Booking rejected")
                                st.rerun()

                    elif booking['status'] == 'confirmed':
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("🎉 Complete", key=f"complete_{booking['id']}"):
                                update_booking_status(booking['id'], 'completed')
                                st.success("Booking marked as completed!")
                                st.rerun()
                        with col_b:
                            if st.button("📝 Reschedule", key=f"reschedule_{booking['id']}"):
                                st.info("Reschedule interface would open here")

                    # Contact actions
                    st.write("**Contact:**")
                    if st.button("💬 Message", key=f"message_{booking['id']}"):
                        st.info("Chat interface would open here")

                    if st.button("📞 Call", key=f"call_{booking['id']}"):
                        st.info("Call interface would open here")
    else:
        st.info("No appointments scheduled for today! 🎉")

        # Quick actions for empty day
        st.write("**Quick Actions:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📅 View Calendar"):
                st.info("Calendar view would open here")

        with col2:
            if st.button("⏰ Set Availability"):
                st.info("Availability settings would open here")

        with col3:
            if st.button("📊 View Analytics"):
                st.info("Analytics would be displayed here")

def display_pending_requests(username):
    """Display pending booking requests"""
    st.write("**Pending Booking Requests**")

    pending_bookings = get_pending_bookings(username)

    if pending_bookings:
        for booking in pending_bookings:
            with st.expander(f"⏳ {booking['customer_name']} - {booking['appointment_date']} at {booking['start_time']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Customer:** {booking['customer_name']}")
                    st.write(f"**Date:** {booking['appointment_date']}")
                    st.write(f"**Time:** {booking['start_time']} - {booking['end_time']}")
                    st.write(f"**Service:** {booking['service_type']}")
                    st.write(f"**Amount:** ₹{booking['amount']}")
                    if booking['notes']:
                        st.write(f"**Special Requests:** {booking['notes']}")

                    # Customer details
                    st.write("**Customer Contact:**")
                    st.write(f"📧 {booking['customer_email']}")
                    st.write(f"📱 {booking['customer_phone']}")

                with col2:
                    # Action buttons
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("✅ Accept", key=f"accept_req_{booking['id']}"):
                            update_booking_status(booking['id'], 'confirmed')
                            st.success("Booking request accepted!")
                            st.rerun()

                    with col_b:
                        if st.button("❌ Reject", key=f"reject_req_{booking['id']}"):
                            update_booking_status(booking['id'], 'cancelled')
                            st.error("Booking request rejected")
                            st.rerun()

                    with col_c:
                        if st.button("📝 Modify", key=f"modify_req_{booking['id']}"):
                            st.info("Booking modification interface would open here")

                    # Additional actions
                    if st.button("💬 Contact Customer", key=f"contact_req_{booking['id']}"):
                        st.info("Customer contact interface would open here")
    else:
        st.info("No pending booking requests! 📬")

def display_all_bookings(username):
    """Display all bookings with filters"""
    st.write("**All Bookings**")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Confirmed", "Completed", "Cancelled"])

    with col2:
        date_filter = st.selectbox("Time Period", ["All Time", "This Month", "Last 30 Days", "This Week"])

    with col3:
        sort_by = st.selectbox("Sort By", ["Date (Newest)", "Date (Oldest)", "Customer Name", "Amount"])

    # Get filtered bookings
    all_bookings = get_all_bookings(username, status_filter, date_filter, sort_by)

    if all_bookings:
        # Display as table
        st.dataframe(all_bookings, use_container_width=True)

        # Bulk actions
        st.write("**Bulk Actions:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Export to CSV"):
                export_bookings_csv(all_bookings)
                st.success("Bookings exported to CSV!")

        with col2:
            if st.button("📧 Send Reminders"):
                st.info("Reminder emails would be sent")

        with col3:
            if st.button("📊 Generate Report"):
                st.info("Booking report would be generated")
    else:
        st.info("No bookings found matching the criteria.")

def display_booking_analytics(username):
    """Display booking analytics"""
    st.subheader("📊 Booking Analytics")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_bookings = get_total_booking_count(username)
        st.metric("Total Bookings", total_bookings)

    with col2:
        monthly_bookings = get_monthly_booking_count(username)
        st.metric("This Month", monthly_bookings)

    with col3:
        completion_rate = get_completion_rate(username)
        st.metric("Completion Rate", f"{completion_rate:.1f}%")

    with col4:
        avg_booking_value = get_avg_booking_value(username)
        st.metric("Avg Booking Value", f"₹{avg_booking_value:.0f}")

    # Booking trends
    st.subheader("📈 Booking Trends")

    # Mock trend data
    trend_data = {
        "Week 1": {"bookings": 8, "revenue": 4000, "completion": 95},
        "Week 2": {"bookings": 12, "revenue": 6000, "completion": 92},
        "Week 3": {"bookings": 15, "revenue": 7500, "completion": 98},
        "Week 4": {"bookings": 10, "revenue": 5000, "completion": 90}
    }

    for week, data in trend_data.items():
        with st.expander(f"📅 {week}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bookings", data["bookings"])
            with col2:
                st.metric("Revenue", f"₹{data['revenue']}")
            with col3:
                st.metric("Completion %", f"{data['completion']}%")

    # Popular services
    st.subheader("🎨 Popular Services")

    popular_services = get_popular_services(username)

    if popular_services:
        for service in popular_services:
            st.write(f"**{service['name']}:** {service['count']} bookings (₹{service['revenue']})")
    else:
        st.info("No service data available")

    # Customer insights
    st.subheader("👥 Customer Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Repeat Customers:**")
        repeat_customers = get_repeat_customer_count(username)
        st.metric("Repeat Customers", repeat_customers)

        st.write("**New Customers:**")
        new_customers = get_new_customer_count(username)
        st.metric("New Customers", new_customers)

    with col2:
        st.write("**Customer Satisfaction:**")
        satisfaction = get_customer_satisfaction_score(username)
        st.metric("Avg Rating", f"{satisfaction:.1f}⭐")

        st.write("**Top Customer:**")
        top_customer = get_top_customer(username)
        if top_customer:
            st.write(f"{top_customer['name']} ({top_customer['booking_count']} bookings)")

# Database helper functions
def get_today_bookings(username):
    """Get today's bookings for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.*, u.username as customer_name, u.email as customer_email, u.phone as customer_phone
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN artists a ON b.artist_id = a.id
            JOIN users au ON a.user_id = au.id
            WHERE au.username = ? AND DATE(b.appointment_date) = DATE('now')
            ORDER BY b.start_time ASC
        """, (username,))

        bookings = cursor.fetchall()
        conn.close()

        return [dict(booking) for booking in bookings]
    except Exception as e:
        st.error(f"Error getting today's bookings: {e}")
        return []

def get_pending_bookings(username):
    """Get pending booking requests for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.*, u.username as customer_name, u.email as customer_email, u.phone as customer_phone
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN artists a ON b.artist_id = a.id
            JOIN users au ON a.user_id = au.id
            WHERE au.username = ? AND b.status = 'pending'
            ORDER BY b.appointment_date ASC, b.start_time ASC
        """, (username,))

        bookings = cursor.fetchall()
        conn.close()

        return [dict(booking) for booking in bookings]
    except Exception as e:
        st.error(f"Error getting pending bookings: {e}")
        return []

def get_all_bookings(username, status_filter="All", date_filter="All Time", sort_by="Date (Newest)"):
    """Get all bookings with filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT b.*, u.username as customer_name, u.email as customer_email, u.phone as customer_phone
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN artists a ON b.artist_id = a.id
            JOIN users au ON a.user_id = au.id
            WHERE au.username = ?
        """

        params = [username]

        # Apply status filter
        if status_filter != "All":
            query += " AND b.status = ?"
            params.append(status_filter.lower())

        # Apply date filter
        if date_filter == "This Month":
            query += " AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')"
        elif date_filter == "Last 30 Days":
            query += " AND b.appointment_date >= date('now', '-30 days')"
        elif date_filter == "This Week":
            query += " AND b.appointment_date >= date('now', 'weekday 0', '-6 days')"

        # Apply sorting
        if sort_by == "Date (Newest)":
            query += " ORDER BY b.appointment_date DESC, b.start_time DESC"
        elif sort_by == "Date (Oldest)":
            query += " ORDER BY b.appointment_date ASC, b.start_time ASC"
        elif sort_by == "Customer Name":
            query += " ORDER BY u.username ASC"
        elif sort_by == "Amount":
            query += " ORDER BY b.amount DESC"

        cursor.execute(query, params)
        bookings = cursor.fetchall()
        conn.close()

        return [dict(booking) for booking in bookings]
    except Exception as e:
        st.error(f"Error getting all bookings: {e}")
        return []

def update_booking_status(booking_id, status):
    """Update booking status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE bookings SET
            status = ?,
            updated_at = datetime('now')
            WHERE id = ?
        """, (status, booking_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating booking status: {e}")
        return False

def get_total_booking_count(username):
    """Get total booking count for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
        """, (username,))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error getting total booking count: {e}")
        return 0

def get_monthly_booking_count(username):
    """Get monthly booking count for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND strftime('%Y-%m', b.appointment_date) = strftime('%Y-%m', 'now')
        """, (username,))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error getting monthly booking count: {e}")
        return 0

def get_completion_rate(username):
    """Get booking completion rate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
            FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
        """, (username,))

        rate = cursor.fetchone()[0]
        conn.close()
        return rate if rate else 0
    except Exception as e:
        st.error(f"Error getting completion rate: {e}")
        return 0

def get_avg_booking_value(username):
    """Get average booking value"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT AVG(amount) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND amount > 0
        """, (username,))

        avg_value = cursor.fetchone()[0]
        conn.close()
        return avg_value if avg_value else 0
    except Exception as e:
        st.error(f"Error getting average booking value: {e}")
        return 0

def get_popular_services(username):
    """Get popular services"""
    try:
        # Mock data - would be implemented based on actual service types
        return [
            {"name": "Bridal Mehndi", "count": 25, "revenue": 15000},
            {"name": "Arabic Design", "count": 18, "revenue": 9000},
            {"name": "Traditional Design", "count": 12, "revenue": 6000}
        ]
    except Exception as e:
        st.error(f"Error getting popular services: {e}")
        return []

def get_repeat_customer_count(username):
    """Get repeat customer count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(DISTINCT b.user_id) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
            GROUP BY b.user_id
            HAVING COUNT(*) > 1
        """, (username,))

        count = cursor.fetchone()
        conn.close()
        return count[0] if count else 0
    except Exception as e:
        st.error(f"Error getting repeat customer count: {e}")
        return 0

def get_new_customer_count(username):
    """Get new customer count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(DISTINCT b.user_id) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
              AND b.appointment_date >= date('now', '-30 days')
        """, (username,))

        count = cursor.fetchone()
        conn.close()
        return count[0] if count else 0
    except Exception as e:
        st.error(f"Error getting new customer count: {e}")
        return 0

def get_customer_satisfaction_score(username):
    """Get customer satisfaction score"""
    try:
        # Mock implementation - would get from reviews
        return 4.7
    except Exception as e:
        st.error(f"Error getting customer satisfaction: {e}")
        return 4.0

def get_top_customer(username):
    """Get top customer"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.username as name, COUNT(*) as booking_count
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN artists a ON b.artist_id = a.id
            JOIN users au ON a.user_id = au.id
            WHERE au.username = ?
            GROUP BY u.id, u.username
            ORDER BY booking_count DESC
            LIMIT 1
        """, (username,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {"name": result[0], "booking_count": result[1]}
        return None
    except Exception as e:
        st.error(f"Error getting top customer: {e}")
        return None

def export_bookings_csv(bookings):
    """Export bookings to CSV"""
    try:
        # Convert bookings to DataFrame
        df = pd.DataFrame(bookings)

        # Select relevant columns
        columns_to_export = ['id', 'customer_name', 'appointment_date', 'start_time', 'end_time', 'status', 'amount']
        df_export = df[columns_to_export] if all(col in df.columns for col in columns_to_export) else df

        # Download CSV
        st.download_button(
            label="📥 Download CSV",
            data=df_export.to_csv(index=False),
            file_name=f"bookings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error exporting CSV: {e}")
