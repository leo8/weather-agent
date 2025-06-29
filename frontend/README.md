# Weather Agent Frontend 🌤️

A modern, responsive web interface for the Weather Agent API.

## Features

- 🎨 **Modern UI**: Clean, weather-themed design with smooth animations
- 💬 **Chat Interface**: Natural conversation flow with the AI weather assistant
- 📱 **Responsive**: Works beautifully on desktop, tablet, and mobile
- ⚡ **Real-time**: Live connection status and instant responses
- 🌍 **Interactive**: Example queries and easy-to-use input

## Quick Start

1. **Start the API server** (in the project root):
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open the frontend**:
   ```bash
   # Option 1: Open directly in browser
   open frontend/index.html
   
   # Option 2: Serve with Python (recommended)
   cd frontend
   python -m http.server 3000
   # Then visit: http://localhost:3000
   
   # Option 3: Serve with Node.js
   cd frontend
   npx serve .
   ```

3. **Start chatting!** Try asking:
   - "What's the weather like in Paris today?"
   - "Will it rain tomorrow in Tokyo?"
   - "Should I bring a jacket to New York?"

## How It Works

1. **Natural Language Input**: Type weather questions in plain English
2. **AI Processing**: OpenAI GPT parses your query and extracts location/intent
3. **Weather Data**: Real-time weather data fetched from OpenWeatherMap
4. **Smart Response**: AI generates natural language response with weather details

## API Integration

The frontend communicates with the FastAPI backend via:
- **Endpoint**: `POST /query/`
- **Health Check**: `GET /health`
- **CORS**: Enabled for development

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+  
- ✅ Safari 14+
- ✅ Edge 90+

## Development

### File Structure
```
frontend/
├── index.html          # Main HTML structure
├── style.css           # Modern CSS styling
├── script.js           # JavaScript functionality
└── README.md          # This file
```

### Key Components
- **Chat Interface**: Real-time messaging with typing indicators
- **Weather Display**: Structured weather data presentation  
- **Status Indicator**: Live API connection status
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Mobile-first approach

### Customization

**Colors**: Edit CSS variables in `style.css`:
```css
:root {
    --primary-blue: #2563eb;
    --sky-blue: #0ea5e9;
    /* ... */
}
```

**API URL**: Update in `script.js`:
```javascript
this.apiBaseUrl = 'https://your-api-domain.com';
```

## Production Deployment

For production, serve the frontend files through:
- **Static hosting**: Netlify, Vercel, GitHub Pages
- **CDN**: CloudFront, CloudFlare  
- **Web server**: Nginx, Apache
- **Container**: Docker with nginx

Example nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

**Built with ❤️ using vanilla JavaScript, CSS3, and modern web APIs** 