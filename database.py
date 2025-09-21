import sqlite3
import os
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Database file path
DB_PATH = "mehndi_app.db"

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database with all tables"""
    try:
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'artist', 'admin')),
                email TEXT,
                phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME,
                is_online BOOLEAN DEFAULT FALSE
            )
        ''')

        # Artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                bio TEXT,
                experience_years INTEGER,
                specializations TEXT,
                price_range TEXT,
                portfolio_url TEXT,
                areas_covered TEXT,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
                rating REAL DEFAULT 0.0,
                total_reviews INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Artist availability table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artist_availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER REFERENCES artists(id),
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                is_available BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                artist_id INTEGER REFERENCES artists(id),
                appointment_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                amount REAL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER REFERENCES users(id),
                receiver_id INTEGER REFERENCES users(id),
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'image')),
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER REFERENCES bookings(id),
                user_id INTEGER REFERENCES users(id),
                artist_id INTEGER REFERENCES artists(id),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Admin logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER REFERENCES users(id),
                action TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create default admin user
        cursor.execute("SELECT id FROM users WHERE username = 'admin' AND role = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password, role, is_online)
                VALUES ('admin', ?, 'admin', FALSE)
            """, ('$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCaLbfQ4f7cHS3Wa',))  # password: admin123

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

def get_nearby_artists(location, filters=None):
    """Get artists near a location with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT a.*, u.is_online,
                   (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM reviews r WHERE r.artist_id = a.id) as review_count
            FROM artists a
            JOIN users u ON a.user_id = u.id
            WHERE a.status = 'approved'
        """

        params = []

        if filters:
            if 'style' in filters and filters['style']:
                query += " AND a.specializations LIKE ?"
                params.append(f"%{filters['style']}%")

            if 'max_price' in filters and filters['max_price']:
                query += " AND CAST(SUBSTR(a.price_range, INSTR(a.price_range, '-') + 1) AS INTEGER) <= ?"
                params.append(filters['max_price'])

            if 'min_rating' in filters and filters['min_rating']:
                query += " AND (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) >= ?"
                params.append(filters['min_rating'])

        query += " ORDER BY u.is_online DESC, avg_rating DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Error getting nearby artists: {e}")
        return []

def get_artist_availability(artist_id, date=None):
    """Get artist availability for a specific date or all dates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM artist_availability WHERE artist_id = ?"
        params = [artist_id]

        if date:
            query += " AND date = ?"
            params.append(date)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Error getting availability: {e}")
        return []

def create_booking(user_id, artist_id, appointment_date, start_time, end_time, amount, notes=""):
    """Create a new booking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookings (user_id, artist_id, appointment_date, start_time, end_time, amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, artist_id, appointment_date, start_time, end_time, amount, notes))

        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return booking_id
    except Exception as e:
        st.error(f"Error creating booking: {e}")
        return None

def get_user_bookings(user_id):
    """Get all bookings for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.*, a.name as artist_name, u.username as artist_username
            FROM bookings b
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE b.user_id = ?
            ORDER BY b.appointment_date DESC, b.start_time DESC
        """, (user_id,))

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Error getting bookings: {e}")
        return []

def log_admin_action(admin_id, action, details):
    """Log admin actions for audit trail"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action, details)
            VALUES (?, ?, ?)
        """, (admin_id, action, details))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error logging admin action: {e}")
        return False

def get_user_role(username):
    """Get user role from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None
    except Exception as e:
        st.error(f"Error getting user role: {e}")
        return None

def get_user_profile(username):
    """Get user profile from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.*, a.*
            FROM users u
            LEFT JOIN artists a ON u.id = a.user_id
            WHERE u.username = ?
        """, (username,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return dict(result)
        else:
            return None
    except Exception as e:
        st.error(f"Error getting user profile: {e}")
        return None

def update_artist_profile(username, profile_data):
    """Update artist profile in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user id
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        user_id = user_result[0]

        # Update artists table with profile_data dictionary keys and values
        set_clause = ", ".join([f"{key} = ?" for key in profile_data.keys()])
        values = list(profile_data.values())
        values.append(user_id)

        query = f"UPDATE artists SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        cursor.execute(query, values)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating artist profile: {e}")
        return False

def geocode_address(address):
    """Convert address to coordinates using geocoding"""
    try:
        geolocator = Nominatim(user_agent="mehndi_app")
        location = geolocator.geocode(address, timeout=10)

        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        st.warning(f"Geocoding error: {e}")
        return None

def calculate_distance(coord1, coord2):
    """Calculate distance between two coordinates in kilometers"""
    try:
        return geodesic(coord1, coord2).kilometers
    except Exception as e:
        st.warning(f"Distance calculation error: {e}")
        return None

def get_nearby_artists(location, max_distance=50, filters=None):
    """Get artists near a location with optional filters"""
    try:
        # Geocode the search location
        user_coords = geocode_address(location)
        if not user_coords:
            st.warning("Could not geocode the location. Using default search.")
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT a.*, u.is_online, u.username,
                   (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM reviews r WHERE r.artist_id = a.id) as review_count
            FROM artists a
            JOIN users u ON a.user_id = u.id
            WHERE a.status = 'approved'
        """

        params = []

        if filters:
            if 'style' in filters and filters['style']:
                query += " AND a.specializations LIKE ?"
                params.append(f"%{filters['style']}%")

            if 'max_price' in filters and filters['max_price']:
                query += " AND CAST(SUBSTR(a.price_range, INSTR(a.price_range, '-') + 1) AS INTEGER) <= ?"
                params.append(filters['max_price'])

            if 'min_rating' in filters and filters['min_rating']:
                query += " AND (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) >= ?"
                params.append(filters['min_rating'])

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Filter by distance and add distance information
        nearby_artists = []
        for row in results:
            artist_dict = dict(row)

            # Try to geocode artist address
            if artist_dict.get('address'):
                artist_coords = geocode_address(artist_dict['address'])
                if artist_coords:
                    distance = calculate_distance(user_coords, artist_coords)
                    if distance and distance <= max_distance:
                        artist_dict['distance'] = round(distance, 1)
                        nearby_artists.append(artist_dict)
                else:
                    # If geocoding fails, include artist with estimated distance
                    artist_dict['distance'] = 5.0  # Default distance
                    nearby_artists.append(artist_dict)
            else:
                # If no address, include with default distance
                artist_dict['distance'] = 5.0
                nearby_artists.append(artist_dict)

        # Sort by distance
        nearby_artists.sort(key=lambda x: x.get('distance', 999))

        return nearby_artists

    except Exception as e:
        st.error(f"Error getting nearby artists: {e}")
        return []

def get_artists_by_area(area_name):
    """Get artists in a specific area"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, u.is_online,
                   (SELECT AVG(r.rating) FROM reviews r WHERE r.artist_id = a.id) as avg_rating,
                   (SELECT COUNT(*) FROM reviews r WHERE r.artist_id = a.id) as review_count
            FROM artists a
            JOIN users u ON a.user_id = u.id
            WHERE a.areas_covered LIKE ?
               AND a.status = 'approved'
            ORDER BY u.is_online DESC, avg_rating DESC
        """, (f"%{area_name}%",))

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Error getting artists by area: {e}")
        return []
