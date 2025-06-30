// Environment Detection and Setup
function detectEnvironment() {
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Detect environment based on URL
    if (hostname === 'localhost' || hostname === '127.0.0.1' || port === '8080') {
        return 'local';
    } else if (hostname.includes('-dev') || hostname.includes('development')) {
        return 'development';
    } else {
        return 'production';
    }
}

function setupEnvironmentUI() {
    const env = detectEnvironment();
    const envBanner = document.getElementById('envBanner');
    const versionBadge = document.getElementById('versionBadge');
    const container = document.querySelector('.container');
    
    // Update version badge
    versionBadge.className = `version-badge ${env === 'production' ? 'prod' : env === 'development' ? 'dev' : 'local'}`;
    
    // Update version text
    if (env === 'local') {
        versionBadge.textContent = 'v1.1.0-local';
        document.title = 'Weather Agent 🌤️ - Local Development';
    } else if (env === 'development') {
        versionBadge.textContent = 'v1.1.0-dev';
        document.title = 'Weather Agent 🌤️ - Development';
    } else {
        versionBadge.textContent = 'v1.1.0';
        document.title = 'Weather Agent 🌤️ - AI Weather Assistant';
    }
    
    // Show environment banner for non-production
    if (env !== 'production') {
        envBanner.style.display = 'block';
        container.classList.add('has-banner');
        
        if (env === 'local') {
            envBanner.textContent = '💻 LOCAL DEVELOPMENT ENVIRONMENT 💻';
            envBanner.style.background = 'linear-gradient(135deg, #339af0, #228be6)';
        } else {
            envBanner.textContent = '🚧 DEVELOPMENT ENVIRONMENT 🚧';
        }
    }
    
    console.log(`🌤️ Weather Agent running in ${env} environment`);
}

// Initialize environment UI when page loads
document.addEventListener('DOMContentLoaded', setupEnvironmentUI);

// Weather Agent Frontend JavaScript
class WeatherAgent {
    constructor() {
        // Auto-detect API base URL based on environment
        this.apiBaseUrl = this.detectApiBaseUrl();
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.sendButton = document.getElementById('sendButton');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.errorModal = document.getElementById('errorModal');
        this.modalClose = document.getElementById('modalClose');
        this.errorMessage = document.getElementById('errorMessage');
        
        this.isLoading = false;
        this.messageId = 0;
        
        this.init();
    }
    
    detectApiBaseUrl() {
        // If running on the same domain (production), use relative URLs
        if (window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1')) {
            return window.location.origin;
        }
        // Local development
        return 'http://localhost:8080';
    }
    
    init() {
        this.setupEventListeners();
        this.checkAPIHealth();
        this.addWelcomeMessage();
        
        // Log API URL for debugging
        console.log(`API Base URL: ${this.apiBaseUrl}`);
    }
    
    setupEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Example chip clicks
        document.querySelectorAll('.example-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const query = chip.getAttribute('data-query');
                this.messageInput.value = query;
                this.handleSubmit();
            });
        });
        
        // Modal close
        this.modalClose.addEventListener('click', () => {
            this.hideModal();
        });
        
        // Input focus management
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit();
            }
        });
        
        // Focus input on load
        this.messageInput.focus();
    }
    
    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                this.updateStatus('connected');
                const data = await response.json();
                console.log('API Health:', data);
            } else {
                this.updateStatus('disconnected');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatus('disconnected');
        }
    }
    
    updateStatus(status) {
        const statusText = this.statusIndicator.querySelector('span');
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        
        if (status === 'connected') {
            statusText.textContent = 'Connected';
            this.statusIndicator.classList.remove('disconnected');
        } else {
            statusText.textContent = 'Disconnected';
            this.statusIndicator.classList.add('disconnected');
        }
    }
    
    addWelcomeMessage() {
        // Hide welcome section when first message is sent
        this.welcomeShown = true;
    }
    
    async handleSubmit() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Hide welcome section on first message
        if (this.welcomeShown) {
            document.querySelector('.welcome-section').style.display = 'none';
            this.welcomeShown = false;
        }
        
        // Add user message
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        
        // Show loading
        this.setLoading(true);
        
        try {
            // Send to API
            const response = await this.sendQuery(message);
            this.handleAPIResponse(response);
        } catch (error) {
            console.error('API Error:', error);
            this.addMessage(
                `Sorry, I encountered an error while processing your request. Please try again or check if the API server is running.\n\nError: ${error.message}`,
                'bot',
                true
            );
        } finally {
            this.setLoading(false);
        }
    }
    
    async sendQuery(query) {
        const response = await fetch(`${this.apiBaseUrl}/query/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
        }
        
        return await response.json();
    }
    
    handleAPIResponse(response) {
        // Add natural language response
        if (response.natural_response) {
            this.addMessage(response.natural_response, 'bot');
        }
        
        // Add weather data if available
        if (response.weather_data) {
            this.addWeatherData(response.weather_data);
        }
        
        // Show processing time if available
        if (response.processing_time_ms) {
            const timeMs = Math.round(response.processing_time_ms);
            console.log(`Processing time: ${timeMs}ms`);
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageId = ++this.messageId;
        const timestamp = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble ${isError ? 'error' : ''}">
                    ${this.formatMessage(content)}
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addWeatherData(weatherData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        let weatherHtml = '';
        
        // Current weather
        if (weatherData.current_weather) {
            const current = weatherData.current_weather;
            weatherHtml += `
                <div class="weather-data">
                    <div class="weather-header">
                        <i class="fas fa-thermometer-half"></i>
                        Current Weather in ${weatherData.location}
                    </div>
                    <div class="weather-current">
                        <div class="weather-item">
                            <span>Temperature:</span>
                            <strong>${current.temperature}°C</strong>
                        </div>
                        <div class="weather-item">
                            <span>Feels like:</span>
                            <strong>${current.feels_like}°C</strong>
                        </div>
                        <div class="weather-item">
                            <span>Humidity:</span>
                            <strong>${current.humidity}%</strong>
                        </div>
                        <div class="weather-item">
                            <span>Pressure:</span>
                            <strong>${current.pressure} hPa</strong>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Forecast data
        if (weatherData.forecast && weatherData.forecast.length > 0) {
            weatherHtml += `
                <div class="weather-data">
                    <div class="weather-header">
                        <i class="fas fa-calendar-alt"></i>
                        Forecast for ${weatherData.location}
                    </div>
                    <div class="forecast-items">
                        ${weatherData.forecast.slice(0, 5).map(item => {
                            const dateTime = new Date(item.date);
                            const today = new Date();
                            const tomorrow = new Date(today);
                            tomorrow.setDate(today.getDate() + 1);
                            
                            // Format date and time based on when it is
                            let dateLabel;
                            if (dateTime.toDateString() === today.toDateString()) {
                                dateLabel = `Today ${dateTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
                            } else if (dateTime.toDateString() === tomorrow.toDateString()) {
                                dateLabel = `Tomorrow ${dateTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
                            } else {
                                dateLabel = `${dateTime.toLocaleDateString()} ${dateTime.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
                            }
                            
                            const temp = item.weather_data?.temperature || 'N/A';
                            const desc = item.conditions?.[0]?.description || 'No description';
                            return `
                                <div class="weather-item">
                                    <span>${dateLabel}</span>
                                    <strong>${temp}°C - ${desc}</strong>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        
        if (weatherHtml) {
            const timestamp = new Date().toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    ${weatherHtml}
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
            
            this.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();
        }
    }
    
    formatMessage(content) {
        // Convert line breaks to HTML
        return content.replace(/\n/g, '<br>');
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.loadingIndicator.style.display = 'flex';
            this.scrollToBottom();
        } else {
            this.loadingIndicator.style.display = 'none';
            this.messageInput.focus();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    showModal(message) {
        this.errorMessage.textContent = message;
        this.errorModal.style.display = 'flex';
    }
    
    hideModal() {
        this.errorModal.style.display = 'none';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherAgent();
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Network connection restored');
});

window.addEventListener('offline', () => {
    console.log('Network connection lost');
});

// Service worker registration (if needed for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment if you add a service worker
        // navigator.serviceWorker.register('/sw.js');
    });
} 