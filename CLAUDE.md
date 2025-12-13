# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

名侦探作业帮 (Detective Study Helper) is an AI-powered educational web application for solving physics and chemistry problems, with diary journaling and goal tracking features.

- **Dual API Support**: Text queries via DeepSeek API (deepseek-reasoner), image recognition via Doubao API (doubao-seed-1-6-251015)
- **Flask Backend**: RESTful API with Server-Sent Events for streaming responses
- **MySQL Database**: User authentication, diaries, and goals with Zeabur-hosted MySQL
- **Vanilla Frontend**: Pure HTML5, CSS3, JavaScript with Detective Conan theme
- **Bilingual i18n**: Supports `zh-CN` and `en-US` via cookie-based language switching

## Development Commands

```bash
# Install dependencies
python scripts/install_all.py
# Or: pip install -r src/requirements.txt

# Configure environment
cp config/.env.example src/.env  # Edit with your API keys

# Run application (from project root)
python start.py
# Or on Windows: scripts\启动项目.bat

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
4. Backend streams response from DeepSeek (text) or Doubao (image)

### Deep Think Mode (Cross-Validation)
When `deep_think=true`:
- **Text queries**: DeepSeek solves → Doubao verifies
- **Image queries**: Doubao solves → DeepSeek verifies
- SSE events include `stage` (solving/verifying), `verify_thinking`, `verify_answer`

### Backend (`src/`)
- `app.py` - Flask routes, SSE streaming, session management, auth/diary/goal endpoints
- `database.py` - MySQL connection, user CRUD, diary CRUD (with AI responses, streak tracking), goal CRUD (with status: active/completed/archived)
- `doubao_api.py` - DoubaoClient class for image+text queries (uses OpenAI SDK compatibility), image compression via Pillow, streaming with reasoning_content support
- `prompts.py` / `prompts_en.py` - Subject-specific system prompts (physics/chemistry/competition/verification) in Chinese and English

### Frontend (`frontend/`)
- `templates/` - Jinja2 templates: `home.html`, `index.html`, `login.html`, `register.html`, `reset_password.html`, `result.html`, `profile.html`, `diary.html`, `diary_list.html`, `diary_detail.html`
- `static/css/` - Theming with CSS variables (blue=physics, red=chemistry)
- `static/js/` - EventSource for SSE, drag-drop file upload
- `static/js/i18n.js` - Language switching logic
- `static/js/translations/` - Translation files (`zh-CN.js`, `en-US.js`)

### API Endpoints

**Query endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/query/text` | POST | Text query → returns session_id for streaming |
| `/api/query/image` | POST | Image upload → returns session_id for streaming |
| `/api/query/base64` | POST | Base64 image → same as image endpoint |
| `/api/stream/<session_id>` | GET | SSE stream for response |

**Auth endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Register user (name, email/phone, password) |
| `/api/auth/login` | POST | Login (account, password) → sets session |
| `/api/auth/logout` | POST | Clear session |
| `/api/auth/check-account` | POST | Check if email/phone exists |
| `/api/auth/reset-password` | POST | Reset password |
| `/api/auth/user` | GET | Get current logged-in user |

**Diary endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/diaries` | GET | List user diaries (with pagination) |
| `/api/diary` | POST | Create diary entry |
| `/api/diary/<id>` | GET | Get single diary |
| `/api/diary/<id>` | DELETE | Delete diary |
| `/api/diary/generate-ai` | POST | Generate AI response for diary (SSE) |
| `/api/diary/status/today` | GET | Check if user wrote diary today |
| `/api/diary/streak` | GET | Get consecutive diary streak days |

**Goal endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/goals` | GET | List user goals (filter by status) |
| `/api/goals` | POST | Create new goal |
| `/api/goal/<id>` | GET | Get single goal |
| `/api/goal/<id>` | PUT | Update goal (title, description, status) |
| `/api/goal/<id>` | DELETE | Delete goal |

### Environment Variables (`src/.env`)
```
# AI APIs
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner
DOUBAO_API_KEY=your_key

# MySQL (Zeabur)
MYSQL_HOST=sjc1.clusters.zeabur.com
MYSQL_PORT=29007
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=zeabur

# Flask
SECRET_KEY=flask_secret
FLASK_DEBUG=false
PORT=5000
```

## Key Implementation Details

### DeepSeek Streaming
The DeepSeek API returns two content types in streaming mode:
- `delta.reasoning_content` - AI's thinking process (sent as `type: 'thinking'`)
- `delta.content` - Final answer (sent as `type: 'answer'`)

Enable thinking mode: `extra_body={"thinking": {"type": "enabled"}}`

### Doubao Deep Thinking
Uses model `doubao-seed-1-6-251015` with streaming:
- `delta.reasoning_content` - Thinking process (same as DeepSeek)
- `delta.content` - Final answer
- Timeout set to 1800s for complex reasoning

### Image Processing
- Images resized to max 1024x1024 before encoding
- Converted to JPEG at 85% quality
- Uses `detail: "low"` for faster processing
- Fallback to lower settings if API call fails

### Session Storage
Sessions stored as JSON files: `data/sessions/{YYYYMMDDHHMMSS}{microseconds}.json`
Response saved separately: `data/sessions/{session_id}_response.json`

### User Authentication
- Passwords hashed with SHA-256
- Login via email or phone number
- Flask session stores user_id, user_name, scores

### Diary AI Responses
- Uses Doubao API for generating AI responses to diary entries
- Can analyze recent diaries with `history_range` parameter (e.g., "week", "month")
- Supports goal progress analysis via `goal_analysis` field
- Tracks consecutive diary writing streaks

### i18n Language Support
- Language stored in browser cookie (`lang`)
- Supported values: `zh-CN` (default), `en-US`
- `get_current_language()` reads cookie in requests
- Prompts selected via `get_subject_prompt_by_lang()` etc.

## File Organization Rules

- **Temporary tests**: `.claude/tests/temporary/` (auto-cleanup after 24h)
- **Test naming**: `test_<feature>_<timestamp>.py`
- **Uploads**: `data/uploads/` (16MB max, allowed: png, jpg, jpeg, gif, webp)
- **Sessions**: `data/sessions/` (JSON files with format `{YYYYMMDDHHMMSS}{microseconds}.json`)
- **Logs**: `data/logs/`

## Production

Use `src/run_production.py` with Waitress (Windows) or Gunicorn (Linux) instead of Flask dev server.

Docker deployment configured via `Dockerfile` and `zeabur.json` for Zeabur platform.

## Dependencies

Key Python packages (see `src/requirements.txt`):
- `Flask`, `Flask-CORS` - Web framework
- `openai>=1.40.0` - API client for DeepSeek and Doubao (OpenAI-compatible)
- `Pillow>=10.0.0` - Image processing and compression
- `mysql-connector-python>=8.0.0` - Database driver
- `waitress>=2.1.2` - Production WSGI server (Windows)
- `volcengine-python-sdk[ark]` - Volcengine SDK for Doubao
