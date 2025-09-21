# 🪔 Mehndi App

A comprehensive Streamlit application for connecting mehndi artists with customers. This platform provides a complete solution for booking mehndi appointments, managing artist profiles, real-time chat, and admin oversight.

## ✨ Features

### 👤 User Features
- **User Registration & Login**: Secure authentication system
- **Artist Discovery**: Find nearby artists with map integration
- **Advanced Search & Filters**: Filter by style, price, ratings, distance
- **Real-time Chat**: Communicate with artists before booking
- **Booking System**: Easy appointment scheduling
- **Reviews & Ratings**: Rate and review artists
- **Profile Management**: Manage personal information

### 🎨 Artist Features
- **Profile Management**: Create and update professional profiles
- **Portfolio Showcase**: Upload and display work samples
- **Availability Management**: Set working hours and time slots
- **Booking Management**: View and manage appointments
- **Real-time Chat**: Communicate with customers
- **Performance Analytics**: Track ratings and reviews

### 👑 Admin Features
- **Artist Approval**: Review and approve new artist registrations
- **Content Moderation**: Monitor and manage flagged content
- **Analytics Dashboard**: Comprehensive business insights
- **System Settings**: Configure app parameters
- **Audit Logs**: Track all admin actions

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLite (demo) / PostgreSQL (production)
- **Authentication**: bcrypt password hashing
- **Maps**: Google Maps / Mapbox / OpenStreetMap integration
- **Charts**: Plotly for analytics
- **File Storage**: Local storage (demo) / Cloud storage (production)

## 📁 Project Structure

```
mehndi_app/
├── main.py              # Application entry point
├── auth.py              # Authentication & user management
├── database.py          # Database connection & queries
├── admin.py             # Admin functionality
├── booking.py           # Booking & scheduling system
├── chat.py              # Chat functionality
├── utils.py             # Helper functions & utilities
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── mehndi_app.db       # SQLite database (created on first run)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mehndi_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:8501`

## 🔐 Initial Setup

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default admin password after first login!

### Database Initialization
The application automatically creates the SQLite database on first run with:
- User tables and authentication
- Artist profiles and portfolios
- Booking system
- Chat messaging
- Reviews and ratings
- Admin audit logs

## 📖 Usage Guide

### For Users
1. **Register** as a new user
2. **Login** with your credentials
3. **Search** for artists near your location
4. **Chat** with artists to discuss requirements
5. **Book** appointments at convenient times
6. **Rate** and review artists after service

### For Artists
1. **Register** as an artist
2. **Complete** your profile with portfolio
3. **Set** your availability and working hours
4. **Wait** for admin approval
5. **Start** accepting bookings and chat with customers

### For Admins
1. **Login** with admin credentials
2. **Review** pending artist applications
3. **Monitor** system activity and analytics
4. **Manage** flagged content and user reports
5. **Configure** app settings as needed

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production settings:
```env
DATABASE_URL=postgresql://user:password@localhost/mehndi_app
SECRET_KEY=your-secret-key
MAP_API_KEY=your-map-api-key
CLOUD_STORAGE_BUCKET=your-bucket-name
```

### Map Integration
The app supports multiple map providers:
- **Google Maps**: Requires API key
- **Mapbox**: Requires access token
- **OpenStreetMap**: Free, no API key required

## 🔒 Security Features

- **Role-based Access Control**: User, Artist, and Admin roles
- **Password Hashing**: bcrypt encryption
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Parameterized queries
- **XSS Prevention**: Input sanitization and escaping
- **Audit Logging**: All admin actions are logged

## 📊 Database Schema

### Core Tables
- `users`: User accounts and authentication
- `artists`: Artist profiles and portfolios
- `artist_availability`: Artist working hours
- `bookings`: Appointment bookings
- `chat_messages`: Real-time messaging
- `reviews`: Ratings and reviews
- `admin_logs`: Audit trail

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py
```

### Production Deployment
1. **Heroku**: Add `Procfile` and deploy
2. **AWS**: Use EC2 or Elastic Beanstalk
3. **Google Cloud**: Use App Engine or Cloud Run
4. **Docker**: Containerize the application

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "main.py", "--server.port", "8501"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Future Enhancements

- [ ] Mobile app development
- [ ] Push notifications
- [ ] Payment gateway integration
- [ ] Video calling feature
- [ ] Advanced AI recommendations
- [ ] Multi-language support
- [ ] Social media integration

---

**Built with ❤️ for the Mehndi community**
