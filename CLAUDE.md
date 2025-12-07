# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

名侦探作业帮 (Detective Study Helper) is an AI-powered educational web application for solving physics and chemistry problems.

- **Dual API Support**: Text queries via DeepSeek API (deepseek-reasoner), image recognition via Doubao API (doubao-seed-1-6-251015)
- **Flask Backend**: RESTful API with Server-Sent Events for streaming responses
- **Vanilla Frontend**: Pure HTML5, CSS3, JavaScript with Detective Conan theme
- **Chinese Language**: Fully localized interface and responses

## Development Commands

```bash
# Install dependencies
python scripts/install_all.py
# Or: pip install -r src/requirements.txt

# Configure environment
cp config/.env.example src/.env  # Edit with your API keys

# Run application
python start.py  # Or: 启动项目.bat on Windows

# Run tests
python tests/api/test_deepseek_simple.py
python tests/api/test_chinese.py

# Project management
python .claude/scripts/validate.py   # Validate structure
python .claude/scripts/cleanup.py    # Clean temp files
```

## Architecture

### Request Flow
1. Frontend submits question via `/api/query/text` (text) or `/api/query/image` (with image)
2. Backend creates session (JSON in `data/sessions/`), returns session ID
3. Frontend connects to `/api/stream/<session_id>` for SSE streaming
4. Backend streams response from DeepSeek (text) or returns Doubao result (image)

### Backend (`src/`)
- `app.py` - Flask routes, SSE streaming, session management
- `doubao_api.py` - DoubaoClient class for image+text queries (uses OpenAI SDK)
- `prompts.py` - Subject-specific system prompts (physics/chemistry)

### Frontend (`frontend/`)
- `templates/index.html` - Main Jinja2 template
- `static/css/` - Theming with CSS variables (blue=physics, red=chemistry)
- `static/js/` - EventSource for SSE, drag-drop file upload

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/query/text` | POST | Text query → returns session_id for streaming |
| `/api/query/image` | POST | Image upload → processes via Doubao, returns result |
| `/api/query/base64` | POST | Base64 image → same as image endpoint |
| `/api/stream/<session_id>` | GET | SSE stream for DeepSeek response |
| `/result/<session_id>` | GET | Result page with streaming display |

### Environment Variables (`src/.env`)
```
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner
DOUBAO_API_KEY=your_key
SECRET_KEY=flask_secret
```

## Key Implementation Details

### DeepSeek Streaming
The DeepSeek API returns two content types in streaming mode:
- `delta.reasoning_content` - AI's thinking process (sent as `type: 'thinking'`)
- `delta.content` - Final answer (sent as `type: 'answer'`)

Enable thinking mode: `extra_body={"thinking": {"type": "enabled"}}`

### Doubao Image Processing
- Images resized to max 1024x1024 before encoding
- Converted to JPEG at 85% quality
- Uses `detail: "low"` for faster processing
- Fallback to lower settings if API call fails

### Session Storage
Sessions stored as JSON files: `data/sessions/{YYYYMMDDHHMMSS}{microseconds}.json`
Contains: question, subject, timestamp, and response data after completion.

## File Organization Rules

- **Temporary tests**: `.claude/tests/temporary/` (auto-cleanup after 24h)
- **Test naming**: `test_<feature>_<timestamp>.py`
- **Uploads**: `data/uploads/` (16MB max, allowed: png, jpg, jpeg, gif, webp)
- **Logs**: `data/logs/`

## Production

Use `src/run_production.py` with Waitress (Windows) or Gunicorn (Linux) instead of Flask dev server.
