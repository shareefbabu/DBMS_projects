import os
import argparse
import datetime
import random
import string
import re
import logging
import mysql.connector
from mysql.connector import pooling, Error
from functools import lru_cache
import bcrypt
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'GDSingh@2026'),
    'database': 'FlightBookingDB',
    'pool_name': 'flight_pool',
    'pool_size': 10,  # Increased for better concurrency
    'pool_reset_session': True
}

class FlightBookingAPI:
    """
    Backend API Class: Handles all database interactions and business logic.
    Returns pure data (dictionaries/lists) or booleans.
    Optimized with connection pooling, caching, and security best practices.
    """
    def __init__(self, use_sample_data: bool = False):
        self.connection_pool = None
        self.current_user_id = None
        self.use_sample_data = use_sample_data
        # Cache for search results (key: search_params_hash, value: (results, timestamp))
        self._search_cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
        # Initialize connection pool
        try:
            pool_config = DB_CONFIG.copy()
            pool_config['connection_timeout'] = 30
            pool_config['autocommit'] = False
            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info("Database connection pool created successfully")
        except Error as e:
            logger.error(f"Failed to create connection pool: {e}")

    def get_connection(self):
        """Get a connection from the pool with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.connection_pool:
                    conn = self.connection_pool.get_connection()
                else:
                    conn = mysql.connector.connect(**DB_CONFIG)
                
                if conn.is_connected():
                    return conn
            except Error as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
        
        logger.error("Failed to get database connection after retries")
        return None

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections to ensure proper cleanup."""
        conn = self.get_connection()
        if not conn:
            yield None
        else:
            try:
                yield conn
            finally:
                if conn.is_connected():
                    conn.close()

    def disconnect(self):
        """Close all connections in the pool gracefully."""
        self.connection_pool = None
        logger.info("Connection pool cleanup initiated")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt for enhanced security."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def register_user(self, name: str, email: str, phone: str, password: str) -> Dict[str, Any]:
        """Register new user with hashed password."""
        if not email or '@' not in email:
            return {"success": False, "message": "Invalid email format"}
        if not name or len(name.strip()) < 2:
            return {"success": False, "message": "Name must be at least 2 characters"}
        
        with self.get_db_connection() as conn:
            if not conn:
                return {"success": False, "message": "System unavailable. Please try again."}
            
            cursor = None
            try:
                cursor = conn.cursor()
                hashed_password = self.hash_password(password)
                
                # Use Stored Procedure for Registration
                cursor.callproc('RegisterUser', [name.strip(), email.strip().lower(), phone.strip(), hashed_password])
                conn.commit()
                
                logger.info(f"User registered: {email}")
                return {"success": True, "message": "Registration successful! You can now login."}
            except Error as e:
                conn.rollback()
                error_msg = str(e).lower()
                if 'already registered' in error_msg or 'duplicate' in error_msg:
                    return {"success": False, "message": "Email already registered. Please login."}
                logger.error(f"Registration error: {e}")
                return {"success": False, "message": "Registration failed. Please try again."}
            finally:
                if cursor:
                    cursor.close()

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user by verifying bcrypt hashed password."""
        if not email or not password:
            return {"success": False, "message": "Email and password required"}
        
        with self.get_db_connection() as conn:
            if not conn:
                return {"success": False, "message": "System unavailable. Please try again."}
            
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                # Fetch user with password hash for verification
                query = """
                    SELECT user_id, name, email, phone, password_hash 
                    FROM Users 
                    WHERE email = %s 
                    LIMIT 1
                """
                cursor.execute(query, (email.strip().lower(),))
                user = cursor.fetchone()
                
                if user and self.verify_password(password, user['password_hash']):
                    self.current_user_id = user['user_id']
                    # Remove password_hash from returned user object
                    del user['password_hash']
                    logger.info(f"Login successful: {email}")
                    return {"success": True, "user": user, "message": "Welcome back!"}
                else:
                    logger.warning(f"Failed login attempt: {email}")
                    return {"success": False, "message": "Invalid email or password"}
            except Error as e:
                logger.error(f"Authentication error: {e}")
                return {"success": False, "message": "Login failed. Please try again."}
            finally:
                if cursor:
                    cursor.close()

    def search_flights(self, source: str, dest: str, date: str) -> List[Dict[str, Any]]:
        """Search flights with caching."""
        if not source or not dest or not date:
            return []
        
        # Cache key
        cache_key = f"{source.strip().lower()}_{dest.strip().lower()}_{date}"
        current_time = datetime.datetime.now().timestamp()
        
        # Check cache
        if cache_key in self._search_cache:
            cached_results, cache_time = self._search_cache[cache_key]
            if current_time - cache_time < self._cache_ttl:
                logger.info(f"Cache hit for search: {source}->{dest}")
                return cached_results
            else:
                del self._search_cache[cache_key]
        
        with self.get_db_connection() as conn:
            if not conn:
                return []
            
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.callproc('SearchFlights', [source.strip().title(), dest.strip().title(), date])
                
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                
                # Serialize types for JSON/Display compatibility
                for r in results:
                    for k, v in r.items():
                        if isinstance(v, (datetime.date, datetime.time, datetime.timedelta)):
                            r[k] = str(v)
                        elif isinstance(v, (int, float)) and k == 'price':
                            r[k] = float(v)
                
                # Update cache
                self._search_cache[cache_key] = (results, current_time)
                return results
            except Error as e:
                logger.error(f"Search error: {e}")
                return []
            finally:
                if cursor:
                    cursor.close()

    def get_flight_details(self, flight_number: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific flight."""
        if not flight_number:
            return None
        
        with self.get_db_connection() as conn:
            if not conn:
                return None
            
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT flight_id, price, available_seats, departure_time, arrival_time
                    FROM Flights 
                    WHERE flight_number = %s 
                    LIMIT 1
                """
                cursor.execute(query, (flight_number.strip(),))
                return cursor.fetchone()
            except Error as e:
                logger.error(f"Flight details error: {e}")
                return None
            finally:
                if cursor:
                    cursor.close()

    def book_flight(self, flight_id: int, seat_no: str, booking_date_str: str) -> Dict[str, Any]:
        """Book a flight for the current user."""
        if not self.current_user_id:
            return {"success": False, "message": "Please login to book flights"}
        
        if not flight_id or not seat_no:
            return {"success": False, "message": "Invalid booking details"}

        pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        with self.get_db_connection() as conn:
            if not conn:
                return {"success": False, "message": "System unavailable."}
            
            cursor = None
            try:
                cursor = conn.cursor()
                # Call BookFlight stored procedure
                cursor.callproc('BookFlight', [self.current_user_id, flight_id, seat_no.strip().upper(), pnr, booking_date_str])
                conn.commit()
                
                logger.info(f"Booking confirmed: PNR {pnr}")
                return {
                    "success": True, 
                    "pnr": pnr, 
                    "message": f"Booking confirmed! Your PNR is {pnr}"
                }
            except Error as e:
                conn.rollback()
                error_msg = str(e).lower()
                if 'fully booked' in error_msg:
                    return {"success": False, "message": "Flight is fully booked"}
                elif 'duplicate' in error_msg:
                    return {"success": False, "message": "You already have a booking for this flight"}
                logger.error(f"Booking error: {e}")
                return {"success": False, "message": "Booking failed. Please try again."}
            finally:
                if cursor:
                    cursor.close()

class FlightBookingCLI:
    """
    Frontend CLI Class: Handles user input/output and calls the API.
    """
    def __init__(self, use_sample_data=False):
        self.api = FlightBookingAPI(use_sample_data)

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(email and re.match(pattern, email))
    
    def validate_phone(self, phone):
        pattern = r'^(\+91)?[6-9]\d{9}$'
        if not phone: return False
        phone_clean = phone.replace(' ', '').replace('-', '')
        return bool(re.match(pattern, phone_clean))
    
    def validate_date(self, date_text):
        if not date_text: return False
        try:
            parsed_date = datetime.datetime.strptime(date_text.strip(), '%Y-%m-%d').date()
            if parsed_date < datetime.date.today():
                return False
            return True
        except ValueError:
            return False
    
    def get_suggested_dates(self):
        today = datetime.date.today()
        return [
            ("Today", today),
            ("+7 days", today + datetime.timedelta(days=7)),
            ("+14 days", today + datetime.timedelta(days=14))
        ]

    def run(self):
        print("\n" + "="*50)
        print("   WELCOME TO AIRLINE RESERVATION SYSTEM")
        print("="*50)
        
        while True:
            if not self.api.current_user_id:
                print("\n1. Register")
                print("2. Login")
                print("3. Exit")
                choice = input("\nEnter choice: ").strip()
                
                if choice == '1':
                    print("\n--- REGISTER ---")
                    name = input("Name: ")
                    email = input("Email: ")
                    phone = input("Phone: ")
                    password = input("Password: ")
                    
                    if not self.validate_email(email):
                        print("Error: Invalid email format")
                        continue
                    if not self.validate_phone(phone):
                        print("Error: Invalid phone number (10 digits required)")
                        continue
                        
                    result = self.api.register_user(name, email, phone, password)
                    if result:
                        print(f"\n{result.get('message', 'Registration processed')}")
                    else:
                        print("\nRegistration failed. Please try again.")
                    
                elif choice == '2':
                    print("\n--- LOGIN ---")
                    email = input("Email: ")
                    password = input("Password: ")
                    result = self.api.authenticate_user(email, password)
                    if result:
                        print(f"\n{result.get('message', 'Authentication processed')}")
                    else:
                        print("\nLogin failed. Please try again.")
                    
                elif choice == '3':
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice")
            else:
                print("\n--- MAIN MENU ---")
                print("1. Search Flights")
                print("2. Logout")
                choice = input("\nEnter choice: ").strip()
                
                if choice == '1':
                    source = input("Source City: ")
                    dest = input("Destination City: ")
                    
                    print("\nSuggested Dates:")
                    dates = self.get_suggested_dates()
                    for i, (label, d) in enumerate(dates, 1):
                        print(f"{i}. {label} ({d})")
                    print("4. Custom Date")
                    
                    date_choice = input("Select Date Option: ").strip()
                    date_str = None
                    
                    if date_choice in ['1', '2', '3']:
                        date_str = str(dates[int(date_choice)-1][1])
                    else:
                        date_str = input("Enter Date (YYYY-MM-DD): ")
                        if not self.validate_date(date_str):
                            print("Invalid date")
                            continue
                            
                    results = self.api.search_flights(source, dest, date_str)
                    
                    if not results:
                        print("\nNo flights found.")
                    else:
                        print(f"\nFound {len(results)} flights:")
                        print("-" * 80)
                        print(f"{'Flight':<10} | {'Airline':<15} | {'Departs':<10} | {'Price':<10} | {'Seats'}")
                        print("-" * 80)
                        for r in results:
                            try:
                                flight_num = r.get('flight_number', 'N/A')
                                airline = r.get('airline_name', 'N/A')
                                dep_time = r.get('departure_time', 'N/A')
                                price = r.get('price', 0)
                                seats = r.get('available_seats', 0)
                                print(f"{flight_num:<10} | {airline:<15} | {str(dep_time):<10} | ₹{price:<9} | {seats}")
                            except Exception as e:
                                logger.error(f"Error displaying flight: {e}")
                                continue
                        print("-" * 80)
                        
                        book_choice = input("\nEnter Flight Number to book (or Enter to go back): ").strip()
                        if book_choice:
                            # Verify flight exists and get ID
                            # In a real app, search results would include ID hidden from user
                            # For CLI, we'll fetch details again
                            details = self.api.get_flight_details(book_choice)
                            if details and 'flight_id' in details:
                                seat = input("Enter Seat Number (e.g., 12A): ")
                                res = self.api.book_flight(details['flight_id'], seat, date_str)
                                if res:
                                    print(f"\n{res.get('message', 'Booking processed')}")
                                else:
                                    print("\nBooking failed. Please try again.")
                            else:
                                print("Invalid flight number")
                                
                elif choice == '2':
                    self.api.current_user_id = None
                    print("\nLogged out successfully")
                else:
                    print("Invalid choice")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flight Booking System CLI")
    parser.add_argument('--sample', action='store_true', help="Use sample data mode")
    args = parser.parse_args()
    
    app = FlightBookingCLI(use_sample_data=args.sample)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        app.api.disconnect()
