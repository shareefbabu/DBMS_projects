"""
Utility functions for the Flight Booking System
Extracted from api_server.py for better code organization
"""
import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def precompute_locations(df):
    """
    Pre-compute and cache location data from DataFrame
    
    Args:
        df: Pandas DataFrame containing flight data
        
    Returns:
        dict: Dictionary containing airports, cities, and mapping data
    """
    # Extract unique airport names
    departure_airports = df['Departure_Port_Name'].dropna().unique().tolist()
    arrival_airports = df['Arrival_Port_Name'].dropna().unique().tolist()
    all_airports = sorted(list(set(departure_airports + arrival_airports)))
    
    # City-to-airport manual mapping
    city_to_airport_manual = {
        'delhi': 'Indira Gandhi International Airport',
        'new delhi': 'Indira Gandhi International Airport',
        'bengaluru': 'Kempegowda International Airport',
        'bangalore': 'Kempegowda International Airport',
        'mumbai': 'Chhatrapati Shivaji Maharaj International Airport',
        'bombay': 'Chhatrapati Shivaji Maharaj International Airport',
        'chennai': 'Chennai International Airport',
        'madras': 'Chennai International Airport',
        'kolkata': 'Netaji Subhas Chandra Bose International Airport',
        'calcutta': 'Netaji Subhas Chandra Bose International Airport',
        'hyderabad': 'Rajiv Gandhi International Airport',
        'pune': 'Pune Airport',
        'ahmedabad': 'Sardar Vallabhbhai Patel International Airport',
        'kochi': 'Cochin International Airport',
        'cochin': 'Cochin International Airport',
        'goa': 'Goa Dabolim Airport',
        'jaipur': 'Jaipur International Airport',
        'lucknow': 'Chaudhary Charan Singh International Airport',
        'bhubaneswar': 'Biju Patnaik International Airport',
        'thiruvananthapuram': 'Trivandrum International Airport',
        'trivandrum': 'Trivandrum International Airport',
        'nagpur': 'Dr. Babasaheb Ambedkar International Airport',
        'kozhikode': 'Calicut International Airport',
        'calicut': 'Calicut International Airport',
        'coimbatore': 'Coimbatore International Airport',
        'indore': 'Devi Ahilya Bai Holkar Airport',
        'gaya': 'Gaya International Airport',
        'varanasi': 'Maharishi Valmiki International Airport',
        'srinagar': 'Sheikh ul-Alam International Airport',
        'bhopal': 'Raja Bhoj International Airport',
        'amritsar': 'Sri Guru Ram Dass Jee International Airport',
        'mangalore': 'Mangalore International Airport',
        'madurai': 'Madurai International Airport',
        'kannur': 'Kannur International Airport',
        'nashik': 'Nashik Airport (Ozar)',
        'tiruchirappalli': 'Tiruchirappalli International Airport',
        'trichy': 'Tiruchirappalli International Airport',
        'surat': 'Surat International Airport',
        'visakhapatnam': 'Visakhapatnam International Airport',
        'vizag': 'Visakhapatnam International Airport',
        'raipur': 'Swami Vivekananda Airport',
        'agartala': 'Maharaja Bir Bikram Airport',
        'port blair': 'Veer Savarkar International Airport',
        'guwahati': 'Lokpriya Gopinath Bordoloi International Airport',
    }
    
    # Extract city names
    cities = set()
    airport_city_map = {}
    
    for city, airport in city_to_airport_manual.items():
        if airport in all_airports:
            airport_city_map[city] = airport
            base_city = city.split()[0] if ' ' in city else city
            cities.add(base_city.title())
    
    for airport in all_airports:
        airport_city_map[airport.lower()] = airport
        city = None
        airport_lower = airport.lower()
        
        if 'international airport' in airport_lower:
            city = airport.split('International Airport')[0].strip()
        elif 'airport' in airport_lower:
            city = airport.split('Airport')[0].strip()
        else:
            city = airport.strip()
        
        city = re.sub(r'\([^)]*\)', '', city).strip()
        
        if city:
            cities.add(city)
            airport_city_map[city.lower()] = airport
    
    cities_list = sorted(list(cities))
    
    return {
        'airports': all_airports,
        'cities': cities_list,
        'airport_city_map': airport_city_map,
        'departure_airports': sorted(departure_airports),
        'arrival_airports': sorted(arrival_airports),
        'count': len(all_airports)
    }


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate Indian phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    pattern = r'^(\+91)?[6-9]\d{9}$'
    phone_clean = phone.replace(' ', '').replace('-', '')
    return bool(re.match(pattern, phone_clean))
