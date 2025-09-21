import streamlit as st
from datetime import datetime, date, time, timedelta
from database import get_db_connection, create_booking, get_user_bookings, get_artist_availability, get_nearby_artists
import pandas as pd

def booking_system():
    st.subheader("Book Your Mehndi Appointment")

    tab1, tab2 = st.tabs(["📅 Book New", "📋 My Bookings"])

    with tab1:
        book_new_appointment()

    with tab2:
        my_bookings()

def book_new_appointment():
    st.write("Find and book appointments with mehndi artists")

    # Location input for finding artists
    location = st.text_input("Enter your location to find nearby artists", placeholder="Enter city, area, or full address")

    if location:
        # Get real artists from database
        artists = get_nearby_artists(location)

        if artists:
            # Artist selection
            st.subheader("Select Artist")

            artist_options = []
            for artist in artists:
                rating = artist.get('avg_rating', 0)
                rating_display = f"{rating:.1f}" if rating else "New"
                price_range = artist.get('price_range', '₹500-1500')
                # Mock distance for now - would use geocoding
                distance = f"{artists.index(artist) + 1}.0 km"

                artist_options.append(f"{artist['name']} (⭐{rating_display} • {price_range} • {distance})")

            selected_artist_option = st.selectbox(
                "Choose an artist",
                options=artist_options,
                key="artist_select"
            )

            if selected_artist_option:
                # Get the selected artist
                selected_index = artist_options.index(selected_artist_option)
                selected_artist = artists[selected_index]
                artist_id = selected_artist['id']

        # Date selection
        st.subheader("Select Date")
        selected_date = st.date_input(
            "Choose appointment date",
            min_value=date.today(),
            max_value=date.today() + timedelta(days=30),
            key="date_select"
        )

        if selected_date:
            # Time slots
            st.subheader("Available Time Slots")

            # Mock available slots - in real app, this would come from database
            available_slots = [
                "09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"
            ]

            cols = st.columns(3)
            selected_slot = None

            for i, slot in enumerate(available_slots):
                with cols[i % 3]:
                    if st.button(slot, key=f"slot_{i}"):
                        selected_slot = slot

            if selected_slot:
                st.success(f"Selected: {selected_slot} on {selected_date}")

                # Booking details
                st.subheader("Booking Details")

                with st.form("booking_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        customer_name = st.text_input("Your Name")
                        phone = st.text_input("Phone Number")
                        email = st.text_input("Email")

                    with col2:
                        mehndi_type = st.selectbox("Mehndi Type", [
                            "Bridal Mehndi", "Engagement Mehndi", "Party Mehndi",
                            "Festival Mehndi", "Arabic Design", "Traditional Design"
                        ])
                        special_requests = st.text_area("Special Requests/Design References")

                # Price calculation using artist's price range
                price_range = selected_artist.get('price_range', '₹500-1500')
                # Extract minimum price from range for estimation
                try:
                    min_price = int(price_range.split('-')[0].replace('₹', '').strip())
                except:
                    min_price = 500
                st.write(f"**Estimated Price:** ₹{min_price}")

                submit_booking = st.form_submit_button("Confirm Booking")

                if submit_booking:
                        if not customer_name or not phone:
                            st.error("Please fill in all required fields")
                        else:
                            # Create booking in database
                            booking_id = create_booking(
                                user_id=st.session_state.user_id if 'user_id' in st.session_state else 1,  # Use actual user ID
                                artist_id=artist_id,
                                appointment_date=selected_date,
                                start_time=selected_slot,
                                end_time=(datetime.strptime(selected_slot, "%I:%M %p") + timedelta(hours=2)).strftime("%I:%M %p"),
                                amount=min_price,
                                notes=special_requests
                            )

                            if booking_id:
                                st.success("🎉 Booking confirmed!")
                                st.write(f"**Booking ID:** {booking_id}")
                                st.write(f"**Artist:** {selected_artist['name']}")
                                st.write(f"**Date:** {selected_date}")
                                st.write(f"**Time:** {selected_slot}")
                                st.write(f"**Amount:** ₹{min_price}")

                                # Show next steps
                                st.info("📱 You'll receive a confirmation message shortly. The artist will contact you to discuss the design.")
                            else:
                                st.error("Failed to create booking. Please try again.")

def my_bookings():
    st.subheader("My Bookings")

    # Get real bookings from database
    user_id = st.session_state.user_id if 'user_id' in st.session_state else 1
    bookings = get_user_bookings(user_id)

    if bookings:
        for booking in bookings:
            with st.expander(f"Booking #{booking['id']} - {booking['artist_name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Artist:** {booking['artist_name']}")
                    st.write(f"**Date:** {booking['appointment_date']}")
                    st.write(f"**Time:** {booking['start_time']}")
                    st.write(f"**Amount:** ₹{booking['amount']}")

                with col2:
                    status_color = {
                        "pending": "🟡",
                        "confirmed": "🟢",
                        "completed": "✅",
                        "cancelled": "❌"
                    }

                    st.write(f"**Status:** {status_color.get(booking['status'], '❓')} {booking['status'].title()}")

                    # Action buttons based on status
                    if booking['status'] == 'confirmed':
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Cancel", key=f"cancel_{booking['id']}"):
                                st.warning("Booking cancelled")
                                st.rerun()
                        with col_b:
                            if st.button("Reschedule", key=f"reschedule_{booking['id']}"):
                                st.info("Reschedule functionality would be here")

                    elif booking['status'] == 'completed':
                        if st.button("Rate Artist", key=f"rate_{booking['id']}"):
                            st.info("Rating system would be here")

    else:
        st.info("No bookings found. Book your first appointment!")

def artist_availability_management():
    """Artist availability management interface"""
    st.subheader("Manage Your Availability")

    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=date.today())
    with col2:
        end_date = st.date_input("To Date", value=date.today() + timedelta(days=7))

    # Time slots
    st.subheader("Set Available Time Slots")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:
        with st.expander(f"{day} - Set Availability"):
            col1, col2 = st.columns(2)

            with col1:
                start_time = st.time_input(f"Start Time ({day})", value=time(9, 0))
                end_time = st.time_input(f"End Time ({day})", value=time(17, 0))

            with col2:
                is_available = st.checkbox(f"Available on {day}", value=True)

                if st.button(f"Save {day}", key=f"save_{day}"):
                    st.success(f"{day} availability updated!")

    # Bulk actions
    st.subheader("Bulk Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Mark All Available"):
            st.success("All days marked as available")

    with col2:
        if st.button("Mark All Unavailable"):
            st.success("All days marked as unavailable")

    with col3:
        if st.button("Copy This Week to Next"):
            st.success("Schedule copied to next week")

def get_available_slots(artist_id, date):
    """Get available time slots for an artist on a specific date"""
    # Mock implementation - in real app, this would query the database
    base_slots = [
        "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
    ]

    # Mock booked slots
    booked_slots = ["11:00 AM", "03:00 PM"]

    return [slot for slot in base_slots if slot not in booked_slots]
