import bcrypt
import sqlite3
from database import get_db_connection
import streamlit as st

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password, role):
    """Create a new user in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False

        # Insert new user
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (username, hashed_password, role))

        # If artist, create artist profile
        if role == 'artist':
            cursor.execute("""
                INSERT INTO artists (user_id, name, status)
                VALUES ((SELECT id FROM users WHERE username = ?), ?, 'pending')
            """, (username, username))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def authenticate_user(username, password, role):
    """Authenticate a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username = ? AND role = ?", (username, role))
        result = cursor.fetchone()
        conn.close()

        if result and verify_password(password, result[0]):
            return True
        return False
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False



def update_user_status(username, status):
    """Update user online status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET last_active = datetime('now'), is_online = ?
            WHERE username = ?
        """, (status, username))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating status: {e}")
        return False

def get_user_profile(username):
    """Get user profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.*, a.* FROM users u
            LEFT JOIN artists a ON u.id = a.user_id
            WHERE u.username = ?
        """, (username,))

        result = cursor.fetchone()
        conn.close()

        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    except Exception as e:
        st.error(f"Error getting profile: {e}")
        return None

def update_artist_profile(username, profile_data):
    """Update artist profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update artist table
        cursor.execute("""
            UPDATE artists SET
            name = ?, address = ?, phone = ?, bio = ?, experience_years = ?,
            specializations = ?, price_range = ?, portfolio_url = ?,
            areas_covered = ?, updated_at = datetime('now')
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        """, (
            profile_data.get('name'),
            profile_data.get('address'),
            profile_data.get('phone'),
            profile_data.get('bio'),
            profile_data.get('experience_years'),
            profile_data.get('specializations'),
            profile_data.get('price_range'),
            profile_data.get('portfolio_url'),
            profile_data.get('areas_covered'),
            username
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False
