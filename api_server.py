"""
Flask REST API Server for Flight Booking System
Provides HTTP endpoints for the frontend to interact with the backend
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import logging
import os
import sys
import pandas as pd
import hashlib
from functools import wraps
from flight_booking_system import FlightBookingAPI
from password_reset_manager import PasswordResetManager
from utils import precompute_locations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_default_secret_key')

# ===================================
# PERFORMANCE: Global CSV Data Cache
# ===================================
FLIGHTS_DATAFRAME = None
LOCATIONS_CACHE = None
CACHE_LOADED = False

def load_csv_cache():
    """Load CSV data into memory cache on server startup for performance"""
    global FLIGHTS_DATAFRAME, LOCATIONS_CACHE, CACHE_LOADED
    
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'flight_dataset_cleaned.csv')
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found at {csv_path}")
            return False
        
        # Load CSV into pandas DataFrame (cached in memory)
        logger.info("Loading flight dataset into memory cache...")
        FLIGHTS_DATAFRAME = pd.read_csv(csv_path)
        logger.info(f"[+] Loaded {len(FLIGHTS_DATAFRAME)} flights into cache")
        
        # Pre-compute locations data
        logger.info("Pre-computing locations data...")
        LOCATIONS_CACHE = precompute_locations(FLIGHTS_DATAFRAME)
        logger.info(f"[+] Cached {LOCATIONS_CACHE['count']} unique airports")
        
        CACHE_LOADED = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to load CSV cache: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False



# Initialize the Flight Booking API
api = FlightBookingAPI()

# Initialize Password Reset Manager
reset_manager = PasswordResetManager()


# ===================================
# LOGIN TRACKING FUNCTIONALITY
# ===================================

def record_login(user_id, email, login_status='Success'):
    """
    Record a login event in the database
    
    Args:
        user_id: User ID from Users table
        email: User email address
        login_status: Status of login attempt (Success/Failed/Timeout)
    
    Returns:
        int: record_id of created login record
    """
    try:
        # Ensure database connection is active
        if not api.db_connection or not api.db_connection.is_connected():
            api.db_connection = api.get_connection()
            if not api.db_connection:
                logger.error("Failed to get database connection for login tracking")
                return None
        
        cursor = api.db_connection.cursor()
        
        # Get client information
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Determine device type from user agent
        device_type = 'Desktop'
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_type = 'Mobile'
        elif 'iPad' in user_agent or 'Tablet' in user_agent:
            device_type = 'Tablet'
        
        query = """
        INSERT INTO login_records 
        (user_id, email, login_timestamp, ip_address, user_agent, 
         login_status, device_type, location)
        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            user_id, 
            email, 
            ip_address, 
            user_agent, 
            login_status, 
            device_type,
            'India'  # Default location
        ))
        
        api.db_connection.commit()
        record_id = cursor.lastrowid
        cursor.close()
        
        logger.info(f"[+] Login recorded for user {email} (ID: {user_id})")
        return record_id
        
    except Exception as e:
        logger.error(f"Error recording login: {e}")
        return None


def record_logout(user_id):
    """
    Record logout timestamp and calculate session duration
    
    Args:
        user_id: User ID
    """
    try:
        # Ensure database connection is active
        if not api.db_connection or not api.db_connection.is_connected():
            api.db_connection = api.get_connection()
            if not api.db_connection:
                logger.error("Failed to get database connection for logout tracking")
                return
        
        cursor = api.db_connection.cursor()
        
        # Update the most recent login record for this user
        query = """
        UPDATE login_records 
        SET logout_timestamp = NOW(),
            session_duration = TIMESTAMPDIFF(SECOND, login_timestamp, NOW())
        WHERE user_id = %s 
          AND logout_timestamp IS NULL
        ORDER BY login_timestamp DESC
        LIMIT 1
        """
        
        cursor.execute(query, (user_id,))
        api.db_connection.commit()
        cursor.close()
        
        logger.info(f"[+] Logout recorded for user ID: {user_id}")
        
    except Exception as e:
        logger.error(f"Error recording logout: {e}")


def login_required(f):
    """Decorator to require login for certain endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Please login to continue"}), 401
        api.current_user_id = session['user_id']
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400
        
        # Call backend API
        result = api.register_user(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password=data['password']
        )
        
        status_code = 201 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            "success": False,
            "message": "Server error. Please try again."
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and create session with login tracking"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            # Record failed login attempt (no user_id)
            record_login(None, email, 'Failed')
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400
            
        logger.info(f"Attempting login for: {email}")  # Trigger reload
        
        # Call backend API
        result = api.authenticate_user(
            email=email,
            password=password
        )
        
        if result.get('success'):
            # Store user info in session
            session['user_id'] = result['user']['user_id']
            session['user_name'] = result['user']['name']
            session['user_email'] = result['user']['email']
            session.permanent = True
            
            # Record successful login
            record_id = record_login(result['user']['user_id'], email, 'Success')
            session['current_login_record_id'] = record_id
            
            logger.info(f"[+] User logged in: {email}")
        else:
            # Record failed login attempt
            record_login(None, email, 'Failed')
            logger.warning(f"[-] Failed login attempt for {email}")
        
        status_code = 200 if result.get('success') else 401
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            "success": False,
            "message": "Server error. Please try again."
        }), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user and clear session with session tracking"""
    try:
        user_id = session.get('user_id')
        email = session.get('user_email')
        
        # Record logout if user was logged in
        if user_id:
            record_logout(user_id)
            logger.info(f"[+] User logged out: {email}")
        
        # Clear session
        session.clear()
        api.current_user_id = None
        
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"success": False, "message": "Logout failed"}), 500


@app.route('/api/session', methods=['GET'])
def get_session():
    """Get current session info"""
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "user_id": session['user_id'],
                "name": session['user_name'],
                "email": session['user_email']
            }
        }), 200
    else:
        return jsonify({"authenticated": False}), 200


@app.route('/api/search', methods=['GET'])
def search_flights():
    """Search for flights"""
    try:
        # Get query parameters
        source = request.args.get('source', '').strip()
        destination = request.args.get('destination', '').strip()
        date = request.args.get('date', '').strip()
        
        if not source or not destination or not date:
            return jsonify({
                "success": False,
                "message": "Source, destination, and date are required",
                "flights": []
            }), 400
        
        # Call backend API
        flights = api.search_flights(source, destination, date)
        
        return jsonify({
            "success": True,
            "flights": flights,
            "count": len(flights)
        }), 200
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            "success": False,
            "message": "Error searching flights",
            "flights": []
        }), 500


@app.route('/api/flight/<flight_number>', methods=['GET'])
def get_flight_details(flight_number):
    """Get details for a specific flight"""
    try:
        flight = api.get_flight_details(flight_number)
        
        if flight:
            return jsonify({
                "success": True,
                "flight": flight
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Flight not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Flight details error: {e}")
        return jsonify({
            "success": False,
            "message": "Error retrieving flight details"
        }), 500


@app.route('/api/book', methods=['POST'])
@login_required
def book_flight():
    """Book a flight"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('flight_id') or not data.get('seat_no'):
            return jsonify({
                "success": False,
                "message": "Flight ID and seat number are required"
            }), 400
        
        booking_date = data.get('booking_date', '')
        
        # Call backend API
        result = api.book_flight(
            flight_id=int(data['flight_id']),
            seat_no=data['seat_no'],
            booking_date_str=booking_date
        )
        
        status_code = 201 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Booking error: {e}")
        return jsonify({
            "success": False,
            "message": "Error processing booking"
        }), 500


@app.route('/api/bookings', methods=['GET'])
@login_required
def get_user_bookings():
    """Get all bookings for the current user"""
    try:
        # This would require adding a method to FlightBookingAPI
        # For now, return a placeholder
        user_id = session['user_id']
        
        return jsonify({
            "success": True,
            "bookings": [],
            "message": "Bookings feature coming soon"
        }), 200
        
    except Exception as e:
        logger.error(f"Get bookings error: {e}")
        return jsonify({
            "success": False,
            "message": "Error retrieving bookings"
        }), 500


@app.route('/api/login_history', methods=['GET'])
@login_required
def get_login_history():
    """Get login history for current user"""
    try:
        user_id = session.get('user_id')
        
        cursor = api.db_connection.cursor(dictionary=True)
        query = """
        SELECT 
            record_id,
            login_timestamp,
            logout_timestamp,
            ip_address,
            login_status,
            session_duration,
            device_type,
            location,
            CASE 
                WHEN logout_timestamp IS NULL AND login_status = 'Success' 
                THEN 'Active'
                ELSE 'Complete'
            END as session_status
        FROM login_records
        WHERE user_id = %s
        ORDER BY login_timestamp DESC
        LIMIT 50
        """
        
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error fetching login history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/active_sessions', methods=['GET'])
@login_required
def get_active_sessions():
    """Get currently active sessions for current user"""
    try:
        user_id = session.get('user_id')
        
        cursor = api.db_connection.cursor(dictionary=True)
        query = """
        SELECT 
            record_id,
            login_timestamp,
            ip_address,
            device_type,
            TIMESTAMPDIFF(MINUTE, login_timestamp, NOW()) as minutes_active
        FROM login_records
        WHERE user_id = %s
          AND logout_timestamp IS NULL
          AND login_status = 'Success'
        ORDER BY login_timestamp DESC
        """
        
        cursor.execute(query, (user_id,))
        sessions = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'count': len(sessions),
            'active_sessions': sessions
        })
        
    except Exception as e:
        logger.error(f"Error fetching active sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================================
# PASSWORD RESET ENDPOINTS
# ===================================

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset - validates email exists before sending reset link
    
    Request body:
        {
            "email": "user@email.com"
        }
    
    Returns:
        Success: {"success": true, "message": "Reset instructions sent to email"}
        Email not found: {"success": false, "message": "Email address not found"}
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email or '@' not in email:
            return jsonify({
                'success': False,
                'message': 'Please provide a valid email address'
            }), 400
        
        # CRITICAL: Verify email exists in Users table
        exists, user_id = reset_manager.verify_email_exists(email)
        
        if not exists:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return jsonify({
                'success': False,
                'message': 'Email address not found. Please check and try again.'
            }), 404
        
        # RATE LIMITING: Check for recent reset requests
        try:
            cursor = api.db_connection.cursor(dictionary=True)
            rate_limit_query = """
            SELECT COUNT(*) as request_count
            FROM password_reset_tokens
            WHERE email = %s 
            AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """
            cursor.execute(rate_limit_query, (email,))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result['request_count'] >= 3:
                logger.warning(f"Rate limit exceeded for password reset: {email}")
                return jsonify({
                    'success': False,
                    'message': 'Too many password reset requests. Please try again in an hour.'
                }), 429
        except Exception as rate_error:
            logger.error(f"Rate limiting check failed: {rate_error}")
            # Continue anyway - don't block password reset due to rate limit check failure
        
        # Generate reset token
        reset_token = reset_manager.generate_reset_token(email, user_id)
        
        if not reset_token:
            return jsonify({
                'success': False,
                'message': 'Failed to generate reset token. Please try again.'
            }), 500
        
        # Create reset link
        reset_link = f"http://localhost:5000/reset-password.html?token={reset_token}"
        
        # Send email via email service
        from email_service import EmailService
        email_service = EmailService()
        email_sent = email_service.send_password_reset_email(email, reset_token, reset_link)
        
        if not email_sent:
            logger.error(f"Failed to send password reset email to {email}")
            # Don't fail the request - email might be in console
        
        logger.info(f"[+] Password reset requested for: {email}")
        
        # Return success with reset link (for development convenience)
        return jsonify({
            'success': True,
            'message': f'Password reset instructions have been sent to {email}',
            'reset_link': reset_link,  # Helpful for development - shows in UI
            'dev_mode': not email_service.smtp_enabled  # Indicate if using console logging
        }), 200
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }), 500


@app.route('/api/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """
    Verify if reset token is valid
    
    Returns:
        {"valid": true, "email": "user@email.com"}
        {"valid": false, "message": "Token expired/invalid"}
    """
    try:
        is_valid, token_data = reset_manager.validate_reset_token(token)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'email': token_data.get('email')
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': 'Invalid or expired reset token'
            }), 400
            
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({
            'valid': False,
            'message': 'Error verifying token'
        }), 500


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password with valid token
    Updates password in MySQL database
    
    Request body:
        {
            "token": "reset_token_string",
            "new_password": "newpassword123"
        }
    """
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({
                'success': False,
                'message': 'Token and new password are required'
            }), 400
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        # Validate token
        is_valid, token_data = reset_manager.validate_reset_token(token)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired reset token'
            }), 400
        
        user_id = token_data.get('user_id')
        email = token_data.get('email')
        
        # Hash new password (same method as registration)
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Update password in MySQL database
        try:
            if api.db_connection and api.db_connection.is_connected():
                cursor = api.db_connection.cursor()
            else:
                # Reconnect if needed
                api.db_connection = api.get_connection()
                cursor = api.db_connection.cursor()
            
            update_query = """
            UPDATE Users 
            SET password_hash = %s 
            WHERE user_id = %s AND email = %s
            """
            
            cursor.execute(update_query, (new_password_hash, user_id, email))
            api.db_connection.commit()
            cursor.close()
            
            logger.info(f"[+] Password updated in database for {email}")
            
        except Exception as db_error:
            logger.error(f"Database update error: {db_error}")
            return jsonify({
                'success': False,
                'message': 'Failed to update password in database'
            }), 500
        

        
        # Mark token as used
        reset_manager.mark_token_used(token)
        
        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }), 200
        
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while resetting password'
        }), 500


@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get unique airport names from cache for autocomplete (OPTIMIZED with caching)"""
    try:
        # Use cached data if available
        if CACHE_LOADED and LOCATIONS_CACHE:
            logger.info(f"Serving locations from cache ({LOCATIONS_CACHE['count']} airports)")
            return jsonify({
                "success": True,
                **LOCATIONS_CACHE,
                "all_cities": LOCATIONS_CACHE['airports']  # Backward compatibility
            }), 200
        
        # Fallback: Load from CSV if cache not available
        logger.warning("Cache not loaded, falling back to CSV read")
        import re
        
        csv_path = os.path.join(os.path.dirname(__file__), 'flight_dataset_cleaned.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({
                "success": False,
                "message": "CSV file not found",
                "airports": []
            }), 404
        
        df = pd.read_csv(csv_path)
        locations_data = precompute_locations(df)
        
        return jsonify({
            "success": True,
            **locations_data,
            "all_cities": locations_data['airports']
        }), 200
        
    except Exception as e:
        logger.error(f"Error loading airports: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"Error loading airports: {str(e)}",
            "airports": []
        }), 500


@app.route('/api/flights/csv', methods=['GET'])
def get_flights_from_csv():
    """Get flights directly from the CSV file with enhanced filtering"""
    try:
        import random
        import string
        from datetime import datetime, timedelta
        
        # Airline logo mapping for common Indian airlines
        AIRLINE_LOGOS = {
            'Air India': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Air_India_logo.svg/120px-Air_India_logo.svg.png',
            'Air India Express': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/96/Air_India_Express_logo.svg/120px-Air_India_Express_logo.svg.png',
            'IndiGo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/IndiGo_logo.svg/120px-IndiGo_logo.svg.png',
            'SpiceJet': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/SpiceJet_logo.svg/120px-SpiceJet_logo.svg.png',
            'Vistara': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Vistara_Logo.svg/120px-Vistara_Logo.svg.png',
            'GoAir': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/GoAir_logo.svg/120px-GoAir_logo.svg.png',
            'Go First': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/GoAir_logo.svg/120px-GoAir_logo.svg.png',
            'AirAsia India': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/AirAsia_New_Logo.svg/120px-AirAsia_New_Logo.svg.png',
            'Alliance Air': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Alliance_Air_logo.svg/120px-Alliance_Air_logo.svg.png',
        }
        
        # Get query parameters
        source = request.args.get('source', '').strip()
        destination = request.args.get('destination', '').strip()
        date_str = request.args.get('date', '').strip()
        
        # PERFORMANCE: Use cached DataFrame if available
        if CACHE_LOADED and FLIGHTS_DATAFRAME is not None:
            logger.info(f"[CACHE] Using cached flight data for search")
            df = FLIGHTS_DATAFRAME.copy()
        else:
            # Fallback: Load from CSV
            logger.warning("[!] Cache not loaded, reading CSV file...")
            csv_path = os.path.join(os.path.dirname(__file__), 'flight_dataset_cleaned.csv')
            
            if not os.path.exists(csv_path):
                return jsonify({
                    "success": False,
                    "message": "CSV file not found",
                    "flights": []
                }), 404
            
            df = pd.read_csv(csv_path)
        
        # Resolve city names to airport names using cache
        if CACHE_LOADED and LOCATIONS_CACHE and 'airport_city_map' in LOCATIONS_CACHE:
            city_map = LOCATIONS_CACHE['airport_city_map']
            
            # Resolve source
            if source and source.lower() in city_map:
                original_source = source
                source = city_map[source.lower()]
                logger.info(f"Resolved source city '{original_source}' to '{source}'")
            
            # Resolve destination
            if destination and destination.lower() in city_map:
                original_dest = destination
                destination = city_map[destination.lower()]
                logger.info(f"Resolved destination city '{original_dest}' to '{destination}'")
        
        # Filter by source (departure location)
        if source:
            df = df[df['Departure_Port_Name'].str.contains(source, case=False, na=False)]
        
        # Filter by destination (arrival location)
        if destination:
            df = df[df['Arrival_Port_Name'].str.contains(destination, case=False, na=False)]
        
        # Limit results to manageable number
        df = df.head(100)
        
        # Helper function to generate PNR
        def generate_pnr():
            """Generate a unique 6-character PNR number"""
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Helper function to get airline logo
        def get_airline_logo(airline_name):
            """Get airline logo URL based on airline name"""
            # Try exact match first
            if airline_name in AIRLINE_LOGOS:
                return AIRLINE_LOGOS[airline_name]
            # Try partial match
            for key in AIRLINE_LOGOS:
                if key.lower() in airline_name.lower():
                    return AIRLINE_LOGOS[key]
            # Default placeholder
            return 'https://via.placeholder.com/120x40/667eea/ffffff?text=Airline'
        

        
        # Helper function to extract stop details
        def extract_stop_details(stops, departure_time, arrival_time, duration):
            """Extract location and timing details for stops"""
            stop_details = []
            
            if pd.isna(stops) or int(stops) == 0:
                return []
            
            num_stops = int(stops)
            
            # Parse times
            try:
                dep_time = datetime.strptime(str(departure_time), '%H:%M:%S')
                arr_time = datetime.strptime(str(arrival_time), '%H:%M:%S')
                dur_parts = str(duration).split(':')
                total_minutes = int(dur_parts[0]) * 60 + int(dur_parts[1])
                
                # Calculate stop timing intervals
                segment_duration = total_minutes // (num_stops + 1)
                
                # Common Indian layover cities
                layover_cities = [
                    'Mumbai (Chhatrapati Shivaji Maharaj International Airport)',
                    'Delhi (Indira Gandhi International Airport)',
                    'Bengaluru (Kempegowda International Airport)',
                    'Hyderabad (Rajiv Gandhi International Airport)',
                    'Chennai (Chennai International Airport)',
                    'Kolkata (Netaji Subhas Chandra Bose International Airport)',
                    'Ahmedabad (Sardar Vallabhbhai Patel International Airport)',
                    'Pune (Pune Airport)'
                ]
                
                current_time = dep_time
                for i in range(num_stops):
                    # Add segment duration
                    current_time += timedelta(minutes=segment_duration)
                    
                    # Layover duration (30-60 minutes)
                    layover_duration = random.randint(30, 60)
                    
                    stop_info = {
                        'stop_number': i + 1,
                        'location': random.choice(layover_cities),
                        'arrival_time': current_time.strftime('%H:%M'),
                        'duration_minutes': layover_duration
                    }
                    stop_details.append(stop_info)
                    
                    # Add layover duration
                    current_time += timedelta(minutes=layover_duration)
                    
            except Exception as e:
                logger.warning(f"Error calculating stop details: {e}")
                # Return basic stop information
                for i in range(num_stops):
                    stop_details.append({
                        'stop_number': i + 1,
                        'location': 'Intermediate Airport',
                        'arrival_time': 'N/A',
                        'duration_minutes': 45
                    })
            
            return stop_details
        
        # Use the requested date or default to future date
        journey_date = date_str if date_str else '2025-12-15'
        
        # Convert to list of dictionaries with enhanced data
        flights = []
        for idx, row in df.iterrows():
            stops = int(row['Stop']) if pd.notna(row['Stop']) else 0
            stop_details = extract_stop_details(
                row['Stop'], 
                row['Departure_Time'], 
                row['Arrival_Time'], 
                row['Duration_Time']
            )
            
            airline_name = str(row['Airlines_Name'])
            
            flight = {
                'flight_id': int(idx),
                'flight_number': str(row['Flight_Number']),
                'airline_name': airline_name,
                'airline_logo': get_airline_logo(airline_name),  # NEW: Airline logo URL
                'pnr_number': generate_pnr(),  # Generate PNR
                'source': str(row['Departure_Port_Name']),
                'destination': str(row['Arrival_Port_Name']),
                'departure_time': str(row['Departure_Time']),
                'arrival_time': str(row['Arrival_Time']),
                'duration': str(row['Duration_Time']),
                'price': float(row['Fare']),
                'available_seats': random.randint(10, 100),  # Random available seats
                'aircraft_type': str(row['Aircraft_Type']),
                'cabin_class': str(row['Cabin_Class']),
                'stops': stops,  # Number of stops
                'stop_details': stop_details,  # Detailed stop information
                'journey_date': journey_date
            }
            flights.append(flight)
        
        return jsonify({
            "success": True,
            "flights": flights,
            "count": len(flights),  # Total number of flights found
            "source": "CSV",
            "search_criteria": {
                "departure": source if source else "Any",
                "arrival": destination if destination else "Any",
                "date": journey_date
            }
        }), 200
        
    except Exception as e:
        logger.error(f"CSV read error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"Error reading CSV: {str(e)}",
            "flights": []
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Flight Booking API Server Starting...")
    print("=" * 60)
    
    # Load CSV cache before starting server
    print("Initializing performance cache...")
    cache_success = load_csv_cache()
    if cache_success:
        print("[+] CSV data successfully cached in memory")
        print(f"[+] {len(FLIGHTS_DATAFRAME)} flights loaded")
        print(f"[+] {LOCATIONS_CACHE['count']} airports indexed")
    else:
        print("[!] Warning: Cache initialization failed - using fallback CSV reads")
    print("=" * 60)
    
    print(f"Server URL: http://localhost:5000")
    print(f"API Endpoints:")
    print(f"  - POST /api/register    - Register new user")
    print(f"  - POST /api/login       - Login user")
    print(f"  - POST /api/logout      - Logout user")
    print(f"  - GET  /api/session     - Get session info")
    print(f"  - GET  /api/search      - Search flights")
    print(f"  - GET  /api/flight/<#>  - Get flight details")
    print(f"  - POST /api/book        - Book a flight")
    print(f"  - GET  /api/bookings    - Get user bookings")
    print(f"  - GET  /api/cities      - Get all cities for autocomplete")
    print(f"  - GET  /api/locations   - Get airports & cities (CACHED)")
    print(f"  - GET  /api/flights/csv - Get flights from CSV (CACHED)")
    print("=" * 60)
    
    try:
        # Run the Flask development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
        api.disconnect()
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        api.disconnect()
