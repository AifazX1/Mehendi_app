import streamlit as st
from datetime import datetime
from database import get_db_connection
import time

import streamlit as st
from datetime import datetime
from database import get_db_connection
import time

def get_artist_location(artist_id):
    """Fetch artist location (address) from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT address FROM artists WHERE id = ?", (artist_id,))
        result = cursor.fetchone()
        conn.close()
        if result and result[0]:
            return result[0]
        return None
    except Exception as e:
        st.error(f"Error fetching artist location: {e}")
        return None

def chat_interface():
    st.subheader("💬 Chat with Artists")

    # Artist selection for chat
    st.write("Select an artist to start chatting:")

    # Get available artists for chat
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.id, a.name, u.is_online
        FROM artists a
        JOIN users u ON a.user_id = u.id
        WHERE a.status = 'approved'
        ORDER BY u.is_online DESC, a.name
    """)

    artists = cursor.fetchall()
    conn.close()

    if artists:
        artist_options = [f"{artist['name']} {'🟢' if artist['is_online'] else '🔴'}" for artist in artists]

        selected_artist_option = st.selectbox(
            "Choose an artist to chat with",
            options=artist_options,
            key="chat_artist_select"
        )

        if selected_artist_option:
            # Get selected artist ID
            selected_index = artist_options.index(selected_artist_option)
            selected_artist = artists[selected_index]

            # Load chat history
            current_user_id = st.session_state.user_id if 'user_id' in st.session_state else 1
            chat_history = get_chat_history(current_user_id, selected_artist['id'])

            # Display chat messages
            st.write(f"**Chatting with: {selected_artist['name']}**")

            # Display artist location on map if available
            artist_location = get_artist_location(selected_artist['id'])
            if artist_location:
                st.write("**Artist Location:**")
                # Use OpenStreetMap embed with query for the address
                map_url = f"https://www.openstreetmap.org/search?query={artist_location.replace(' ', '%20')}"
                st.markdown(f"[View on Map]({map_url})", unsafe_allow_html=True)
            else:
                st.info("Artist location not available.")

            if chat_history:
                for message in chat_history:
                    if message['sender_id'] == current_user_id:
                        with st.chat_message("user"):
                            st.write(message['message'])
                            st.caption(message['created_at'])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message['message'])
                            st.caption(f"{selected_artist['name']} • {message['created_at']}")
            else:
                st.info("No previous messages. Start the conversation!")

            # Chat input
            user_input = st.chat_input("Type your message...")

            if user_input:
                # Send message to database
                success = send_message(
                    sender_id=current_user_id,
                    receiver_id=selected_artist['id'],
                    message=user_input
                )

                if success:
                    st.rerun()  # Refresh to show new message
                else:
                    st.error("Failed to send message")
    else:
        st.info("No artists available for chat at the moment.")

def send_message(sender_id, receiver_id, message, message_type="text"):
    """Send a message between users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO chat_messages (sender_id, receiver_id, message, message_type, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (sender_id, receiver_id, message, message_type))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False

def get_chat_history(user_id, other_user_id):
    """Get chat history between two users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT cm.*, u.username as sender_name
            FROM chat_messages cm
            JOIN users u ON cm.sender_id = u.id
            WHERE (cm.sender_id = ? AND cm.receiver_id = ?)
               OR (cm.sender_id = ? AND cm.receiver_id = ?)
            ORDER BY cm.created_at ASC
        """, (user_id, other_user_id, other_user_id, user_id))

        messages = cursor.fetchall()
        conn.close()

        return [dict(message) for message in messages]
    except Exception as e:
        st.error(f"Error getting chat history: {e}")
        return []

def get_unread_count(user_id):
    """Get count of unread messages for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM chat_messages
            WHERE receiver_id = ? AND is_read = FALSE
        """, (user_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count
    except Exception as e:
        st.error(f"Error getting unread count: {e}")
        return 0

def mark_messages_read(user_id, sender_id):
    """Mark messages as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE chat_messages SET is_read = TRUE
            WHERE receiver_id = ? AND sender_id = ?
        """, (user_id, sender_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error marking messages as read: {e}")
        return False

def get_recent_chats(user_id):
    """Get recent chats for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT
                CASE
                    WHEN cm.sender_id = ? THEN cm.receiver_id
                    ELSE cm.sender_id
                END as other_user_id,
                u.username,
                u.role,
                MAX(cm.created_at) as last_message_time,
                (SELECT message FROM chat_messages
                 WHERE (sender_id = ? AND receiver_id = u.id)
                    OR (sender_id = u.id AND receiver_id = ?)
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                (SELECT COUNT(*) FROM chat_messages
                 WHERE receiver_id = ? AND sender_id = u.id AND is_read = FALSE) as unread_count
            FROM chat_messages cm
            JOIN users u ON (u.id = cm.sender_id OR u.id = cm.receiver_id)
            WHERE (cm.sender_id = ? OR cm.receiver_id = ?)
              AND u.id != ?
            GROUP BY other_user_id, u.username, u.role
            ORDER BY last_message_time DESC
        """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id))

        chats = cursor.fetchall()
        conn.close()

        return [dict(chat) for chat in chats]
    except Exception as e:
        st.error(f"Error getting recent chats: {e}")
        return []

def chat_management():
    """Chat management interface for admin"""
    st.subheader("Chat Management")

    # Mock flagged chats
    flagged_chats = [
        {
            "id": 1,
            "users": "user123 ↔ artist456",
            "reason": "Inappropriate language",
            "flagged_by": "System",
            "date": "2024-01-10"
        },
        {
            "id": 2,
            "users": "user789 ↔ artist321",
            "reason": "Spam content",
            "flagged_by": "User report",
            "date": "2024-01-09"
        }
    ]

    for chat in flagged_chats:
        with st.expander(f"🚩 {chat['users']} - {chat['reason']}"):
            st.write(f"**Flagged by:** {chat['flagged_by']}")
            st.write(f"**Date:** {chat['date']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("View Chat", key=f"view_{chat['id']}"):
                    st.info("Chat viewer would be here")
            with col2:
                if st.button("Warn Users", key=f"warn_{chat['id']}"):
                    st.success("Warning sent to users")
            with col3:
                if st.button("Block Users", key=f"block_{chat['id']}"):
                    st.error("Users blocked from chat")

def image_sharing_interface():
    """Interface for sharing design reference images"""
    st.subheader("📸 Share Design References")

    uploaded_file = st.file_uploader(
        "Upload design reference images",
        type=['png', 'jpg', 'jpeg'],
        help="Share images of designs you like for reference"
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Design Reference", width=300)
        st.success("Image uploaded successfully!")

        if st.button("Send to Artist"):
            st.info("Image sent to artist for reference!")

    # Mock shared images
    st.subheader("Previously Shared Images")
    col1, col2, col3 = st.columns(3)

    for i in range(3):
        with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
            st.image("https://via.placeholder.com/150", caption=f"Design {i+1}")
