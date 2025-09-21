import streamlit as st
from datetime import datetime, timedelta
from database import get_db_connection
import time

def artist_status_management(username):
    """Artist online/offline status management"""
    st.subheader("🔄 Status Management")

    # Current status display
    current_status = get_artist_online_status(username)
    status_text = "🟢 Online" if current_status else "🔴 Offline"
    status_color = "green" if current_status else "red"

    st.markdown(f"""
    <div style="padding: 1rem; border-radius: 10px; border-left: 5px solid {status_color}; background-color: #f8f9fa;">
        <h3>Current Status: {status_text}</h3>
        <p>Last updated: {get_last_status_update(username)}</p>
    </div>
    """, unsafe_allow_html=True)

    # Status toggle
    col1, col2 = st.columns(2)

    with col1:
        if current_status:
            if st.button("🔴 Go Offline", type="secondary", key="go_offline"):
                update_artist_status(username, False)
                st.success("Status updated to Offline")
                st.rerun()
        else:
            if st.button("🟢 Go Online", type="primary", key="go_online"):
                update_artist_status(username, True)
                st.success("Status updated to Online")
                st.rerun()

    with col2:
        if st.button("🔄 Toggle Status", key="toggle_status"):
            new_status = not current_status
            update_artist_status(username, new_status)
            status_text = "Online" if new_status else "Offline"
            st.success(f"Status updated to {status_text}")
            st.rerun()

    # Auto status management
    st.subheader("🤖 Auto Status Management")

    col1, col2 = st.columns(2)

    with col1:
        auto_offline = st.checkbox("Auto offline when inactive", value=True)
        if auto_offline:
            inactive_minutes = st.number_input("Offline after (minutes)", min_value=5, max_value=120, value=30)
            st.caption(f"Will go offline automatically after {inactive_minutes} minutes of inactivity")

    with col2:
        work_hours = st.checkbox("Set work hours", value=False)
        if work_hours:
            st.write("**Work Hours**")
            wh_col1, wh_col2 = st.columns(2)

            with wh_col1:
                start_hour = st.time_input("Start Time", value=time(9, 0))
                end_hour = st.time_input("End Time", value=time(17, 0))

            with wh_col2:
                work_days = st.multiselect("Work Days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

    # Save auto settings
    if st.button("💾 Save Auto Settings"):
        save_auto_status_settings(username, {
            'auto_offline': auto_offline,
            'inactive_minutes': inactive_minutes if auto_offline else 30,
            'work_hours': work_hours,
            'start_hour': start_hour.strftime("%H:%M") if work_hours else "09:00",
            'end_hour': end_hour.strftime("%H:%M") if work_hours else "17:00",
            'work_days': work_days if work_hours else []
        })
        st.success("Auto status settings saved!")

    # Status history
    st.subheader("📊 Status History")

    status_history = get_status_history(username)

    if status_history:
        for record in status_history[:10]:  # Show last 10 records
            with st.expander(f"{record['status']} - {record['timestamp']}"):
                st.write(f"**Status:** {record['status']}")
                st.write(f"**Changed at:** {record['timestamp']}")
                st.write(f"**Duration:** {record['duration']}")
    else:
        st.info("No status history available")

    # Quick actions
    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚫 Busy Mode", key="busy_mode"):
            set_busy_mode(username)
            st.warning("Busy mode activated - New bookings disabled")

    with col2:
        if st.button("🎯 Available Now", key="available_now"):
            update_artist_status(username, True)
            st.success("Available now!")

    with col3:
        if st.button("⏰ Break Time", key="break_time"):
            set_break_time(username)
            st.info("Break time activated")

    with col4:
        if st.button("📱 Away", key="away_mode"):
            set_away_mode(username)
            st.info("Away mode activated")

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

def update_artist_status(username, status):
    """Update artist online status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET
            is_online = ?,
            last_active = datetime('now')
            WHERE username = ?
        """, (status, username))

        # Log status change
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'status_change', ?, datetime('now'))
        """, (username, f"Status changed to {'online' if status else 'offline'}"))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating status: {e}")
        return False

def get_last_status_update(username):
    """Get last status update time"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT last_active FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return result[0]
        else:
            return "Never"
    except Exception as e:
        st.error(f"Error getting last update: {e}")
        return "Unknown"

def get_status_history(username):
    """Get status change history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT action, details, created_at,
                   strftime('%s', created_at) as timestamp_seconds
            FROM admin_logs
            WHERE admin_id = (SELECT id FROM users WHERE username = ?)
              AND action = 'status_change'
            ORDER BY created_at DESC
        """, (username,))

        records = cursor.fetchall()
        conn.close()

        # Process records to add duration
        processed_records = []
        for i, record in enumerate(records):
            status_info = {
                'status': record['details'].replace('Status changed to ', ''),
                'timestamp': record['created_at'],
                'duration': 'Current'
            }

            if i < len(records) - 1:
                next_time = datetime.strptime(records[i+1]['created_at'], '%Y-%m-%d %H:%M:%S')
                current_time = datetime.strptime(record['created_at'], '%Y-%m-%d %H:%M:%S')
                duration_seconds = (current_time - next_time).total_seconds()

                if duration_seconds > 0:
                    hours = int(duration_seconds // 3600)
                    minutes = int((duration_seconds % 3600) // 60)

                    if hours > 0:
                        status_info['duration'] = f"{hours}h {minutes}m"
                    else:
                        status_info['duration'] = f"{minutes}m"

            processed_records.append(status_info)

        return processed_records
    except Exception as e:
        st.error(f"Error getting status history: {e}")
        return []

def save_auto_status_settings(username, settings):
    """Save auto status settings"""
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
        st.error(f"Error saving auto settings: {e}")
        return False

def set_busy_mode(username):
    """Set artist to busy mode"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET
            is_online = FALSE,
            last_active = datetime('now')
            WHERE username = ?
        """, (username,))

        # Log busy mode
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'busy_mode', 'Busy mode activated', datetime('now'))
        """, (username,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error setting busy mode: {e}")
        return False

def set_break_time(username):
    """Set artist to break time"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET
            is_online = FALSE,
            last_active = datetime('now')
            WHERE username = ?
        """, (username,))

        # Log break time
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'break_time', 'Break time activated', datetime('now'))
        """, (username,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error setting break time: {e}")
        return False

def set_away_mode(username):
    """Set artist to away mode"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET
            is_online = FALSE,
            last_active = datetime('now')
            WHERE username = ?
        """, (username,))

        # Log away mode
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'away_mode', 'Away mode activated', datetime('now'))
        """, (username,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error setting away mode: {e}")
        return False

def get_status_statistics(username):
    """Get status statistics for the artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total online time today
        cursor.execute("""
            SELECT COUNT(*) FROM admin_logs
            WHERE admin_id = (SELECT id FROM users WHERE username = ?)
              AND action = 'status_change'
              AND details LIKE '%online%'
              AND DATE(created_at) = DATE('now')
        """, (username,))

        online_changes = cursor.fetchone()[0]

        # Get total time online this week
        cursor.execute("""
            SELECT SUM(CASE
                WHEN details LIKE '%online%' THEN 1
                WHEN details LIKE '%offline%' THEN -1
                ELSE 0
            END) as net_status
            FROM admin_logs
            WHERE admin_id = (SELECT id FROM users WHERE username = ?)
              AND action = 'status_change'
              AND DATE(created_at) >= DATE('now', '-7 days')
        """, (username,))

        net_status = cursor.fetchone()[0]

        conn.close()

        return {
            'online_changes_today': online_changes,
            'net_status_week': net_status if net_status else 0,
            'is_currently_online': get_artist_online_status(username)
        }
    except Exception as e:
        st.error(f"Error getting status statistics: {e}")
        return {
            'online_changes_today': 0,
            'net_status_week': 0,
            'is_currently_online': False
        }

def display_status_analytics(username):
    """Display status analytics"""
    st.subheader("📊 Status Analytics")

    stats = get_status_statistics(username)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status Changes Today", stats['online_changes_today'])

    with col2:
        st.metric("Net Online (Week)", f"{stats['net_status_week']} days")

    with col3:
        status_text = "🟢 Online" if stats['is_currently_online'] else "🔴 Offline"
        st.metric("Current Status", status_text)

    # Status timeline
    st.subheader("📈 Status Timeline (Last 7 Days)")

    # Mock timeline data
    timeline_data = [
        {"date": "2024-01-10", "online_hours": 6, "bookings": 3},
        {"date": "2024-01-09", "online_hours": 8, "bookings": 5},
        {"date": "2024-01-08", "online_hours": 4, "bookings": 2},
        {"date": "2024-01-07", "online_hours": 7, "bookings": 4},
        {"date": "2024-01-06", "online_hours": 5, "bookings": 3},
        {"date": "2024-01-05", "online_hours": 6, "bookings": 4},
        {"date": "2024-01-04", "online_hours": 8, "bookings": 6}
    ]

    for day in timeline_data:
        with st.expander(f"📅 {day['date']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Online Hours", day['online_hours'])
            with col2:
                st.metric("Bookings", day['bookings'])
            with col3:
                st.metric("Hourly Rate", f"{day['bookings']/day['online_hours']:.1f}")
