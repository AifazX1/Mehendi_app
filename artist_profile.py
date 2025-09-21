import streamlit as st
from datetime import datetime
from database import get_db_connection, update_artist_profile, get_user_profile
from utils import validate_email, validate_phone, sanitize_input

def artist_profile_management(username, artist_profile):
    """Complete artist profile management interface"""
    st.subheader("👤 Manage Your Profile")

    # Profile completion status
    completion_percentage = calculate_profile_completion(artist_profile)
    st.progress(completion_percentage / 100)
    st.write(f"Profile Completion: {completion_percentage}%")

    if completion_percentage < 100:
        st.warning("Complete your profile to get more bookings!")

    # Profile editing form
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Basic Information**")
            name = st.text_input("Full Name", value=artist_profile.get('name', ''))
            email = st.text_input("Email", value=artist_profile.get('email', ''))
            phone = st.text_input("Phone", value=artist_profile.get('phone', ''))
            address = st.text_area("Address", value=artist_profile.get('address', ''), height=100)

        with col2:
            st.write("**Professional Details**")
            experience_years = st.number_input("Years of Experience",
                min_value=0, max_value=50, value=artist_profile.get('experience_years', 0))

            specializations = st.text_area("Specializations (comma-separated)",
                value=artist_profile.get('specializations', ''),
                help="e.g., Bridal Mehndi, Arabic Design, Traditional, etc.")

            price_range = st.text_input("Price Range",
                value=artist_profile.get('price_range', '₹500-1500'),
                help="e.g., ₹500-1500, ₹1000-3000")

        st.write("**Additional Information**")
        col3, col4 = st.columns(2)

        with col3:
            bio = st.text_area("Bio/About You",
                value=artist_profile.get('bio', ''),
                height=100,
                help="Tell customers about your style, experience, and what makes you unique")

            areas_covered = st.text_area("Areas Covered",
                value=artist_profile.get('areas_covered', ''),
                help="Cities/areas where you provide services")

        with col4:
            portfolio_url = st.text_input("Portfolio Website/Instagram",
                value=artist_profile.get('portfolio_url', ''),
                help="Link to your portfolio or social media")

            languages = st.multiselect("Languages Spoken",
                ["Hindi", "English", "Punjabi", "Gujarati", "Marathi", "Tamil", "Telugu", "Other"],
                default=artist_profile.get('languages', ['Hindi']).split(', ') if artist_profile.get('languages') else ['Hindi'])

        # Submit button
        submitted = st.form_submit_button("💾 Save Profile", type="primary")

        if submitted:
            if not name or not phone:
                st.error("Name and phone are required fields")
            elif email and not validate_email(email):
                st.error("Please enter a valid email address")
            elif phone and not validate_phone(phone):
                st.error("Please enter a valid phone number")
            else:
                # Prepare profile data
                profile_data = {
                    'name': sanitize_input(name),
                    'email': sanitize_input(email),
                    'phone': sanitize_input(phone),
                    'address': sanitize_input(address),
                    'experience_years': experience_years,
                    'specializations': sanitize_input(specializations),
                    'price_range': sanitize_input(price_range),
                    'bio': sanitize_input(bio),
                    'areas_covered': sanitize_input(areas_covered),
                    'portfolio_url': sanitize_input(portfolio_url),
                    'languages': ', '.join(languages)
                }

                # Update profile
                success = update_artist_profile(username, profile_data)

                if success:
                    st.success("✅ Profile updated successfully!")
                    st.balloons()

                    # Refresh profile data
                    st.rerun()
                else:
                    st.error("Failed to update profile. Please try again.")

    # Display current profile information
    st.subheader("📋 Current Profile Information")

    if artist_profile:
        display_profile_info(artist_profile)

    # Profile actions
    st.subheader("🎯 Profile Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📸 Upload Portfolio Images", key="upload_portfolio"):
            st.info("Portfolio upload feature would be implemented here")

    with col2:
        if st.button("⭐ Request Featured Status", key="request_featured"):
            request_featured_status(username)
            st.success("Featured status request submitted!")

    with col3:
        if st.button("📊 View Public Profile", key="view_public"):
            st.info("Public profile view would be implemented here")

def calculate_profile_completion(artist_profile):
    """Calculate profile completion percentage"""
    required_fields = ['name', 'phone', 'address', 'bio', 'specializations', 'price_range']
    optional_fields = ['email', 'experience_years', 'portfolio_url', 'areas_covered']

    completed_required = sum(1 for field in required_fields if artist_profile.get(field))
    completed_optional = sum(1 for field in optional_fields if artist_profile.get(field))

    total_fields = len(required_fields) + len(optional_fields)
    completed_fields = completed_required + completed_optional

    return int((completed_fields / total_fields) * 100)

def display_profile_info(artist_profile):
    """Display current profile information in a nice format"""
    col1, col2 = st.columns(2)

    with col1:
        st.write("**👤 Personal Information**")
        st.write(f"**Name:** {artist_profile.get('name', 'Not set')}")
        st.write(f"**Email:** {artist_profile.get('email', 'Not set')}")
        st.write(f"**Phone:** {artist_profile.get('phone', 'Not set')}")
        st.write(f"**Address:** {artist_profile.get('address', 'Not set')}")

        st.write("**🎨 Professional Information**")
        st.write(f"**Experience:** {artist_profile.get('experience_years', 0)} years")
        st.write(f"**Specializations:** {artist_profile.get('specializations', 'Not set')}")
        st.write(f"**Price Range:** {artist_profile.get('price_range', 'Not set')}")

    with col2:
        st.write("**📖 Additional Information**")
        st.write(f"**Bio:** {artist_profile.get('bio', 'Not set')}")
        st.write(f"**Areas Covered:** {artist_profile.get('areas_covered', 'Not set')}")
        st.write(f"**Portfolio:** {artist_profile.get('portfolio_url', 'Not set')}")
        st.write(f"**Languages:** {artist_profile.get('languages', 'Not set')}")

        # Rating and status
        st.write("**⭐ Performance**")
        rating = artist_profile.get('rating', 0)
        st.write(f"**Rating:** {rating:.1f}/5.0")
        st.write(f"**Status:** {artist_profile.get('status', 'pending').title()}")

def request_featured_status(username):
    """Request featured artist status"""
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

        # Update status to request featured
        cursor.execute("""
            UPDATE artists SET
            status = 'featured_requested',
            updated_at = datetime('now')
            WHERE id = ?
        """, (artist_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error requesting featured status: {e}")
        return False

def get_artist_reviews(username):
    """Get reviews for the artist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.*, u.username as reviewer_name, b.appointment_date
            FROM reviews r
            JOIN bookings b ON r.booking_id = b.id
            JOIN artists a ON b.artist_id = a.id
            JOIN users u ON b.user_id = u.id
            WHERE a.user_id = (SELECT id FROM users WHERE username = ?)
            ORDER BY r.created_at DESC
        """, (username,))

        reviews = cursor.fetchall()
        conn.close()

        return [dict(review) for review in reviews]
    except Exception as e:
        st.error(f"Error getting reviews: {e}")
        return []

def display_artist_reviews(username):
    """Display artist reviews"""
    st.subheader("⭐ Customer Reviews")

    reviews = get_artist_reviews(username)

    if reviews:
        for review in reviews:
            with st.expander(f"⭐ {review['rating']}/5 - {review['reviewer_name']} ({review['appointment_date']})"):
                st.write(f"**Rating:** {review['rating']}/5")
                if review['review_text']:
                    st.write(f"**Review:** {review['review_text']}")
                st.caption(f"Reviewed on: {review['created_at']}")
    else:
        st.info("No reviews yet. Complete some bookings to get reviews!")

def artist_verification_status(username):
    """Display artist verification status"""
    st.subheader("✅ Verification Status")

    artist_profile = get_user_profile(username)

    if not artist_profile:
        st.error("Profile not found")
        return

    # Mock verification items
    verification_items = {
        "Profile Completion": artist_profile.get('name') and artist_profile.get('phone'),
        "Email Verification": artist_profile.get('email'),
        "Phone Verification": artist_profile.get('phone'),
        "Portfolio Upload": artist_profile.get('portfolio_url'),
        "Minimum Reviews": len(get_artist_reviews(username)) >= 3,
        "Background Check": False  # Mock - would be real verification
    }

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Required for Basic Verification:**")
        for item, completed in list(verification_items.items())[:3]:
            status_icon = "✅" if completed else "❌"
            st.write(f"{status_icon} {item}")

    with col2:
        st.write("**Required for Premium Verification:**")
        for item, completed in list(verification_items.items())[3:]:
            status_icon = "✅" if completed else "❌"
            st.write(f"{status_icon} {item}")

    # Overall verification status
    basic_completed = sum(list(verification_items.values())[:3])
    premium_completed = sum(list(verification_items.values()))

    if premium_completed == len(verification_items):
        st.success("🎉 Premium Artist Status - All verifications complete!")
    elif basic_completed >= 3:
        st.success("✅ Basic Artist Status - Ready to receive bookings!")
    else:
        st.warning("⚠️ Complete basic verification to start receiving bookings")

def artist_portfolio_management(username):
    """Manage artist portfolio images and samples"""
    st.subheader("📸 Portfolio Management")

    # Upload new images
    st.write("**Upload Portfolio Images**")
    uploaded_files = st.file_uploader(
        "Choose images",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload your best mehndi design samples"
    )

    if uploaded_files:
        for file in uploaded_files:
            st.image(file, caption=file.name, width=200)

        if st.button("💾 Save to Portfolio"):
            st.success(f"Saved {len(uploaded_files)} images to portfolio!")

    # Display existing portfolio
    st.write("**Current Portfolio**")
    col1, col2, col3, col4 = st.columns(4)

    # Mock portfolio images
    for i in range(8):
        with col1 if i % 4 == 0 else col2 if i % 4 == 1 else col3 if i % 4 == 2 else col4:
            st.image("https://via.placeholder.com/150", caption=f"Design {i+1}")

            if st.button(f"🗑️", key=f"delete_{i}"):
                st.warning(f"Delete Design {i+1}")

    # Portfolio statistics
    st.write("**Portfolio Statistics**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Designs", "8")
    with col2:
        st.metric("Views This Month", "245")
    with col3:
        st.metric("Downloads", "12")
