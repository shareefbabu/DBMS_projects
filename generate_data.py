    """Escapes single quotes in strings for SQL safety."""
    if isinstance(val, str):
        return val.replace("'", "''")
    return val

def generate_sql():
    sql_content = []
    
    # Header
    sql_content.append("/*")
    sql_content.append("==================================================================================")
    sql_content.append("DBMS MINI PROJECT: AIRLINE RESERVATION SYSTEM (REAL-WORLD)")
    sql_content.append("==================================================================================")
    sql_content.append("Description: A comprehensive database system for managing airline bookings.")
    sql_content.append("Features:")
    sql_content.append("  - Normalized Schema (3NF)")
    sql_content.append("  - Automated Data Integrity (Triggers)")
    sql_content.append("  - Application Logic (Stored Procedures)")
    sql_content.append("  - Advanced Search Functionality (Mimics Modern Booking Platforms)")
    sql_content.append("  - Real-World Features: PNR, Flight Stops, User Authentication")
    sql_content.append("==================================================================================")
    sql_content.append("*/")
    sql_content.append("")
    
    # DDL
    sql_content.append("DROP DATABASE IF EXISTS FlightBookingDB;")
    sql_content.append("CREATE DATABASE FlightBookingDB;")
    sql_content.append("USE FlightBookingDB;")
    sql_content.append("")
    
    sql_content.append("-- 1. Airlines Table")
    sql_content.append("CREATE TABLE Airlines (")
    sql_content.append("    airline_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    airline_name VARCHAR(100) NOT NULL,")
    sql_content.append("    airline_code VARCHAR(3) NOT NULL")
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 2. Airports Table")
    sql_content.append("CREATE TABLE Airports (")
    sql_content.append("    airport_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    airport_name VARCHAR(150) NOT NULL,")
    sql_content.append("    city VARCHAR(100) NOT NULL,")
    sql_content.append("    owned_by VARCHAR(150)")
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 3. Flights Table")
    sql_content.append("CREATE TABLE Flights (")
    sql_content.append("    flight_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    airline_id INT,")
    sql_content.append("    flight_number VARCHAR(20),")
    sql_content.append("    source_airport_id INT,")
    sql_content.append("    destination_airport_id INT,")
    sql_content.append("    journey_date DATE,")
    sql_content.append("    departure_time TIME,")
    sql_content.append("    arrival_time TIME,")
    sql_content.append("    duration TIME,")
    sql_content.append("    stops INT,")
    sql_content.append("    aircraft_type VARCHAR(50),")
    sql_content.append("    price DECIMAL(10,2) DEFAULT 5000.00,")
    sql_content.append("    total_seats INT DEFAULT 180,")
    sql_content.append("    available_seats INT DEFAULT 180,")
    sql_content.append("    FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id),")
    sql_content.append("    FOREIGN KEY (source_airport_id) REFERENCES Airports(airport_id),")
    sql_content.append("    FOREIGN KEY (destination_airport_id) REFERENCES Airports(airport_id)")
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 4. Flight_Stops Table (NEW)")
    sql_content.append("CREATE TABLE Flight_Stops (")
    sql_content.append("    stop_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    flight_id INT,")
    sql_content.append("    airport_id INT,")
    sql_content.append("    arrival_time TIME,")
    sql_content.append("    departure_time TIME,")
    sql_content.append("    stop_sequence INT,")
    sql_content.append("    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id),")
    sql_content.append("    FOREIGN KEY (airport_id) REFERENCES Airports(airport_id)")
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 5. Users Table (Updated with Password)")
    sql_content.append("CREATE TABLE Users (")
    sql_content.append("    user_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    name VARCHAR(100),")
    sql_content.append("    email VARCHAR(100) UNIQUE,")
    sql_content.append("    phone VARCHAR(15),")
    sql_content.append("    password_hash VARCHAR(255) DEFAULT 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'") # SHA-256 for 'password123'
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 6. Bookings Table (Updated with PNR)")
    sql_content.append("CREATE TABLE Bookings (")
    sql_content.append("    booking_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    user_id INT,")
    sql_content.append("    flight_id INT,")
    sql_content.append("    booking_date DATE,")
    sql_content.append("    status ENUM('Confirmed', 'Cancelled', 'Pending') DEFAULT 'Confirmed',")
    sql_content.append("    seat_no VARCHAR(10),")
    sql_content.append("    pnr VARCHAR(10) UNIQUE,")
    sql_content.append("    FOREIGN KEY (user_id) REFERENCES Users(user_id),")
    sql_content.append("    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)")
    sql_content.append(");")
    sql_content.append("")
    
    sql_content.append("-- 7. Payments Table")
    sql_content.append("CREATE TABLE Payments (")
    sql_content.append("    payment_id INT AUTO_INCREMENT PRIMARY KEY,")
    sql_content.append("    booking_id INT,")
    sql_content.append("    amount DECIMAL(10,2),")
    sql_content.append("    payment_date DATE,")
    sql_content.append("    status ENUM('Paid', 'Refunded', 'Pending'),")
    sql_content.append("    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE")
    sql_content.append(");")
    sql_content.append("")

    # DATA GENERATION
    
    # Airlines
    print("\n[1/7] Processing Airlines...")
    airlines = df[['Airlines_Name', 'Airline_Code']].drop_duplicates().reset_index(drop=True)
    airlines['airline_id'] = range(1, len(airlines) + 1)
    
    sql_content.append("-- INSERTING DATA: Airlines")
    sql_content.append("INSERT INTO Airlines (airline_name, airline_code) VALUES")
    airline_values = [f"('{escape_sql(row['Airlines_Name'])}', '{escape_sql(row['Airline_Code'])}')" 
                    for _, row in airlines.iterrows()]
    sql_content.append(",\n".join(airline_values) + ";")
    sql_content.append("")
    print(f"   [OK] Processed {len(airlines)} airlines")
    
    # Airports
    print("[2/7] Processing Airports...")
    source_airports = df[['Departure_Port', 'Departure_Port_Name']].rename(
        columns={'Departure_Port': 'City', 'Departure_Port_Name': 'Airport_Name'}
    )
    dest_airports = df[['Arrival_Port', 'Arrival_Port_Name']].rename(
        columns={'Arrival_Port': 'City', 'Arrival_Port_Name': 'Airport_Name'}
    )
    all_airports = pd.concat([source_airports, dest_airports]).drop_duplicates(subset=['Airport_Name']).reset_index(drop=True)
    
    # Use all airports from the dataset
    airports = all_airports.copy()
    airports['airport_id'] = range(1, len(airports) + 1)
    
    sql_content.append("-- INSERTING DATA: Airports")
    sql_content.append("INSERT INTO Airports (airport_name, city, owned_by) VALUES")
    # Insert NULL for owned_by since we removed it from the dataset
    airport_values = [f"('{escape_sql(r['Airport_Name'])}', '{escape_sql(r['City'])}', NULL)" 
                    for _, r in airports.iterrows()]
    sql_content.append(",\n".join(airport_values) + ";")
    sql_content.append("")
    print(f"   [OK] Processed {len(airports)} airports")
    
    # Flights
    print("[3/7] Filtering and Processing Flights...")
    valid_airlines = set(airlines['Airlines_Name'])
    valid_airports = set(airports['Airport_Name'])
    
    df_filtered = df[
        (df['Airlines_Name'].isin(valid_airlines)) &
        (df['Departure_Port_Name'].isin(valid_airports)) &
        (df['Arrival_Port_Name'].isin(valid_airports))
    ]
    
    # Remove duplicates based on route + flight number
    df_unique = df_filtered.drop_duplicates(subset=['Flight_Number', 'Departure_Port', 'Arrival_Port'], keep='first')
    
    # Sample flights (e.g., 2000)
    sample_size = min(2000, len(df_unique))
    if sample_size == 0:
        print("   [WARNING] No flights matched. Check dataset.")
        flights_sample = pd.DataFrame()
    else:
        flights_sample = df_unique.sample(sample_size)
        print(f"   [OK] Sampled {sample_size} unique flights from dataset")
    
    flights_data = []
    stops_data = []
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_spread = 90
    
    for idx, row in enumerate(tqdm(list(flights_sample.itertuples(index=False)), desc="Generating Flight Data"), 1):
        airline_id = airlines[airlines['Airlines_Name'] == row.Airlines_Name]['airline_id'].values[0]
        src_id = airports[airports['Airport_Name'] == row.Departure_Port_Name]['airport_id'].values[0]
        dest_id = airports[airports['Airport_Name'] == row.Arrival_Port_Name]['airport_id'].values[0]
        
        base_price = getattr(row, 'Fare', 5000)
        price = base_price if base_price > 0 else random.randint(3000, 15000)
        
        flight_id = idx
        stops = int(row.Stop)
        
        journey_date = start_date + timedelta(days=(idx % days_spread))
        journey_date_str = journey_date.strftime('%Y-%m-%d')
        
        total_seats = 180
        available_seats = random.randint(0, 180)
        
        # Duration is already in HH:MM:SS from cleaned CSV
        duration_str = str(row.Duration_Time)
        
        flights_data.append(
            f"({airline_id}, '{escape_sql(row.Flight_Number)}', {src_id}, {dest_id}, "
            f"'{journey_date_str}', '{row.Departure_Time}', '{row.Arrival_Time}', "
            f"'{escape_sql(duration_str)}', {stops}, '{escape_sql(row.Aircraft_Type)}', "
            f"{price}, {total_seats}, {available_seats})"
        )
        
        # Generate Stops Data (Multi-stop logic)
        if stops > 0:
            # Get available airports excluding source and dest
            # We need 'stops' number of unique airports
            possible_stop_ids = [aid for aid in airports['airport_id'] if aid not in [src_id, dest_id]]
            
            if len(possible_stop_ids) >= stops:
                selected_stop_ids = random.sample(possible_stop_ids, stops)
                
                # Calculate stop times
                # Parse times to datetime objects for calculation
                fmt = '%H:%M:%S'
                try:
                    dep_time = datetime.strptime(row.Departure_Time, fmt)
                    arr_time = datetime.strptime(row.Arrival_Time, fmt)
                    
                    # Handle overnight flights (arrival < departure)
                    if arr_time < dep_time:
                        arr_time += timedelta(days=1)
                        
                    total_duration_seconds = (arr_time - dep_time).total_seconds()
                    
                    # Divide duration into segments
                    # stops + 1 segments
                    segment_duration = total_duration_seconds / (stops + 1)
                    
                    current_time = dep_time
                    
                    for i, stop_aid in enumerate(selected_stop_ids, 1):
                        # Arrival at stop is after 1 segment (minus some layover time logic if we wanted to be super precise, 
                        # but simple segmentation is fine for mock data)
                        
                        # Let's say travel to stop takes 80% of segment, 20% is layover
                        travel_seconds = segment_duration * 0.8
                        layover_seconds = segment_duration * 0.2
                        
                        stop_arr_dt = current_time + timedelta(seconds=travel_seconds)
                        stop_dep_dt = stop_arr_dt + timedelta(seconds=layover_seconds)
                        
                        # Format back to HH:MM:SS
                        stop_arr_str = stop_arr_dt.strftime(fmt)
                        stop_dep_str = stop_dep_dt.strftime(fmt)
                        
                        stops_data.append(
                            f"({flight_id}, {stop_aid}, '{stop_arr_str}', '{stop_dep_str}', {i})"
                        )
                        
                        current_time = stop_dep_dt
                        
                except ValueError:
                    # Fallback if time parsing fails
                    pass

    sql_content.append("-- INSERTING DATA: Flights")
    sql_content.append("INSERT INTO Flights (airline_id, flight_number, source_airport_id, destination_airport_id, journey_date, departure_time, arrival_time, duration, stops, aircraft_type, price, total_seats, available_seats) VALUES")
    sql_content.append(",\n".join(flights_data) + ";")
    sql_content.append("")
    
    if stops_data:
        sql_content.append("-- INSERTING DATA: Flight_Stops")
        sql_content.append("INSERT INTO Flight_Stops (flight_id, airport_id, arrival_time, departure_time, stop_sequence) VALUES")
        sql_content.append(",\n".join(stops_data) + ";")
        sql_content.append("")
    
    # Users
    print("[4/7] Skipping User Generation (Real-time Registration Mode)...")
    sql_content.append("-- Users table will be populated via application registration")
    sql_content.append("")
    
    # Bookings & Payments
    print(f"[5/7] Skipping Bookings & Payments Generation (Real-time Mode)...")
    sql_content.append("-- Bookings and Payments tables will be populated via application usage")
    sql_content.append("")
    
    # Indexes, Triggers, Views, Procedures
    print("[6/7] Creating Indexes, Triggers, Views & Procedures...")
    sql_content.append("-- =====================================================")
    sql_content.append("-- PERFORMANCE INDEXES")
    sql_content.append("-- =====================================================")
    sql_content.append("CREATE INDEX idx_flights_journey ON Flights(journey_date);")
    # idx_flights_route is redundant because idx_flights_route_date covers it (leftmost prefix)
    # sql_content.append("CREATE INDEX idx_flights_route ON Flights(source_airport_id, destination_airport_id);")
    sql_content.append("CREATE INDEX idx_flights_airline ON Flights(airline_id);")
    sql_content.append("CREATE INDEX idx_flights_price ON Flights(price);")
    sql_content.append("CREATE INDEX idx_flights_seats ON Flights(available_seats);")
    sql_content.append("CREATE INDEX idx_bookings_user ON Bookings(user_id);")
    sql_content.append("CREATE INDEX idx_bookings_flight ON Bookings(flight_id);")
    sql_content.append("CREATE INDEX idx_bookings_date ON Bookings(booking_date);")
    sql_content.append("CREATE INDEX idx_bookings_status ON Bookings(status);")
    sql_content.append("CREATE INDEX idx_payments_status ON Payments(status);")
    sql_content.append("CREATE INDEX idx_airports_city ON Airports(city);")
    sql_content.append("CREATE INDEX idx_flights_route_date ON Flights(source_airport_id, destination_airport_id, journey_date);")
    sql_content.append("CREATE INDEX idx_bookings_user_status ON Bookings(user_id, status);")
    sql_content.append("CREATE INDEX idx_flights_avail ON Flights(available_seats, price);")
    sql_content.append("")
    
    sql_content.append("/* ---------------------------------------------------------")
    sql_content.append("   TRIGGERS")
    sql_content.append("--------------------------------------------------------- */")
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE TRIGGER reduce_seat_after_booking")
    sql_content.append("AFTER INSERT ON Bookings")
    sql_content.append("FOR EACH ROW")
    sql_content.append("BEGIN")
    sql_content.append("    IF NEW.status = 'Confirmed' THEN")
    sql_content.append("        UPDATE Flights")
    sql_content.append("        SET available_seats = available_seats - 1")
    sql_content.append("        WHERE flight_id = NEW.flight_id;")
    sql_content.append("    END IF;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")
    
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE TRIGGER increase_seat_on_cancel")
    sql_content.append("AFTER UPDATE ON Bookings")
    sql_content.append("FOR EACH ROW")
    sql_content.append("BEGIN")
    sql_content.append("    IF NEW.status = 'Cancelled' AND OLD.status != 'Cancelled' THEN")
    sql_content.append("        UPDATE Flights")
    sql_content.append("        SET available_seats = available_seats + 1")
    sql_content.append("        WHERE flight_id = NEW.flight_id;")
    sql_content.append("    END IF;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")
    
    sql_content.append("/* ---------------------------------------------------------")
    sql_content.append("   VIEWS")
    sql_content.append("--------------------------------------------------------- */")
    sql_content.append("CREATE VIEW Flight_Schedule_View AS")
    sql_content.append("SELECT f.flight_number, a.airline_name, ")
    sql_content.append("       src.city AS source_city, dst.city AS destination_city,")
    sql_content.append("       f.departure_time, f.arrival_time, f.duration, f.price")
    sql_content.append("FROM Flights f")
    sql_content.append("JOIN Airlines a ON f.airline_id = a.airline_id")
    sql_content.append("JOIN Airports src ON f.source_airport_id = src.airport_id")
    sql_content.append("JOIN Airports dst ON f.destination_airport_id = dst.airport_id;")
    sql_content.append("")
    
    sql_content.append("CREATE VIEW Booking_Summary_View AS")
    sql_content.append("SELECT b.booking_id, b.pnr, u.name AS passenger_name, f.flight_number, ")
    sql_content.append("       b.status, p.amount, p.status AS payment_status")
    sql_content.append("FROM Bookings b")
    sql_content.append("JOIN Users u ON b.user_id = u.user_id")
    sql_content.append("JOIN Flights f ON b.flight_id = f.flight_id")
    sql_content.append("LEFT JOIN Payments p ON b.booking_id = p.booking_id;")
    sql_content.append("")

    sql_content.append("/* ---------------------------------------------------------")
    sql_content.append("   STORED PROCEDURES (APPLICATION LOGIC & SEARCH)")
    sql_content.append("--------------------------------------------------------- */")
    sql_content.append("-- 1. Search Flights (Basic: Source, Dest, Date)")
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE PROCEDURE SearchFlights(IN p_source VARCHAR(100), IN p_dest VARCHAR(100), IN p_date DATE)")
    sql_content.append("BEGIN")
    sql_content.append("    SELECT f.flight_number, a.airline_name, f.departure_time, f.arrival_time, f.duration, f.price, f.available_seats")
    sql_content.append("    FROM Flights f")
    sql_content.append("    JOIN Airlines a ON f.airline_id = a.airline_id")
    sql_content.append("    JOIN Airports src ON f.source_airport_id = src.airport_id")
    sql_content.append("    JOIN Airports dst ON f.destination_airport_id = dst.airport_id")
    sql_content.append("    WHERE src.city = p_source AND dst.city = p_dest AND f.journey_date = p_date")
    sql_content.append("    ORDER BY f.price ASC;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")

    sql_content.append("-- 2. Search Flights with Price Filter (Min - Max)")
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE PROCEDURE SearchFlightsByPrice(IN p_source VARCHAR(100), IN p_dest VARCHAR(100), IN p_min_price DECIMAL(10,2), IN p_max_price DECIMAL(10,2))")
    sql_content.append("BEGIN")
    sql_content.append("    SELECT f.flight_number, a.airline_name, f.departure_time, f.price")
    sql_content.append("    FROM Flights f")
    sql_content.append("    JOIN Airlines a ON f.airline_id = a.airline_id")
    sql_content.append("    JOIN Airports src ON f.source_airport_id = src.airport_id")
    sql_content.append("    JOIN Airports dst ON f.destination_airport_id = dst.airport_id")
    sql_content.append("    WHERE src.city = p_source AND dst.city = p_dest")
    sql_content.append("    AND f.price BETWEEN p_min_price AND p_max_price")
    sql_content.append("    ORDER BY f.price ASC;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")
    
    sql_content.append("-- 3. Register a new user")
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE PROCEDURE RegisterUser(IN p_name VARCHAR(100), IN p_email VARCHAR(100), IN p_phone VARCHAR(15), IN p_password VARCHAR(255))")
    sql_content.append("BEGIN")
    sql_content.append("    IF EXISTS (SELECT 1 FROM Users WHERE email = p_email) THEN")
    sql_content.append("        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already registered';")
    sql_content.append("    ELSE")
    sql_content.append("        INSERT INTO Users (name, email, phone, password_hash) VALUES (p_name, p_email, p_phone, p_password);")
    sql_content.append("    END IF;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")
    
    sql_content.append("-- 4. Book a flight (Transactional with PNR & Custom Date & Seat Check)")
    sql_content.append("DELIMITER //")
    sql_content.append("CREATE PROCEDURE BookFlight(IN p_user_id INT, IN p_flight_id INT, IN p_seat_no VARCHAR(10), IN p_pnr VARCHAR(10), IN p_booking_date DATE)")
    sql_content.append("BEGIN")
    sql_content.append("    DECLARE v_booking_id INT;")
    sql_content.append("    DECLARE v_price DECIMAL(10,2);")
    sql_content.append("    DECLARE v_available_seats INT;")
    sql_content.append("    DECLARE EXIT HANDLER FOR SQLEXCEPTION")
    sql_content.append("    BEGIN")
    sql_content.append("        ROLLBACK;")
    sql_content.append("        RESIGNAL;")
    sql_content.append("    END;")
    sql_content.append("")
    sql_content.append("    -- Check Seat Availability")
    sql_content.append("    SELECT available_seats, price INTO v_available_seats, v_price FROM Flights WHERE flight_id = p_flight_id;")
    sql_content.append("")
    sql_content.append("    IF v_available_seats <= 0 THEN")
    sql_content.append("        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Flight is fully booked';")
    sql_content.append("    END IF;")
    sql_content.append("")
    sql_content.append("    START TRANSACTION;")
    sql_content.append("    -- Insert Booking")
    sql_content.append("    INSERT INTO Bookings (user_id, flight_id, booking_date, status, seat_no, pnr) ")
    sql_content.append("    VALUES (p_user_id, p_flight_id, p_booking_date, 'Confirmed', p_seat_no, p_pnr);")
    sql_content.append("    SET v_booking_id = LAST_INSERT_ID();")
    sql_content.append("")
    sql_content.append("    -- Insert Payment")
    sql_content.append("    INSERT INTO Payments (booking_id, amount, payment_date, status) ")
    sql_content.append("    VALUES (v_booking_id, v_price, p_booking_date, 'Paid');")
    sql_content.append("")
    sql_content.append("    COMMIT;")
    sql_content.append("    SELECT 'Booking Successful' AS Status, v_booking_id AS BookingID, p_pnr AS PNR, v_price AS AmountPaid;")
    sql_content.append("END //")
    sql_content.append("DELIMITER ;")
    sql_content.append("")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(sql_content))
    
    print(f"\n[7/7] Successfully generated {output_file}")

if __name__ == "__main__":
    generate_sql()
