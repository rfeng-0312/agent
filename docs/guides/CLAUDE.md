# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "名侦探作业帮" (Detective Study Tool), a Flask-based educational web application for solving physics and chemistry problems with AI assistance. The application features a Detective Conan theme with animated particle effects and dark cyberpunk aesthetics. It supports both text-only queries (using DeepSeek API) and image-based queries (using ChatGLM API).

## Architecture

### Backend Structure (Flask)
- **Flask Application**: Main backend server in `app.py`
- **API Endpoints**: RESTful APIs for text and image queries
- **File Uploads**: Handles image uploads with validation and security
- **CORS Support**: Cross-origin requests enabled for frontend-backend communication
- **Template System**: Jinja2 templates for dynamic HTML rendering

### Frontend Structure
- **Flask Templates**: HTML files in `templates/` directory using Jinja2 syntax
- **Static Assets**: CSS, JavaScript, and images in `static/` directory
- **Theming**: Dual themes for Physics (blue) and Chemistry (red) with dynamic switching
- **Animation-Heavy**: Extensive CSS animations for particle systems, backgrounds, and UI effects

### Key Files
- `app.py` - Flask application with API endpoints
- `requirements.txt` - Python dependencies (Flask, Flask-CORS, Werkzeug)
- `templates/test.html` - Main application template
- `static/script.js` - Frontend JavaScript with backend communication
- `static/styles.css` - Custom animations, themes, and responsive styles
- `static/67a99ed6f3db4z2m7bdnw17636.jpg` - Conan detective mascot image

### Technical Patterns
- **Flask-CORS**: Handles cross-origin requests between frontend and backend
- **RESTful APIs**: Standardized endpoints for different query types
- **FormData Handling**: Multipart form data for image uploads
- **Async JavaScript**: Fetch API for backend communication
- **Glass-morphism**: UI cards with backdrop blur and transparency effects
- **Particle System**: Animated subject-specific symbols (atoms for physics, flasks for chemistry)

## Development Commands

### Setting up the Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask development server
python app.py
```

### Running the Application
```bash
# Flask will serve on http://localhost:5000
# Access the application in your browser
```

### Development Tools
- **Backend**: Python with Flask framework
- **Frontend**: No build tools - pure HTML5, CSS3, and vanilla JavaScript
- **Dependencies**: Python packages in requirements.txt, frontend via CDN (Tailwind CSS, Font Awesome)
- **Testing**: Manual testing in browser with Flask development server

### Flask Development Server
- Default port: 5000
- Debug mode enabled
- Auto-restart on file changes
- CORS configured for frontend-backend communication

## Development Guidelines

### Theme System
- **Physics Theme**: Blue color palette with atomic particle symbols
- **Chemistry Theme**: Red color palette with chemistry flask symbols
- Colors defined in HTML head: `teitanBlue`, `conanRed`, `neonCyan`, etc.
- Theme switching affects particles, button colors, and glowing effects

### Animation Architecture
- Background: Layered system (stars, moon, city silhouette)
- UI: Floating cards, glowing buttons, typewriter text effects
- Particles: Dynamic generation based on selected subject tab
- All animations prefer CSS over JavaScript for performance

### Code Organization
- Keep HTML structure semantic with proper ARIA labels
- CSS uses custom properties for maintainable theming
- JavaScript is modular with clear separation of concerns
- Responsive breakpoints at 768px for mobile adaptation

### API Integration Patterns
- **Text Queries**: Use `/api/query/text` endpoint for DeepSeek API integration
- **Image Queries**: Use `/api/query/image` endpoint for ChatGLM API integration
- **Base64 Support**: Alternative `/api/query/base64` endpoint available
- **Error Handling**: Consistent JSON error responses across all endpoints
- **File Validation**: Secure filename handling and file type restrictions

### Backend Development
1. **New API Endpoints**: Follow Flask patterns in app.py with proper error handling
2. **AI API Integration**: Replace placeholder responses with actual API calls in designated sections
3. **Database Integration**: Consider SQLAlchemy if data persistence is needed
4. **Authentication**: Add user sessions if required for multi-user support

### Adding New Features
1. **New Subject Tabs**: Update tab system in script.js and add corresponding theme colors
2. **New Particle Types**: Extend particle system with new symbols and animations
3. **New UI Components**: Follow glass-morphism pattern with consistent spacing and blur effects
4. **New Animations**: Use CSS keyframes prefixed with descriptive names (e.g., `float`, `glow`, `pulse`)
5. **New API Endpoints**: Create corresponding Flask routes and frontend JavaScript functions

### Frontend-Backend Communication
- **Fetch API**: All backend communication uses async/await with fetch()
- **Form Data**: Image uploads use FormData for multipart content
- **JSON Responses**: Standardized response format with status and data fields
- **Loading States**: UI feedback during API calls with loading animations
- **Error Display**: User-friendly error messages with retry options

## Visual Design System

### Color Schemes
- Background: Dark gradients with space theme
- Cards: Semi-transparent with backdrop blur
- Text: High contrast with neon glow effects
- Interactive Elements: Hover states with transform and color transitions

### Animation Principles
- Subtle micro-interactions on all interactive elements
- Loading states with pulsing or glowing effects
- Smooth transitions between theme switches
- Performance-optimized using CSS transforms and opacity