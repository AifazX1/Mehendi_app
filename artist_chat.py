import streamlit as st
from datetime import datetime
from database import get_db_connection
import time

def artist_chat_interface(username):
    """Enhanced chat interface for artists"""
    st.subheader("💬 Chat with Customers")

    # Chat tabs
    tab1, tab2, tab3 = st.tabs(["📨 Active Chats", "👥 All Conversations", "📊 Chat Analytics"])

    with tab1:
        display_active_chats(username)

    with tab2:
        display_all_conversations(username)

    with tab3:
        display_chat_analytics(username)

def display_active_chats(username):
    """Display active chats for the artist"""
    st.write("**Active Conversations**")

    # Get active chats (mock data for now)
    active_chats = get_active_chats(username)

    if active_chats:
        for chat in active_chats:
            with st.expander(f"💬 {chat['customer_name']} - {chat['last_message_time']}", expanded=chat['unread_count'] > 0):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Customer:** {chat['customer_name']}")
                    st.write(f"**Last Message:** {chat['last_message']}")
                    st.write(f"**Unread:** {chat['unread_count']}")

                    # Quick reply options
                    st.write("**Quick Replies:**")
                    quick_replies = [
                        "I'll be there on time! 🕐",
                        "Thank you for choosing me! 🙏",
                        "Please share design references 📸",
                        "Payment details sent 💳"
                    ]

                    reply_cols = st.columns(2)
                    for i, reply in enumerate(quick_replies):
                        with reply_cols[i % 2]:
                            if st.button(reply, key=f"quick_{chat['id']}_{i}"):
                                send_quick_reply(username, chat['customer_id'], reply)
                                st.success("Reply sent!")

                with col2:
                    # Chat actions
                    if st.button("Open Chat", key=f"open_{chat['id']}"):
                        st.info("Full chat interface would open here")

                    if st.button("Mark Read", key=f"read_{chat['id']}"):
                        mark_chat_read(username, chat['customer_id'])
                        st.success("Chat marked as read")

                    if st.button("Archive", key=f"archive_{chat['id']}"):
                        archive_chat(username, chat['customer_id'])
                        st.success("Chat archived")
    else:
        st.info("No active chats. All caught up! 🎉")

def display_all_conversations(username):
    """Display all conversations for the artist"""
    st.write("**All Conversations**")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status", ["All", "Active", "Archived", "Flagged"])

    with col2:
        date_filter = st.selectbox("Time Period", ["All Time", "Today", "This Week", "This Month"])

    with col3:
        sort_by = st.selectbox("Sort By", ["Recent", "Most Messages", "Customer Name"])

    # Get all conversations
    conversations = get_all_conversations(username, status_filter, date_filter, sort_by)

    if conversations:
        for conv in conversations:
            with st.expander(f"{'💬' if not conv['archived'] else '📁'} {conv['customer_name']} - {conv['last_activity']}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**Customer:** {conv['customer_name']}")
                    st.write(f"**Total Messages:** {conv['message_count']}")
                    st.write(f"**Last Message:** {conv['last_message']}")
                    st.write(f"**Status:** {'Archived' if conv['archived'] else 'Active'}")

                with col2:
                    if st.button("View Chat", key=f"view_{conv['other_user_id']}"):
                        st.info("Chat viewer would open here")

                    if st.button("Reply", key=f"reply_{conv['other_user_id']}"):
                        st.info("Quick reply interface would open here")

                with col3:
                    if not conv['archived']:
                        if st.button("Archive", key=f"archive_conv_{conv['other_user_id']}"):
                            archive_conversation(username, conv['customer_id'])
                            st.success("Conversation archived")

                    if st.button("Flag", key=f"flag_{conv['other_user_id']}"):
                        flag_conversation(username, conv['customer_id'])
                        st.warning("Conversation flagged for review")
    else:
        st.info("No conversations found.")

def display_chat_analytics(username):
    """Display chat analytics for the artist"""
    st.subheader("📊 Chat Analytics")

    # Analytics metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_chats = get_total_chat_count(username)
        st.metric("Total Chats", total_chats)

    with col2:
        active_chats = get_active_chat_count(username)
        st.metric("Active Chats", active_chats)

    with col3:
        avg_response_time = get_avg_response_time(username)
        st.metric("Avg Response Time", f"{avg_response_time:.1f} min")

    with col4:
        customer_satisfaction = get_customer_satisfaction(username)
        st.metric("Customer Rating", f"{customer_satisfaction:.1f}⭐")

    # Chat trends
    st.subheader("📈 Chat Trends")

    # Mock trend data
    trend_data = {
        "Today": {"chats": 12, "responses": 45, "rating": 4.8},
        "Yesterday": {"chats": 8, "responses": 32, "rating": 4.6},
        "This Week": {"chats": 45, "responses": 180, "rating": 4.7},
        "This Month": {"chats": 180, "responses": 720, "rating": 4.5}
    }

    for period, data in trend_data.items():
        with st.expander(f"📅 {period}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("New Chats", data["chats"])
            with col2:
                st.metric("Total Messages", data["responses"])
            with col3:
                st.metric("Avg Rating", f"{data['rating']}⭐")

    # Response time analysis
    st.subheader("⏱️ Response Time Analysis")

    response_times = get_response_time_distribution(username)

    if response_times:
        for time_range, count in response_times.items():
            st.write(f"**{time_range}:** {count} responses")
    else:
        st.info("No response time data available")

    # Popular chat times
    st.subheader("🕐 Popular Chat Times")

    # Mock popular times
    popular_times = [
        {"hour": "9:00 AM", "chats": 15},
        {"hour": "10:00 AM", "chats": 22},
        {"hour": "11:00 AM", "chats": 18},
        {"hour": "2:00 PM", "chats": 25},
        {"hour": "3:00 PM", "chats": 20},
        {"hour": "4:00 PM", "chats": 16}
    ]

    cols = st.columns(3)
    for i, time_data in enumerate(popular_times):
        with cols[i % 3]:
            st.metric(time_data["hour"], f"{time_data['chats']} chats")

def get_active_chats(username):
    """Get active chats for the artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT
                CASE
                    WHEN cm.sender_id = (SELECT id FROM users WHERE username = ?) THEN cm.receiver_id
                    ELSE cm.sender_id
                END as other_user_id,
                u.username as customer_name,
                u.role,
                MAX(cm.created_at) as last_message_time,
                (SELECT message FROM chat_messages
                 WHERE (sender_id = (SELECT id FROM users WHERE username = ?) AND receiver_id = u.id)
                    OR (sender_id = u.id AND receiver_id = (SELECT id FROM users WHERE username = ?))
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                (SELECT COUNT(*) FROM chat_messages
                 WHERE receiver_id = (SELECT id FROM users WHERE username = ?)
                   AND sender_id = u.id AND is_read = FALSE) as unread_count,
                (SELECT COUNT(*) FROM chat_messages
                 WHERE (sender_id = (SELECT id FROM users WHERE username = ?) AND receiver_id = u.id)
                    OR (sender_id = u.id AND receiver_id = (SELECT id FROM users WHERE username = ?))) as total_messages
            FROM chat_messages cm
            JOIN users u ON (u.id = cm.sender_id OR u.id = cm.receiver_id)
            WHERE (cm.sender_id = (SELECT id FROM users WHERE username = ?)
                   OR cm.receiver_id = (SELECT id FROM users WHERE username = ?))
              AND u.id != (SELECT id FROM users WHERE username = ?)
              AND u.role = 'user'
            GROUP BY other_user_id, u.username, u.role
            ORDER BY last_message_time DESC
        """, (username, username, username, username, username, username, username, username, username))

        chats = cursor.fetchall()
        conn.close()

        return [dict(chat) for chat in chats]
    except Exception as e:
        st.error(f"Error getting active chats: {e}")
        return []

def get_all_conversations(username, status_filter="All", date_filter="All Time", sort_by="Recent"):
    """Get all conversations with filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT
                CASE
                    WHEN cm.sender_id = (SELECT id FROM users WHERE username = ?) THEN cm.receiver_id
                    ELSE cm.sender_id
                END as other_user_id,
                u.username as customer_name,
                u.role,
                MAX(cm.created_at) as last_activity,
                (SELECT message FROM chat_messages
                 WHERE (sender_id = (SELECT id FROM users WHERE username = ?) AND receiver_id = u.id)
                    OR (sender_id = u.id AND receiver_id = (SELECT id FROM users WHERE username = ?))
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                (SELECT COUNT(*) FROM chat_messages
                 WHERE (sender_id = (SELECT id FROM users WHERE username = ?) AND receiver_id = u.id)
                    OR (sender_id = u.id AND receiver_id = (SELECT id FROM users WHERE username = ?))) as message_count,
                0 as archived  -- Mock archived status
            FROM chat_messages cm
            JOIN users u ON (u.id = cm.sender_id OR u.id = cm.receiver_id)
            WHERE (cm.sender_id = (SELECT id FROM users WHERE username = ?)
                   OR cm.receiver_id = (SELECT id FROM users WHERE username = ?))
              AND u.id != (SELECT id FROM users WHERE username = ?)
              AND u.role = 'user'
        """

        params = [username] * 9

        # Apply filters
        if status_filter != "All":
            # Mock filter implementation
            pass

        if date_filter != "All Time":
            if date_filter == "Today":
                query += " AND DATE(cm.created_at) = DATE('now')"
            elif date_filter == "This Week":
                query += " AND DATE(cm.created_at) >= DATE('now', '-7 days')"
            elif date_filter == "This Month":
                query += " AND DATE(cm.created_at) >= DATE('now', 'start of month')"

        # Apply sorting
        if sort_by == "Recent":
            query += " ORDER BY last_activity DESC"
        elif sort_by == "Most Messages":
            query += " ORDER BY message_count DESC"
        elif sort_by == "Customer Name":
            query += " ORDER BY customer_name ASC"

        cursor.execute(query, params)
        conversations = cursor.fetchall()
        conn.close()

        return [dict(conv) for conv in conversations]
    except Exception as e:
        st.error(f"Error getting conversations: {e}")
        return []

def send_quick_reply(artist_username, customer_id, message):
    """Send a quick reply message"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO chat_messages (sender_id, receiver_id, message, message_type, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, 'text', datetime('now'))
        """, (artist_username, customer_id, message))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error sending quick reply: {e}")
        return False

def mark_chat_read(artist_username, customer_id):
    """Mark chat messages as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE chat_messages SET is_read = TRUE
            WHERE receiver_id = (SELECT id FROM users WHERE username = ?)
              AND sender_id = ?
        """, (artist_username, customer_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error marking chat as read: {e}")
        return False

def archive_chat(artist_username, customer_id):
    """Archive a chat conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mock archive implementation - in real app would have archive table
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'chat_archived', ?, datetime('now'))
        """, (artist_username, f"Chat with customer {customer_id} archived"))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error archiving chat: {e}")
        return False

def get_total_chat_count(username):
    """Get total chat count for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(DISTINCT
                CASE
                    WHEN sender_id = (SELECT id FROM users WHERE username = ?) THEN receiver_id
                    ELSE sender_id
                END)
            FROM chat_messages
            WHERE sender_id = (SELECT id FROM users WHERE username = ?)
               OR receiver_id = (SELECT id FROM users WHERE username = ?)
        """, (username, username, username))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error getting total chat count: {e}")
        return 0

def get_active_chat_count(username):
    """Get active chat count for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(DISTINCT
                CASE
                    WHEN sender_id = (SELECT id FROM users WHERE username = ?) THEN receiver_id
                    ELSE sender_id
                END)
            FROM chat_messages
            WHERE (sender_id = (SELECT id FROM users WHERE username = ?)
                   OR receiver_id = (SELECT id FROM users WHERE username = ?))
              AND DATE(created_at) >= DATE('now', '-7 days')
        """, (username, username, username))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        st.error(f"Error getting active chat count: {e}")
        return 0

def get_avg_response_time(username):
    """Get average response time for artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mock implementation - would calculate actual response times
        cursor.execute("""
            SELECT AVG(CASE
                WHEN sender_id = (SELECT id FROM users WHERE username = ?) THEN 1
                ELSE 0
            END) * 10 as avg_response_time  -- Mock calculation
            FROM chat_messages
            WHERE (sender_id = (SELECT id FROM users WHERE username = ?)
                   OR receiver_id = (SELECT id FROM users WHERE username = ?))
              AND DATE(created_at) >= DATE('now', '-30 days')
        """, (username, username, username))

        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 15.0  # Default 15 minutes
    except Exception as e:
        st.error(f"Error getting average response time: {e}")
        return 15.0

def get_customer_satisfaction(username):
    """Get customer satisfaction rating"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mock implementation - would get from reviews
        return 4.5
    except Exception as e:
        st.error(f"Error getting customer satisfaction: {e}")
        return 4.0

def get_response_time_distribution(username):
    """Get response time distribution"""
    try:
        # Mock data
        return {
            "< 5 minutes": 45,
            "5-15 minutes": 78,
            "15-30 minutes": 32,
            "30-60 minutes": 15,
            "> 60 minutes": 8
        }
    except Exception as e:
        st.error(f"Error getting response time distribution: {e}")
        return {}

def archive_conversation(artist_username, customer_id):
    """Archive a conversation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'conversation_archived', ?, datetime('now'))
        """, (artist_username, f"Conversation with customer {customer_id} archived"))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error archiving conversation: {e}")
        return False

def flag_conversation(artist_username, customer_id):
    """Flag a conversation for review"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at)
            VALUES ((SELECT id FROM users WHERE username = ?), 'conversation_flagged', ?, datetime('now'))
        """, (artist_username, f"Conversation with customer {customer_id} flagged"))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error flagging conversation: {e}")
        return False
