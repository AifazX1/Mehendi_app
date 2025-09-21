import streamlit as st
from datetime import datetime, date, time, timedelta
from database import get_db_connection, get_user_profile, update_artist_profile, get_artist_availability, get_user_bookings
from artist_profile import artist_profile_management
from artist_status import artist_status_management
from artist_chat import artist_chat_interface
from artist_booking import artist_booking_management
from artist_analytics import artist_analytics_dashboard
import pandas as pd

def artist_dashboard():
    """Main artist dashboard with comprehensive functionality"""
    st.markdown('<h1 class="main-header">🎨 Artist Dashboard</h1>', unsafe_allow_html=True)

    # Get artist profile
    username = st.session_state.user
    artist_profile = get_user_profile(username)

    if not artist_profile:
        st.error("Artist profile not found. Please contact admin.")
        return

    # Quick stats display
    display_quick_stats(artist_profile)

    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Profile", "📅 Schedule", "💬 Messages", "📋 Bookings",
        "📊 Analytics", "⚙️ Settings"
    ])

    with tab1:
        artist_profile_management(username, artist_profile)

    with tab2:
        artist_schedule_management(username)

    with tab3:
        artist_chat_interface(username)

    with tab4:
        artist_booking_management(username)

    with tab5:
        artist_analytics_dashboard(username)

    with tab6:
        artist_settings(username)

def display_quick_stats(artist_profile):
    """Display quick statistics for the artist"""
    st.subheader("📈 Quick Stats")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Today's bookings count
        today_bookings = get_today_bookings_count(st.session_state.user)
        st.metric("Today's Bookings", today_bookings)

    with col2:
        # Total earnings (mock data for now)
        total_earnings = get_total_earnings(st.session_state.user)
        st.metric("Total Earnings", f"₹{total_earnings}")

    with col3:
        # Average rating
        avg_rating = artist_profile.get('rating', 0)
        st.metric("Average Rating", f"{avg_rating:.1f}⭐")

    with col4:
        # Status indicator
        is_online = get_artist_online_status(st.session_state.user)
        status_text = "🟢 Online" if is_online else "🔴 Offline"
        st.metric("Status", status_text)

def artist_schedule_management(username):
    """Artist schedule and availability management"""
    st.subheader("📅 Manage Your Schedule")

    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=date.today(), key="schedule_start")
    with col2:
        end_date = st.date_input("To Date", value=date.today() + timedelta(days=7), key="schedule_end")

    # Time slots management
    st.subheader("Set Available Time Slots")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:
        with st.expander(f"{day} - Set Availability"):
            col1, col2, col3 = st.columns(3)

            with col1:
                start_time = st.time_input(f"Start Time ({day})", value=time(9, 0), key=f"start_{day}")
                end_time = st.time_input(f"End Time ({day})", value=time(17, 0), key=f"end_{day}")

            with col2:
                is_available = st.checkbox(f"Available on {day}", value=True, key=f"available_{day}")
                break_duration = st.selectbox(f"Break Duration ({day})",
                    ["No Break", "30 minutes", "1 hour", "1.5 hours", "2 hours"],
                    key=f"break_{day}")

            with col3:
                if st.button(f"Save {day}", key=f"save_day_{day}"):
                    save_availability(username, day, start_time, end_time, is_available, break_duration)
                    st.success(f"{day} schedule updated!")

    # Bulk actions
    st.subheader("Bulk Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Copy This Week to Next Week"):
            copy_schedule_to_next_week(username)
            st.success("Schedule copied to next week!")

    with col2:
        if st.button("🎯 Set Standard Hours (9 AM - 5 PM)"):
            set_standard_hours(username)
            st.success("Standard hours set for all days!")

    with col3:
        if st.button("🚫 Block All Days"):
            block_all_days(username)
            st.success("All days blocked!")

def artist_settings(username):
    """Artist settings and preferences"""
    st.subheader("⚙️ Settings & Preferences")

    # Notification settings
    st.subheader("🔔 Notifications")
    col1, col2 = st.columns(2)

    with col1:
        booking_notifications = st.checkbox("New booking notifications", value=True)
        message_notifications = st.checkbox("New message notifications", value=True)
        review_notifications = st.checkbox("New review notifications", value=True)

    with col2:
        email_notifications = st.checkbox("Email notifications", value=True)
        sms_notifications = st.checkbox("SMS notifications", value=False)
        reminder_notifications = st.checkbox("Appointment reminders", value=True)

    # Business settings
    st.subheader("💼 Business Settings")
    col1, col2 = st.columns(2)

    with col1:
        advance_booking_days = st.number_input("Advance booking days", min_value=1, max_value=90, value=30)
        buffer_time = st.selectbox("Buffer time between appointments",
            ["No buffer", "15 minutes", "30 minutes", "1 hour"])

    with col2:
        auto_accept_bookings = st.checkbox("Auto-accept bookings", value=False)
        require_deposit = st.checkbox("Require deposit for bookings", value=False)

    # Save settings
    if st.button("💾 Save Settings", type="primary"):
        save_artist_settings(username, {
            'booking_notifications': booking_notifications,
            'message_notifications': message_notifications,
            'review_notifications': review_notifications,
            'email_notifications': email_notifications,
            'sms_notifications': sms_notifications,
            'reminder_notifications': reminder_notifications,
            'advance_booking_days': advance_booking_days,
            'buffer_time': buffer_time,
            'auto_accept_bookings': auto_accept_bookings,
            'require_deposit': require_deposit
        })
        st.success("Settings saved successfully!")

# Database helper functions
def get_today_bookings_count(username):
    """Get count of today's bookings for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND DATE(b.appointment_date) = DATE('now')
        """, (username,))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error getting today's bookings: {e}")
        return 0

def get_total_earnings(username):
    """Get total earnings for artist (mock implementation)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(b.amount), 0) FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ? AND b.status = 'completed'
        """, (username,))

        earnings = cursor.fetchone()[0]
        conn.close()
        return earnings if earnings else 0
    except Exception as e:
        st.error(f"Error getting earnings: {e}")
        return 0

def get_artist_online_status(username):
    """Get artist online status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT is_online FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else False
    except Exception as e:
        st.error(f"Error getting online status: {e}")
        return False

def save_availability(username, day, start_time, end_time, is_available, break_duration):
    """Save artist availability for a specific day"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get artist ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_result = cursor.fetchone()

        if not artist_result:
            return False

        artist_id = artist_result[0]

        # Calculate break duration in minutes
        break_minutes = 0
        if break_duration == "30 minutes":
            break_minutes = 30
        elif break_duration == "1 hour":
            break_minutes = 60
        elif break_duration == "1.5 hours":
            break_minutes = 90
        elif break_duration == "2 hours":
            break_minutes = 120

        # Insert or update availability
        cursor.execute("""
            INSERT OR REPLACE INTO artist_availability
            (artist_id, date, start_time, end_time, is_available, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (artist_id, day, start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), is_available))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving availability: {e}")
        return False

def copy_schedule_to_next_week(username):
    """Copy current week's schedule to next week"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get artist ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_result = cursor.fetchone()

        if not artist_result:
            return False

        artist_id = artist_result[0]

        # Copy schedule for next 7 days
        for i in range(7):
            next_date = (date.today() + timedelta(days=i+7)).strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT OR REPLACE INTO artist_availability
                SELECT ?, ?, start_time, end_time, is_available, datetime('now')
                FROM artist_availability
                WHERE artist_id = ? AND date = ?
            """, (artist_id, next_date, artist_id, date.today().strftime("%Y-%m-%d")))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error copying schedule: {e}")
        return False

def set_standard_hours(username):
    """Set standard 9 AM - 5 PM hours for all days"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get artist ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_result = cursor.fetchone()

        if not artist_result:
            return False

        artist_id = artist_result[0]

        # Set standard hours for all days
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            cursor.execute("""
                INSERT OR REPLACE INTO artist_availability
                (artist_id, date, start_time, end_time, is_available, created_at)
                VALUES (?, ?, '09:00', '17:00', 1, datetime('now'))
            """, (artist_id, day))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error setting standard hours: {e}")
        return False

def block_all_days(username):
    """Block all days for the artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get artist ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_result = cursor.fetchone()

        if not artist_result:
            return False

        artist_id = artist_result[0]

        # Block all days
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            cursor.execute("""
                INSERT OR REPLACE INTO artist_availability
                (artist_id, date, start_time, end_time, is_available, created_at)
                VALUES (?, ?, '00:00', '00:00', 0, datetime('now'))
            """, (artist_id, day))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error blocking days: {e}")
        return False

def save_artist_settings(username, settings):
    """Save artist settings to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get artist ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]
        cursor.execute("SELECT id FROM artists WHERE user_id = ?", (user_id,))
        artist_result = cursor.fetchone()

        if not artist_result:
            return False

        artist_id = artist_result[0]

        # Store settings as JSON string (simplified for SQLite)
        settings_json = str(settings)

        cursor.execute("""
            UPDATE artists SET
            specializations = ?,
            updated_at = datetime('now')
            WHERE id = ?
        """, (settings_json, artist_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving settings: {e}")
        return False
