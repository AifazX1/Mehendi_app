import streamlit as st
from auth import authenticate_user, create_user, hash_password
from database import init_database, get_user_role, get_nearby_artists
from admin import admin_dashboard
from booking import booking_system
from chat import chat_interface
from artist import artist_dashboard as artist_main_dashboard
import sqlite3
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import geocode_location, get_default_coordinates

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="Mehndi App",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #8B4513;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #8B4513;
        text-align: center;
    }
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    .artist-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #8B4513;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None

    # Sidebar navigation
    st.sidebar.markdown('<div class="sidebar-header">🪔 Mehndi App</div>', unsafe_allow_html=True)

    if st.session_state.user is None:
        # Login page
        st.markdown('<h1 class="main-header">Welcome to Mehndi App</h1>', unsafe_allow_html=True)

        login_type = st.selectbox("Login as:", ["User", "Artist", "Admin"])

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                user = authenticate_user(username, password, login_type.lower())
                if user:
                    st.session_state.user = username
                    st.session_state.role = login_type.lower()
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        # Registration section
        st.markdown("---")
        st.subheader("New User? Register here")

        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_type = st.selectbox("Register as:", ["User", "Artist"])

            register_submit = st.form_submit_button("Register")

            if register_submit:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success = create_user(new_username, new_password, register_type.lower())
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")

    else:
        # Main application
        st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
        st.sidebar.write(f"Role: **{st.session_state.role.title()}**")

        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

        # Role-based navigation
        if st.session_state.role == "admin":
            admin_dashboard()
        elif st.session_state.role == "artist":
            artist_main_dashboard()
        else:
            user_dashboard()

def user_dashboard():
    st.markdown('<h1 class="main-header">User Dashboard</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "💬 Chat", "📅 Bookings", "⭐ Reviews"])

    with tab1:
        st.subheader("Find Mehndi Artists Near You")
        # Location input
        location = st.text_input("Enter your location", placeholder="Enter city, area, or full address")

        if location:
            st.write(f"Searching for artists near: {location}")

            # Get real artists from database
            artists = get_nearby_artists(location)

            if artists:
                # Create map with artist locations
                st.subheader("📍 Artists Near You")
                create_artist_map(artists, location)

                # Display artist listings
                st.subheader("Available Artists")
                col1, col2, col3 = st.columns(3)

                for i, artist in enumerate(artists[:6]):  # Show first 6 artists
                    with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
                        with st.container():
                            # Get rating display
                            rating = artist.get('avg_rating', 0)
                            rating_display = f"{rating:.1f}" if rating else "New"

                            # Get price range
                            price_range = artist.get('price_range', '₹500-1500')

                            # Get distance (mock for now, would use geocoding)
                            distance = f"{i+1}.{i%3} km away"

                            # Online status
                            is_online = artist.get('is_online', False)
                            status_icon = "🟢" if is_online else "🔴"
                            status_text = "Online" if is_online else "Offline"

                            st.markdown(f"""
                            <div class="artist-card">
                                <h4>{artist['name']}</h4>
                                <p>⭐ {rating_display}/5.0 • 💰 {price_range}</p>
                                <p>📍 {distance}</p>
                                <p class="status-{'online' if is_online else 'offline'}">{status_icon} {status_text}</p>
                                <p><strong>Experience:</strong> {artist.get('experience_years', 0)} years</p>
                                <p><strong>Specialization:</strong> {artist.get('specializations', 'General Mehndi')}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Action buttons
                            if st.button(f"View Profile", key=f"view_{artist['id']}"):
                                st.info(f"Profile view for {artist['name']} would be implemented here")

                            if st.button(f"Book Now", key=f"book_{artist['id']}"):
                                st.info(f"Booking system for {artist['name']} would be implemented here")
            else:
                st.info("No artists found in your area. Try expanding your search or check back later.")
                create_empty_map(location)

    with tab2:
        chat_interface()

    with tab3:
        booking_system()

    with tab4:
        st.subheader("Rate & Review Artists")
        st.write("Rating system would be implemented here")

def create_artist_map(artists, location):
    """Create a folium map with artist locations"""
    try:
        center_coords = geocode_location(location)
        if not center_coords:
            center_coords = get_default_coordinates()
            st.warning(f"Could not find coordinates for '{location}'. Using default location.")

        m = folium.Map(location=center_coords, zoom_start=12)

        for artist in artists:
            lat = center_coords[0] + (artists.index(artist) * 0.01)
            lng = center_coords[1] + (artists.index(artist) * 0.01)
            popup_content = f"""
            <b>{artist['name']}</b><br>
            ⭐ {artist.get('avg_rating', 0):.1f}/5.0<br>
            💰 {artist.get('price_range', '₹500-1500')}<br>
            📍 {artist.get('address', 'Address not available')}<br>
            {'🟢 Online' if artist.get('is_online', False) else '🔴 Offline'}
            """
            folium.Marker([lat, lng], popup=popup_content, tooltip=artist['name']).add_to(m)

        st_folium(m, width=700, height=400)

    except Exception as e:
        st.error(f"Error creating map: {e}")
        st.info("Map functionality would be displayed here")

def create_empty_map(location):
    """Create an empty map showing the search area"""
    try:
        center_coords = geocode_location(location)
        if not center_coords:
            center_coords = get_default_coordinates()
            st.warning(f"Could not find coordinates for '{location}'. Using default location.")

        m = folium.Map(location=center_coords, zoom_start=12)
        folium.Marker(center_coords, popup=f"Search area: {location}", tooltip="Your location",
                      icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
        st_folium(m, width=700, height=400)
    except Exception as e:
        st.error(f"Error creating map: {e}")
        st.info("Map functionality would be displayed here")

if __name__ == "__main__":
    main()

