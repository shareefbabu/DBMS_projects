/**
 * Flight Booking System - Frontend Application
 * Handles all client-side logic, API communication, and UI interactions
 */

// ===================================
// Configuration
// ===================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',
    TOAST_DURATION: 5000,
    DATE_FORMAT: 'YYYY-MM-DD'
};

// ===================================
// State Management
// ===================================

const state = {
    currentUser: null,
    currentFlights: [],
    currentBookings: [],
    isAuthenticated: false
};

// ===================================
// API Client
// ===================================

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Important for session cookies
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication endpoints
    async register(userData) {
        return await this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return await this.request('/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async logout() {
        return await this.request('/logout', {
            method: 'POST'
        });
    }

    async getSession() {
        return await this.request('/session');
    }

    // Flight endpoints
    async searchFlights(source, destination, date) {
        const params = new URLSearchParams({ source, destination, date });
        return await this.request(`/search?${params}`);
    }

    async searchFlightsFromCSV(source, destination, date) {
        const params = new URLSearchParams({ source, destination, date });
        return await this.request(`/flights/csv?${params}`);
    }

    async getFlightDetails(flightNumber) {
        return await this.request(`/flight/${flightNumber}`);
    }

    // Location endpoints
    async getLocations() {
        return await this.request('/locations');
    }

    // Booking endpoints
    async bookFlight(bookingData) {
        return await this.request('/book', {
            method: 'POST',
            body: JSON.stringify(bookingData)
        });
    }

    async getUserBookings() {
        return await this.request('/bookings');
    }
}

const api = new APIClient(CONFIG.API_BASE_URL);

// ===================================
// UI Utilities
// ===================================

class UI {
    static showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    static hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    static showToast(title, message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');

        toast.className = `toast ${type} active`;
        toastTitle.textContent = title;
        toastMessage.textContent = message;

        setTimeout(() => {
            toast.classList.remove('active');
        }, CONFIG.TOAST_DURATION);
    }

    static showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    static hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
        document.body.style.overflow = '';
    }

    static updateAuthUI(user) {
        if (user) {
            // User is logged in
            document.getElementById('userInfo').style.display = 'flex';
            document.getElementById('authButtons').style.display = 'none';
            document.getElementById('userName').textContent = user.name;
            document.getElementById('myBookingsLink').style.display = 'block';
        } else {
            // User is logged out
            document.getElementById('userInfo').style.display = 'none';
            document.getElementById('authButtons').style.display = 'flex';
            document.getElementById('myBookingsLink').style.display = 'none';
        }
    }

    static formatPrice(price) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0
        }).format(price);
    }

    static formatTime(timeString) {
        // Convert "HH:MM:SS" to "HH:MM"
        return timeString ? timeString.substring(0, 5) : 'N/A';
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    static calculateDuration(duration) {
        // Duration is in "HH:MM:SS" format
        if (!duration) return 'N/A';
        const parts = duration.split(':');
        const hours = parseInt(parts[0]);
        const minutes = parseInt(parts[1]);
        return `${hours}h ${minutes}m`;
    }
}

// ===================================
// Autocomplete Manager
// ===================================

class AutocompleteManager {
    constructor(inputElement, dropdownElement, suggestions = [], cityAirportMap = {}) {
        this.input = inputElement;
        this.dropdown = dropdownElement;
        this.allSuggestions = suggestions;
        this.cityAirportMap = cityAirportMap;  // NEW: City to airport mapping
        this.filteredSuggestions = [];
        this.selectedIndex = -1;
        this.isOpen = false;
        
        this.setupEventListeners();
    }
    
    setSuggestions(suggestions, cityAirportMap = {}) {
        this.allSuggestions = suggestions;
        this.cityAirportMap = cityAirportMap;
    }
    
    setupEventListeners() {
        // Input event with debouncing
        let debounceTimer;
        this.input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.handleInput(e.target.value);
            }, 150); // 150ms debounce
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectNext();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.selectPrevious();
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (this.selectedIndex >= 0) {
                        this.selectSuggestion(this.filteredSuggestions[this.selectedIndex]);
                    }
                    break;
                case 'Escape':
                    this.close();
                    break;
            }
        });
        
        // Focus event - show dropdown if has value
        this.input.addEventListener('focus', () => {
            if (this.input.value.trim()) {
                this.handleInput(this.input.value);
            }
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.close();
            }
        });
    }
    
    handleInput(value) {
        const query = value.trim().toLowerCase();
        
        if (!query) {
            this.close();
            return;
        }
        
        // NEW: Enhanced filtering to support city-based search
        // First, check if the query matches a city name in the mapping
        let matchedAirport = null;
        if (this.cityAirportMap[query]) {
            // Direct city match - prioritize this airport
            matchedAirport = this.cityAirportMap[query];
        }
        
        // Filter suggestions (case-insensitive, partial match)
        // This will match both airport names and city names
        this.filteredSuggestions = this.allSuggestions.filter(suggestion => {
            const suggestionLower = suggestion.toLowerCase();
            
            // Direct match in airport name
            if (suggestionLower.includes(query)) {
                return true;
            }
            
            // Check if any city in the mapping matches and points to this airport
            for (const [city, airport] of Object.entries(this.cityAirportMap)) {
                if (city.includes(query) && airport === suggestion) {
                    return true;
                }
            }
            
            return false;
        });
        
        // If we found a direct city match, ensure it's first
        if (matchedAirport && this.filteredSuggestions.includes(matchedAirport)) {
            this.filteredSuggestions = [
                matchedAirport,
                ...this.filteredSuggestions.filter(s => s !== matchedAirport)
            ];
        }
        
        this.selectedIndex = -1;
        this.render();
        this.open();
    }
    
    
    render() {
        if (this.filteredSuggestions.length === 0) {
            this.dropdown.innerHTML = `
                <div class="autocomplete-no-results">
                    No airports found
                </div>
            `;
            return;
        }
        
        // Limit to 10 suggestions for performance
        const displaySuggestions = this.filteredSuggestions.slice(0, 10);
        
        this.dropdown.innerHTML = displaySuggestions.map((suggestion, index) => {
            // Extract city name from airport name if possible
            let displayText = suggestion;
            const query = this.input.value.trim().toLowerCase();
            
            // Check if user typed a city name that maps to this airport
            let matchedCity = null;
            for (const [city, airport] of Object.entries(this.cityAirportMap)) {
                if (airport === suggestion && city.includes(query) && !suggestion.toLowerCase().includes(query)) {
                    matchedCity = city;
                    break;
                }
            }
            
            // Format display: show "City → Airport Name" if city match, otherwise just airport
            if (matchedCity) {
                const cityFormatted = matchedCity.charAt(0).toUpperCase() + matchedCity.slice(1);
                displayText = `
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-weight: 600; color: var(--primary-color);">${this.highlightMatch(cityFormatted, query)}</span>
                        <span style="color: var(--text-muted); font-size: 0.875rem;">→</span>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">${suggestion}</span>
                    </div>
                `;
            } else {
                displayText = `
                    <div>
                        <span style="color: var(--text-primary);">${this.highlightMatch(suggestion, query)}</span>
                    </div>
                `;
            }
            
            return `
                <div class="autocomplete-item ${index === this.selectedIndex ? 'active' : ''}" 
                     data-index="${index}"
                     data-value="${suggestion}">
                    ${displayText}
                </div>
            `;
        }).join('');
        
        // Add click listeners to items
        this.dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item.dataset.value);
            });
        });
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    selectNext() {
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredSuggestions.length - 1);
        this.render();
        this.scrollToSelected();
    }
    
    selectPrevious() {
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.render();
        this.scrollToSelected();
    }
    
    scrollToSelected() {
        const activeItem = this.dropdown.querySelector('.autocomplete-item.active');
        if (activeItem) {
            activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }
    
    selectSuggestion(value) {
        this.input.value = value;
        this.close();
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    open() {
        this.dropdown.style.display = 'block';
        this.isOpen = true;
    }
    
    close() {
        this.dropdown.style.display = 'none';
        this.isOpen = false;
        this.selectedIndex = -1;
    }
}

// ===================================
// Flight Search & Display
// ===================================


function renderFlightCard(flight) {
    // Render stop details
    let stopDetailsHTML = '';
    if (flight.stop_details && flight.stop_details.length > 0) {
        stopDetailsHTML = `
            <div class="stops-section" style="margin-top: 1rem; padding: 1rem; background: var(--background-secondary); border-radius: 8px;">
                <div style="font-weight: 600; margin-bottom: 0.75rem; color: var(--text-primary); font-size: 0.875rem;">
                    ✈️ Stop Details (${flight.stops} stop${flight.stops !== 1 ? 's' : ''})
                </div>
                ${flight.stop_details.map(stop => `
                    <div style="display: flex; gap: 1rem; padding: 0.5rem; border-left: 3px solid var(--primary-color); margin-bottom: 0.5rem; background: var(--background-primary);">
                        <div style="min-width: 60px;">
                            <div style="font-size: 0.75rem; color: var(--text-muted);">Stop ${stop.stop_number}</div>
                            <div style="font-weight: 600; color: var(--text-primary);">${stop.arrival_time}</div>
                        </div>
                        <div style="flex: 1;">
                            <div style="font-size: 0.875rem; color: var(--text-primary);">${stop.location}</div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Layover: ${stop.duration_minutes} mins</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else if (flight.stops > 0) {
        stopDetailsHTML = `
            <div class="stops-section" style="margin-top: 1rem; padding: 0.75rem; background: var(--background-secondary); border-radius: 8px;">
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ℹ️ This flight has ${flight.stops} stop${flight.stops !== 1 ? 's' : ''}
                </div>
            </div>
        `;
    }
    
    
    return `
        <div class="flight-card" style="animation-delay: ${Math.random() * 0.2}s;">
            <div class="flight-header">
                <div class="airline-info" style="display: flex; align-items: center; gap: 1rem;">
                    ${flight.airline_logo ? `
                        <img src="${flight.airline_logo}" 
                             alt="${flight.airline_name || 'Airline'}" 
                             class="airline-logo"
                             style="height: 32px; width: auto; object-fit: contain; border-radius: 4px;"
                             onerror="this.style.display='none'">
                    ` : ''}
                    <div>
                        <div class="airline-name">${flight.airline_name || 'Unknown Airline'}</div>
                        <div class="flight-number">Flight ${flight.flight_number || 'N/A'}</div>
                    </div>
                </div>
                <div class="flight-price">${UI.formatPrice(flight.price || 0)}</div>
            </div>
            
            ${flight.pnr_number ? `
                <div style="display: inline-block; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem;">
                    PNR: ${flight.pnr_number}
                </div>
            ` : ''}
            
            <div class="flight-route">
                <div class="route-point">
                    <div class="route-time">${UI.formatTime(flight.departure_time)}</div>
                    <div class="route-city">${flight.source || 'Unknown'}</div>

                </div>
                
                <div class="route-separator">
                    <span>${UI.calculateDuration(flight.duration)}</span>
                    <div class="route-line"></div>
                    <span>${flight.stops || 0} stop${flight.stops !== 1 ? 's' : ''}</span>
                </div>
                
                <div class="route-point">
                    <div class="route-time">${UI.formatTime(flight.arrival_time)}</div>
                    <div class="route-city">${flight.destination || 'Unknown'}</div>
                </div>
            </div>
            
            ${stopDetailsHTML}
            
            <div class="flight-details">
                <div class="flight-info">
                    <div class="info-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2 6L8 2L14 6V13C14 13.5304 13.7893 14.0391 13.4142 14.4142C13.0391 14.7893 12.5304 15 12 15H4C3.46957 15 2.96086 14.7893 2.58579 14.4142C2.21071 14.0391 2 13.5304 2 13V6Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        ${flight.aircraft_type || 'N/A'}
                    </div>
                    <div class="info-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="2" y="4" width="12" height="10" rx="1" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M6 2V4M10 2V4M2 7H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        ${UI.formatDate(flight.journey_date)}
                    </div>
                    <div class="info-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 14C11.3137 14 14 11.3137 14 8C14 4.68629 11.3137 2 8 2C4.68629 2 2 4.68629 2 8C2 11.3137 4.68629 14 8 14Z" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M5.5 5.5L8 8L10 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        ${flight.available_seats || 0} seats left
                    </div>
                </div>
                
                <button 
                    class="btn btn-primary" 
                    onclick="handleBookNow(${flight.flight_id}, '${flight.flight_number}', '${flight.journey_date}')"
                    ${flight.available_seats <= 0 ? 'disabled' : ''}
                >
                    ${flight.available_seats <= 0 ? 'Sold Out' : 'Book Now'}
                </button>
            </div>
        </div>
    `;
}

function displayFlights(flights, searchCriteria) {
    const resultsSection = document.getElementById('results');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultsCount = document.getElementById('resultsCount');
    const noResults = document.getElementById('noResults');

    resultsSection.style.display = 'block';

    if (flights && flights.length > 0) {
        resultsGrid.innerHTML = flights.map(renderFlightCard).join('');
        
        // Enhanced results count with search criteria
        let countHTML = `<strong>${flights.length}</strong> flight${flights.length !== 1 ? 's' : ''} found`;
        if (searchCriteria) {
            countHTML += ` <span style="color: var(--text-secondary); font-size: 0.875rem;">for ${searchCriteria.departure} → ${searchCriteria.arrival} on ${searchCriteria.date}</span>`;
        }
        resultsCount.innerHTML = countHTML;
        
        resultsGrid.style.display = 'grid';
        noResults.style.display = 'none';
    } else {
        resultsGrid.style.display = 'none';
        noResults.style.display = 'block';
        resultsCount.textContent = 'No flights found';
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===================================
// Event Handlers
// ===================================

async function handleSearch(event) {
    event.preventDefault();

    const source = document.getElementById('source').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const date = document.getElementById('date').value;

    if (!source || !destination || !date) {
        UI.showToast('Validation Error', 'Please fill in all fields', 'error');
        return;
    }

    // Validate date
    const selectedDate = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate < today) {
        UI.showToast('Invalid Date', 'Please select a future date', 'error');
        return;
    }

    try {
        UI.showLoading();
       
        // Use CSV data source by default
        const useCSV = document.getElementById('useCSV')?.checked ?? true;
        
        let response;
        if (useCSV) {
            response = await api.searchFlightsFromCSV(source, destination, date);
        } else {
            response = await api.searchFlights(source, destination, date);
        }
        
        state.currentFlights = response.flights || [];
        displayFlights(state.currentFlights, response.search_criteria);
        
        if (response.flights && response.flights.length > 0) {
            const sourceLabel = response.source === 'CSV' ? 'from CSV file' : 'from database';
            UI.showToast('Success', `Found ${response.flights.length} flights ${sourceLabel}`, 'success');
        } else {
            UI.showToast('No Results', 'No flights found for your search criteria. Try different cities or dates.', 'info');
        }
    } catch (error) {
        UI.showToast('Search Failed', error.message || 'Unable to search flights', 'error');
        displayFlights([], null);
    } finally {
        UI.hideLoading();
    }
}

function handleBookNow(flightId, flightNumber, journeyDate) {
    if (!state.isAuthenticated) {
        UI.showToast('Login Required', 'Please login to book flights', 'info');
        UI.showModal('loginModal');
        return;
    }

    // Find flight in current flights
    const flight = state.currentFlights.find(f => f.flight_id === flightId);
    
    if (!flight) {
        UI.showToast('Error', 'Flight not found', 'error');
        return;
    }

    // Populate booking modal
    const bookingDetails = document.getElementById('bookingDetails');
    bookingDetails.innerHTML = `
        <div style="display: grid; gap: 1rem;">
            <div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">Flight</div>
                <div style="font-weight: 600; font-size: 1.125rem;">${flight.airline_name} - ${flight.flight_number}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">From</div>
                    <div style="font-weight: 500;">${flight.source}</div>
                    <div style="color: var(--text-muted); font-size: 0.875rem;">${UI.formatTime(flight.departure_time)}</div>
                </div>
                <div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">To</div>
                    <div style="font-weight: 500;">${flight.destination}</div>
                    <div style="color: var(--text-muted); font-size: 0.875rem;">${UI.formatTime(flight.arrival_time)}</div>
                </div>
            </div>
            <div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">Date</div>
                <div style="font-weight: 500;">${UI.formatDate(flight.journey_date)}</div>
            </div>
            <div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">Price</div>
                <div style="font-weight: 700; font-size: 1.5rem; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${UI.formatPrice(flight.price)}</div>
            </div>
        </div>
    `;

    document.getElementById('bookingFlightId').value = flightId;
    document.getElementById('bookingDate').value = journeyDate;
    document.getElementById('seatNumber').value = '';
    
    UI.showModal('bookingModal');
}

async function handleBookingSubmit(event) {
    event.preventDefault();

    const flightId = document.getElementById('bookingFlightId').value;
    const seatNo = document.getElementById('seatNumber').value.trim().toUpperCase();
    const bookingDate = document.getElementById('bookingDate').value;

    if (!seatNo.match(/^[0-9]{1,3}[A-F]$/)) {
        UI.showToast('Invalid Seat', 'Please enter a valid seat number (e.g., 12A)', 'error');
        return;
    }

    try {
        UI.showLoading();
        const response = await api.bookFlight({
            flight_id: parseInt(flightId),
            seat_no: seatNo,
            booking_date: bookingDate
        });

        UI.hideModal('bookingModal');
        UI.showToast('Booking Confirmed!', response.message || `Your PNR is ${response.pnr}`, 'success');
        
        // Optionally refresh the search results
        document.getElementById('searchForm').dispatchEvent(new Event('submit'));
    } catch (error) {
        UI.showToast('Booking Failed', error.message || 'Unable to complete booking', 'error');
    } finally {
        UI.hideLoading();
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    try {
        UI.showLoading();
        const response = await api.login({ email, password });
        
        state.currentUser = response.user;
        state.isAuthenticated = true;
        
        UI.updateAuthUI(response.user);
        UI.hideModal('loginModal');
        UI.showToast('Welcome!', response.message || 'Login successful', 'success');
        
        // Clear form
        document.getElementById('loginForm').reset();
    } catch (error) {
        UI.showToast('Login Failed', error.message || 'Invalid credentials', 'error');
    } finally {
        UI.hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const name = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const phone = document.getElementById('registerPhone').value.trim();
    const password = document.getElementById('registerPassword').value;

    try {
        UI.showLoading();
        const response = await api.register({ name, email, phone, password });
        
        UI.hideModal('registerModal');
        UI.showToast('Registration Successful!', response.message || 'You can now login', 'success');
        
        // Clear form and show login modal
        document.getElementById('registerForm').reset();
        setTimeout(() => {
            UI.showModal('loginModal');
        }, 500);
    } catch (error) {
        UI.showToast('Registration Failed', error.message || 'Unable to register', 'error');
    } finally {
        UI.hideLoading();
    }
}

async function handleLogout() {
    try {
        UI.showLoading();
        await api.logout();
        
        state.currentUser = null;
        state.isAuthenticated = false;
        
        UI.updateAuthUI(null);
        UI.showToast('Logged Out', 'You have been logged out successfully', 'info');
        
        // Hide results and bookings
        document.getElementById('results').style.display = 'none';
        document.getElementById('bookings').style.display = 'none';
    } catch (error) {
        UI.showToast('Logout Failed', error.message, 'error');
    } finally {
        UI.hideLoading();
    }
}

async function initAutocomplete() {
    try {
        const locationsData = await api.getLocations();
        
        // Use 'airports' field (preferred) or fallback to 'all_cities' for backward compatibility
        const airportNames = locationsData.airports || locationsData.all_cities;
        const cityAirportMap = locationsData.airport_city_map || {};
        
        if (locationsData.success && airportNames && airportNames.length > 0) {
            console.log(`Loaded ${airportNames.length} airports for autocomplete`);
            console.log(`City-to-airport mapping contains ${Object.keys(cityAirportMap).length} entries`);
            
            // Create autocomplete for source input
            const sourceInput = document.getElementById('source');
            const sourceDropdown = document.getElementById('sourceDropdown');
            if (sourceInput && sourceDropdown) {
                new AutocompleteManager(
                    sourceInput,
                    sourceDropdown,
                    airportNames,
                    cityAirportMap
                );
            }
            
            // Create autocomplete for destination input
            const destinationInput = document.getElementById('destination');
            const destinationDropdown = document.getElementById('destinationDropdown');
            if (destinationInput && destinationDropdown) {
                new AutocompleteManager(
                    destinationInput,
                    destinationDropdown,
                    airportNames,
                    cityAirportMap
                );
            }
            
            console.log('Airport autocomplete with city search initialized successfully!');
        } else {
            console.warn('No airport data available for autocomplete');
        }
    } catch (error) {
        console.error('Failed to initialize airport autocomplete:', error);
    }
    
    // Set up event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Search form
    document.getElementById('searchForm').addEventListener('submit', handleSearch);

    // Login modal
    document.getElementById('loginBtn').addEventListener('click', () => UI.showModal('loginModal'));
    document.getElementById('loginClose').addEventListener('click', () => UI.hideModal('loginModal'));
    document.getElementById('loginOverlay').addEventListener('click', () => UI.hideModal('loginModal'));
    document.getElementById('loginForm').addEventListener('submit', handleLogin);

    // Register modal
    document.getElementById('registerBtn').addEventListener('click', () => UI.showModal('registerModal'));
    document.getElementById('registerClose').addEventListener('click', () => UI.hideModal('registerModal'));
    document.getElementById('registerOverlay').addEventListener('click', () => UI.hideModal('registerModal'));
    document.getElementById('registerForm').addEventListener('submit', handleRegister);

    // Switch between login and register
    document.getElementById('switchToRegister').addEventListener('click', (e) => {
        e.preventDefault();
        UI.hideModal('loginModal');
        UI.showModal('registerModal');
    });

    document.getElementById('switchToLogin').addEventListener('click', (e) => {
        e.preventDefault();
        UI.hideModal('registerModal');
        UI.showModal('loginModal');
    });

    // Booking modal
    document.getElementById('bookingClose').addEventListener('click', () => UI.hideModal('bookingModal'));
    document.getElementById('bookingOverlay').addEventListener('click', () => UI.hideModal('bookingModal'));
    document.getElementById('bookingForm').addEventListener('submit', handleBookingSubmit);

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Toast close
    document.getElementById('toastClose').addEventListener('click', () => {
        document.getElementById('toast').classList.remove('active');
    });

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href').substring(1);
            
            // Update active state
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Scroll to section
            const section = document.getElementById(target);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.active');
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });
}

async function handleForgotPassword(event) {
    event.preventDefault();
    
    const email = document.getElementById('forgotEmail').value.trim();
    
    if (!email) {
        UI.showToast('Error', 'Please enter your email address', 'error');
        return;
    }
    
    try {
        UI.showLoading();
        
        const response = await fetch(`${CONFIG.API_BASE_URL}/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            UI.hideModal('forgotPasswordModal');
            UI.showToast('Success', data.message || 'Password reset instructions sent to your email', 'success');
            document.getElementById('forgotPasswordForm').reset();
        } else {
            throw new Error(data.message || 'Failed to send reset email');
        }
    } catch (error) {
        UI.showToast('Error', error.message, 'error');
    } finally {
        UI.hideLoading();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check for session
    api.getSession().then(response => {
        if (response.user) {
            state.currentUser = response.user;
            state.isAuthenticated = true;
            UI.updateAuthUI(response.user);
        }
    }).catch(() => {
        // Session check failed, user is not logged in
        console.log('No active session');
    });

    // Initialize autocomplete
    initAutocomplete();
});
