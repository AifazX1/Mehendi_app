import streamlit as st
from datetime import datetime, timedelta
import re
import hashlib
from geopy.geocoders import Nominatim
import time

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^[\+]?[1-9][\d]{9,14}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', ''))

def format_price(price_range):
    """Format price range for display"""
    if not price_range:
        return "Price not set"

    try:
        min_price, max_price = price_range.split('-')
        return f"₹{min_price.strip()} - ₹{max_price.strip()}"
    except:
        return f"₹{price_range}"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (mock implementation)"""
    # Mock distance calculation
    return round(abs(lat1 - lat2) * 111 + abs(lon1 - lon2) * 111, 1)

def format_duration(start_time, end_time):
    """Format time duration for display"""
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    except:
        return "Duration not available"

def get_status_color(status):
    """Get color code for status"""
    colors = {
        'pending': '#ffc107',
        'confirmed': '#28a745',
        'completed': '#007bff',
        'cancelled': '#dc3545',
        'approved': '#28a745',
        'rejected': '#dc3545',
        'suspended': '#6c757d'
    }
    return colors.get(status.lower(), '#6c757d')

def get_status_icon(status):
    """Get icon for status"""
    icons = {
        'pending': '⏳',
        'confirmed': '✅',
        'completed': '🎉',
        'cancelled': '❌',
        'approved': '✅',
        'rejected': '❌',
        'suspended': '⏸️',
        'online': '🟢',
        'offline': '🔴'
    }
    return icons.get(status.lower(), '❓')

def generate_booking_id():
    """Generate unique booking ID"""
    timestamp = int(datetime.now().timestamp())
    return f"BK{timestamp}"

def format_date(date_obj, format_str="%B %d, %Y"):
    """Format date for display"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except:
            return date_obj
    return date_obj.strftime(format_str)

def format_time(time_obj, format_str="%I:%M %p"):
    """Format time for display"""
    if isinstance(time_obj, str):
        try:
            time_obj = datetime.strptime(time_obj, "%H:%M").time()
        except:
            return time_obj
    return time_obj.strftime(format_str)

def get_greeting():
    """Get time-based greeting"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

def calculate_rating_stats(reviews):
    """Calculate rating statistics"""
    if not reviews:
        return {"average": 0, "distribution": [0]*5, "total": 0}

    ratings = [r.get('rating', 0) for r in reviews]
    average = sum(ratings) / len(ratings) if ratings else 0
    total = len(ratings)

    distribution = [0] * 5
    for rating in ratings:
        if 1 <= rating <= 5:
            distribution[rating-1] += 1

    return {
        "average": round(average, 1),
        "distribution": distribution,
        "total": total
    }

def paginate_data(data, page_size=10, current_page=1):
    """Paginate data for display"""
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return data[start_idx:end_idx]

def search_artists(artists, query, filters=None):
    """Search and filter artists"""
    if not query and not filters:
        return artists

    filtered_artists = []

    for artist in artists:
        # Text search
        if query:
            search_text = f"{artist.get('name', '')} {artist.get('specializations', '')} {artist.get('bio', '')}".lower()
            if query.lower() not in search_text:
                continue

        # Apply filters
        if filters:
            if 'min_rating' in filters and artist.get('rating', 0) < filters['min_rating']:
                continue
            if 'max_price' in filters and artist.get('max_price', float('inf')) > filters['max_price']:
                continue
            if 'style' in filters and filters['style'] not in artist.get('specializations', ''):
                continue

        filtered_artists.append(artist)

    return filtered_artists

def export_data(data, format_type="csv"):
    """Export data to different formats"""
    if format_type == "csv":
        import pandas as pd
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    elif format_type == "json":
        import json
        return json.dumps(data, indent=2)
    else:
        return str(data)

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text

    # Remove potentially harmful characters
    dangerous_chars = ['<', '>', '&', '"', "'", '/']
    sanitized = text

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()

def get_file_hash(file_content):
    """Generate hash for file content"""
    return hashlib.md5(file_content).hexdigest()

def format_currency(amount, currency="₹"):
    """Format currency amount"""
    return f"{currency}{amount:,.2f}"

def get_time_slots(start_hour=9, end_hour=18, interval_minutes=60):
    """Generate time slots between hours"""
    slots = []
    current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")

    while current_time.hour < end_hour:
        end_time = current_time + timedelta(minutes=interval_minutes)
        slots.append({
            "start": current_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M"),
            "display": f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        })
        current_time = end_time

    return slots

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

    today = datetime.now()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def truncate_text(text, max_length=100):
    """Truncate text to maximum length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].strip() + "..."

def get_random_color():
    """Get random color for UI elements"""
    import random
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    return random.choice(colors)

def show_notification(message, type="info"):
    """Show notification message"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)

def create_download_link(data, filename, text="Download"):
    """Create download link for data"""
    import base64

    if isinstance(data, str):
        data = data.encode()

    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def geocode_location(location_name):
    """Convert location name to coordinates using geocoding"""
    try:
        geolocator = Nominatim(user_agent="mehndi_app")
        location = geolocator.geocode(location_name, timeout=10)

        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        st.warning(f"Geocoding error for '{location_name}': {e}")
        return None

def get_default_coordinates():
    """Get default coordinates (Delhi) as fallback"""
    return (28.6139, 77.2090)
