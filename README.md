# Flight Booking System - Frontend & Backend Integration

A modern, responsive flight booking system with a beautiful glassmorphism UI, built with HTML, CSS, and JavaScript for the frontend, integrated with a Python Flask backend and MySQL database.

## 🚀 Features

### Frontend

- **Modern UI Design**: Glassmorphism effects, gradient backgrounds, smooth animations
- **Responsive Layout**: Mobile-first design that works on all devices
- **User Authentication**: Secure registration and login system
- **Flight Search**: Search flights by source, destination, and date
- **Real-time Booking**: Book flights with seat selection and instant PNR generation
- **Toast Notifications**: Beautiful feedback for all user actions
- **Session Management**: Persistent login sessions

### Backend

- **RESTful API**: Clean Flask-based API with JSON responses
- **Database Integration**: MySQL with connection pooling for performance
- **Secure Authentication**: SHA-256 password hashing
- **Stored Procedures**: Optimized database queries
- **CORS Support**: Secure cross-origin requests
- **Session Handling**: Cookie-based session management

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Command line/terminal access

## 🛠️ Installation & Setup

### 1. Database Setup

First, set up the MySQL database:

```bash
# Login to MySQL
mysql -u root -p

# Create and populate the database
source DBMS_PROJECT.sql
```

This will create the `FlightBookingDB` database with all tables, stored procedures, and sample flight data.

### 2. Install Python Dependencies

```bash
# Navigate to the project directory
cd "d:\GIANDEEP MAIN\College Notes and notices\Sem 3\DBMS\DBMS PROJECT"

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Database Connection

The backend uses these default database credentials:

- **Host**: localhost
- **User**: root
- **Password**: GDSingh@2026
- **Database**: FlightBookingDB

If your MySQL credentials are different, update them in `flight_booking_system.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'database': 'FlightBookingDB',
    # ... rest of config
}
```

## 🎯 Running the Application

### ⚡ Quick Start (One-Click Launch)

The easiest way to run SkyBook:

```bash
# Simply double-click this file:
launch_skybook.bat
```

This will automatically:

- ✅ Start the API server in a separate window
- ✅ Wait for the server to be ready
- ✅ Open the website in your browser

**That's it!** Keep the API server window open while using SkyBook.

---

### 🛠️ Manual Start (Advanced)

If you prefer to start components manually:

### Step 1: Start the Backend API Server

```bash
python api_server.py
```

You should see:

```
============================================================
Flight Booking API Server Starting...
============================================================
Server URL: http://localhost:5000
API Endpoints:
  - POST /api/register    - Register new user
  - POST /api/login       - Login user
  - POST /api/logout      - Logout user
  - GET  /api/session     - Get session info
  - GET  /api/search      - Search flights
  - GET  /api/flight/<#>  - Get flight details
  - POST /api/book        - Book a flight
  - GET  /api/bookings    - Get user bookings
============================================================
```

**Important**: Keep this terminal window open. The server must be running for the frontend to work.

### Step 2: Open the Frontend

Option A: **Direct File Access** (Simplest)

```bash
# Just open the HTML file in your browser
start index.html
```

Option B: **Using Python HTTP Server** (Recommended for development)

```bash
# Open a NEW terminal window
python -m http.server 8000

# Then open in browser:
# http://localhost:8000
```

Option C: **Using Live Server** (VS Code extension)

- Install "Live Server" extension in VS Code
- Right-click `index.html` → "Open with Live Server"

## 📖 User Guide

### Registration

1. Click the **"Register"** button in the header
2. Fill in your details:
   - Full Name (minimum 2 characters)
   - Email (valid email format)
   - Phone (numbers only)
   - Password (minimum 6 characters)
3. Click **"Create Account"**
4. You'll be redirected to login

### Login

1. Click the **"Login"** button
2. Enter your email and password
3. Click **"Login"**
4. Your name will appear in the header once logged in

### Searching for Flights

1. In the search form, enter:
   - **From**: Departure city (e.g., Delhi, Mumbai, Bengaluru)
   - **To**: Destination city (e.g., Chennai, Kolkata, Pune)
   - **Date**: Select a future date
2. Click **"Search Flights"**
3. Available flights will be displayed below

**Available Cities**: Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Pune, Hyderabad, Ahmedabad, Jaipur, Lucknow, Kochi, Goa, Amritsar, Srinagar, and more.

### Booking a Flight

1. Click **"Book Now"** on your desired flight
   - Note: You must be logged in to book
2. Enter a seat number (format: row + letter, e.g., "12A", "24C")
   - Rows: 1-180
   - Seats: A-F
3. Click **"Confirm Booking"**
4. You'll receive a PNR (Passenger Name Record) confirmation

### Seat Number Format

- Valid examples: `1A`, `12B`, `45C`, `180F`
- Invalid examples: `A12`, `1G`, `200A`

## 🔧 API Endpoints

### Authentication

**Register User**

```http
POST /api/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91 9876543210",
  "password": "securepassword"
}
```

**Login**

```http
POST /api/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Logout**

```http
POST /api/logout
```

### Flights

**Search Flights**

```http
GET /api/search?source=Delhi&destination=Mumbai&date=2025-12-10
```

**Get Flight Details**

```http
GET /api/flight/6E339
```

### Booking

**Book Flight**

```http
POST /api/book
Content-Type: application/json

{
  "flight_id": 150,
  "seat_no": "12A",
  "booking_date": "2025-12-10"
}
```

## 🎨 Technology Stack

### Frontend

- **HTML5**: Semantic markup for structure
- **CSS3**: Modern styling with CSS custom properties, Grid, Flexbox
- **JavaScript (ES6+)**: Async/await, Fetch API, class-based architecture

### Backend

- **Python 3.8+**
- **Flask 3.0**: Web framework
- **MySQL 8.0**: Relational database
- **mysql-connector-python**: Database driver

### Design Features

- Glassmorphism effects with backdrop-filter
- Dark mode color palette
- Gradient accents
- Smooth animations and transitions
- Responsive grid layouts
- Mobile-first approach

## 📁 Project Structure

```
DBMS PROJECT/
├── launch_skybook.bat      # One-click launcher (double-click to run!)
├── launch_skybook.py       # Python launcher script
├── index.html              # Main frontend HTML
├── styles.css              # CSS styling with design system
├── app.js                  # Frontend JavaScript logic
├── api_server.py           # Flask REST API server
├── flight_booking_system.py # Backend business logic
├── DBMS_PROJECT.sql        # Database schema and data
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── OPTIMIZATION_REPORT.md  # Report on recent optimizations
├── docs/                   # Documentation and guides
├── logs/                   # Application logs
├── backups/                # Archived data files
├── generate_data.py        # Flight data generator
├── test_files.py           # Testing utilities
└── flight_dataset_cleaned.csv # Flight data CSV
```

## 🐛 Troubleshooting

### Backend Issues

**"Connection refused" or "Cannot connect to MySQL"**

- Ensure MySQL server is running: `mysql.server start` or service start
- Verify credentials in `flight_booking_system.py`
- Check if database exists: `SHOW DATABASES;`

**"Module not found" errors**

```bash
pip install -r requirements.txt
```

**Port 5000 already in use**

- Change the port in `api_server.py` (line near `app.run(port=5000)`)
- Update `API_BASE_URL` in `app.js` to match

### Frontend Issues

**"Failed to fetch" errors**

- Ensure the backend server is running on `http://localhost:5000`
- Check browser console (F12) for error details
- Verify CORS is enabled in `api_server.py`

**Login not working**

- Clear browser cookies and localStorage
- Check backend terminal for error messages
- Verify user exists in database

**No flights found**

- Check if flights exist for the selected route and date
- Try popular routes: Delhi→Mumbai, Bengaluru→Chennai
- Ensure date is in the future
- Check database: `SELECT * FROM Flights LIMIT 10;`

### Browser Console Errors

Open the browser console (F12) to see detailed error messages. Common issues:

- CORS errors → Restart backend server
- 401 Unauthorized → Login again
- 500 Server Error → Check backend terminal logs

## 🧪 Testing

### Manual Testing Checklist

- [ ] Register a new user
- [ ] Login with registered credentials
- [ ] Search for flights (various routes)
- [ ] Book a flight
- [ ] Verify PNR generation
- [ ] Logout and login again
- [ ] Test on mobile viewport
- [ ] Test error scenarios (wrong password, invalid seat, etc.)

### Database Verification

```sql
-- Check registered users
SELECT * FROM Users ORDER BY user_id DESC LIMIT 5;

-- Check bookings
SELECT * FROM Bookings ORDER BY booking_id DESC LIMIT 5;

-- Check available flights
SELECT
    flight_number,
    airline_name,
    source,
    destination,
    journey_date,
    available_seats
FROM Flight_Schedule_View
WHERE available_seats > 0
LIMIT 10;
```

## 📝 Sample Data

The database includes flights for dates between **2025-12-02 and 2026-03-01**.

### Popular Routes

- Delhi ↔ Mumbai
- Bengaluru ↔ Chennai
- Kolkata ↔ Hyderabad
- Pune ↔ Goa
- Kochi ↔ Delhi

### Airlines

- Air India, IndiGo, SpiceJet, AkasaAir, Air India Express, and more

## 🔐 Security Notes

- Passwords are hashed using SHA-256 before storage
- Session cookies are HTTP-only and secure
- SQL injection protection via parameterized queries
- Input validation on both frontend and backend
- CORS configured for development (adjust for production)

## 🚀 Future Enhancements

- [ ] Payment gateway integration
- [ ] Email confirmation for bookings
- [ ] Booking history and cancellation
- [ ] Multi-city and round-trip search
- [ ] Filter by price, duration, stops
- [ ] Seat map visualization
- [ ] Admin dashboard

## 👨‍💻 Development

Built for **DBMS Mini Project** - Semester 3

### Key Learning Outcomes

- Full-stack web development
- RESTful API design
- Database design and optimization
- Frontend-backend integration
- Modern UI/UX principles

## 📄 License

This project is created for educational purposes as part of a DBMS course project.

## 🤝 Support

For issues or questions:

1. Check the Troubleshooting section above
2. Review browser console and backend terminal logs
3. Verify database connection and data
4. Check that all dependencies are installed

---

**Happy Flying! ✈️**
