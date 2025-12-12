# Diary Feature Implementation Plan

## Project Overview

**Existing Assets**: A fully functional AI Q&A website with user system, frontend framework, backend API, and database.

**New Module**: "My Growth Diary" - A personal growth tool combining diary recording, AI emotional feedback, and intelligent plan generation.

**Core Relationship**: New module shares user system with main site, but data is isolated.

---

## Technology Stack Alignment

| Component | Existing | Diary Feature |
|-----------|----------|---------------|
| Backend | Flask + Python | Same |
| Frontend | Vanilla JS + Jinja2 | Same (NOT React/Vue) |
| Database | MySQL (Zeabur) | Same |
| AI | DeepSeek + Doubao | Reuse Doubao for emotional responses |
| Auth | Flask session | Shared |
| i18n | zh-CN / en-US | Extend translations |

---

## Database Schema Design

### Table: `diaries`

```sql
CREATE TABLE diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    ai_response TEXT,
    mood_score INT DEFAULT NULL,           -- 1-5 scale (Phase 2)
    sleep_hours FLOAT DEFAULT NULL,        -- Hours slept (Phase 2)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Table: `plans` (Phase 2)

```sql
CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    week_start DATE NOT NULL,              -- Monday of the week
    plan_content JSON NOT NULL,            -- Structured plan data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_week (user_id, week_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Table: `plan_tasks` (Phase 3 - Optional Normalization)

```sql
CREATE TABLE plan_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    category ENUM('academic', 'life', 'exercise') NOT NULL,
    description VARCHAR(500) NOT NULL,
    deadline DATE,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
    INDEX idx_plan_category (plan_id, category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## API Endpoints Design

### Phase 1 - Core APIs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/diary` | Create new diary entry | Yes |
| GET | `/api/diary` | List user's diaries (paginated) | Yes |
| GET | `/api/diary/<id>` | Get single diary detail | Yes |
| PUT | `/api/diary/<id>` | Update diary entry | Yes |
| DELETE | `/api/diary/<id>` | Delete diary entry | Yes |
| GET | `/api/diary/today` | Check if today's diary exists | Yes |

### Phase 2 - Plan APIs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/plan/generate` | Generate weekly plan from diary data | Yes |
| GET | `/api/plan/current` | Get current week's plan | Yes |
| GET | `/api/plan/history` | List past plans | Yes |

### Phase 3 - Enhancement APIs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/api/plan/task/<id>` | Toggle task completion | Yes |
| GET | `/api/diary/stats` | Get mood/sleep statistics (30 days) | Yes |

---

## File Structure

### New Files to Create

```
new_agent/
├── frontend/
│   ├── templates/
│   │   ├── diary.html              # Main diary page (write + view)
│   │   ├── diary_list.html         # Diary history list
│   │   └── plan.html               # Weekly plan page (Phase 2)
│   └── static/
│       ├── js/
│       │   └── diary.js            # Diary frontend logic
│       └── css/
│           └── diary.css           # Diary-specific styles (optional)
├── src/
│   ├── diary_prompts.py            # Diary AI prompts (CN + EN)
│   └── diary_routes.py             # Diary API routes (optional, can be in app.py)
```

### Files to Modify

```
├── src/
│   ├── app.py                      # Add diary routes
│   └── database.py                 # Add diary CRUD functions
├── frontend/
│   ├── templates/
│   │   ├── home.html               # Add "My Diary" nav link
│   │   └── index.html              # Add "My Diary" nav link
│   └── static/js/
│       └── translations/
│           ├── zh-CN.js            # Add diary translations
│           └── en-US.js            # Add diary translations
```

---

## Phase 1: MVP Implementation

### Goal
User can: Write diary → Get AI response → View history

### 1.1 Database Setup

Add to `database.py`:

```python
def create_diary(user_id, content):
    """Create a new diary entry"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO diaries (user_id, content)
            VALUES (%s, %s)
        """, (user_id, content))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def update_diary_ai_response(diary_id, ai_response):
    """Update diary with AI response"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE diaries SET ai_response = %s WHERE id = %s
        """, (ai_response, diary_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_user_diaries(user_id, limit=20, offset=0):
    """Get user's diary list"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, content, ai_response, mood_score, sleep_hours, created_at
            FROM diaries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_diary_by_id(diary_id, user_id):
    """Get single diary (with ownership check)"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM diaries
            WHERE id = %s AND user_id = %s
        """, (diary_id, user_id))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_today_diary(user_id):
    """Check if user has written today's diary"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, content, ai_response, created_at
            FROM diaries
            WHERE user_id = %s AND DATE(created_at) = CURDATE()
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def delete_diary(diary_id, user_id):
    """Delete diary (with ownership check)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM diaries
            WHERE id = %s AND user_id = %s
        """, (diary_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
```

### 1.2 AI Prompts

Create `src/diary_prompts.py`:

```python
# Chinese Diary Prompt
DIARY_RESPONSE_PROMPT_ZH = """你是一个温暖、有同理心的AI伙伴，名叫"小柯"（灵感来自柯南）。
用户刚刚写下了今天的日记，请阅读后给出回应。

要求：
1. 回应要简短（100-150字）
2. 表达理解和共鸣
3. 给予适当的鼓励或建议
4. 语气温暖、真诚，像朋友一样
5. 如果用户情绪低落，要给予安慰
6. 如果用户分享了成就，要真诚祝贺

用户的日记内容：
{diary_content}

请直接给出回应，不要有任何前缀或解释。"""

# English Diary Prompt
DIARY_RESPONSE_PROMPT_EN = """You are a warm, empathetic AI companion named "Conan Jr."
The user just wrote today's diary entry. Please read and respond.

Requirements:
1. Keep response brief (100-150 words)
2. Show understanding and empathy
3. Provide appropriate encouragement or suggestions
4. Use a warm, sincere tone, like a friend
5. If the user seems down, offer comfort
6. If the user shares achievements, congratulate sincerely

User's diary content:
{diary_content}

Please respond directly without any prefix or explanation."""

def get_diary_prompt(lang='zh-CN'):
    """Get diary prompt based on language"""
    if lang == 'en-US':
        return DIARY_RESPONSE_PROMPT_EN
    return DIARY_RESPONSE_PROMPT_ZH
```

### 1.3 Backend Routes

Add to `app.py`:

```python
from diary_prompts import get_diary_prompt
from database import (
    create_diary, update_diary_ai_response,
    get_user_diaries, get_diary_by_id,
    get_today_diary, delete_diary
)

# ========== Diary Routes ==========

@app.route('/diary')
def diary_page():
    """Diary main page"""
    if 'user_id' not in session:
        return redirect('/login?redirect=/diary')
    return render_template('diary.html')

@app.route('/diary/list')
def diary_list_page():
    """Diary history page"""
    if 'user_id' not in session:
        return redirect('/login?redirect=/diary/list')
    return render_template('diary_list.html')

@app.route('/api/diary', methods=['POST'])
def create_diary_entry():
    """Create new diary and get AI response"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'message': 'Diary content cannot be empty'}), 400

    if len(content) > 5000:
        return jsonify({'success': False, 'message': 'Content too long (max 5000 characters)'}), 400

    user_id = session['user_id']
    lang = get_current_language()

    # Create diary entry
    diary_id = create_diary(user_id, content)

    # Generate AI response
    try:
        prompt = get_diary_prompt(lang).format(diary_content=content)

        # Use Doubao for emotional response (good at Chinese)
        from doubao_api import DoubaoClient
        client = DoubaoClient()

        ai_response = ""
        for chunk in client.chat_stream(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a warm and empathetic AI companion."
        ):
            if chunk.get('content'):
                ai_response += chunk['content']

        # Save AI response
        update_diary_ai_response(diary_id, ai_response)

        return jsonify({
            'success': True,
            'diary_id': diary_id,
            'ai_response': ai_response
        })
    except Exception as e:
        print(f"AI response error: {e}")
        return jsonify({
            'success': True,
            'diary_id': diary_id,
            'ai_response': None,
            'message': 'Diary saved, but AI response failed'
        })

@app.route('/api/diary', methods=['GET'])
def list_diaries():
    """Get user's diary list"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit

    diaries = get_user_diaries(session['user_id'], limit, offset)

    # Convert datetime to string
    for diary in diaries:
        diary['created_at'] = diary['created_at'].isoformat()

    return jsonify({
        'success': True,
        'diaries': diaries,
        'page': page,
        'limit': limit
    })

@app.route('/api/diary/<int:diary_id>', methods=['GET'])
def get_diary(diary_id):
    """Get single diary detail"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    diary = get_diary_by_id(diary_id, session['user_id'])

    if not diary:
        return jsonify({'success': False, 'message': 'Diary not found'}), 404

    diary['created_at'] = diary['created_at'].isoformat()
    if diary.get('updated_at'):
        diary['updated_at'] = diary['updated_at'].isoformat()

    return jsonify({'success': True, 'diary': diary})

@app.route('/api/diary/<int:diary_id>', methods=['DELETE'])
def delete_diary_entry(diary_id):
    """Delete diary"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    success = delete_diary(diary_id, session['user_id'])

    if success:
        return jsonify({'success': True, 'message': 'Diary deleted'})
    else:
        return jsonify({'success': False, 'message': 'Diary not found'}), 404

@app.route('/api/diary/today', methods=['GET'])
def check_today_diary():
    """Check if user has written today's diary"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    diary = get_today_diary(session['user_id'])

    return jsonify({
        'success': True,
        'has_diary': diary is not None,
        'diary': diary
    })
```

### 1.4 Frontend Template

Create `frontend/templates/diary.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="diary.pageTitle">My Growth Diary | Detective Study Helper</title>

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        teitanBlue: '#0047AB',
                        conanRed: '#E31D2B',
                        mysteryBlack: '#1a1a2e',
                        moonlightBlue: '#16213e',
                        neonCyan: '#00d4ff',
                        detectiveGold: '#ffd700',
                    }
                }
            }
        }
    </script>
    <style>
        /* Diary-specific styles */
        .diary-card {
            background: rgba(22, 33, 62, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        .diary-textarea {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            resize: none;
        }
        .diary-textarea:focus {
            border-color: #ffd700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
            outline: none;
        }
        .ai-response-card {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(0, 212, 255, 0.1));
            border: 1px solid rgba(255, 215, 0, 0.3);
        }
    </style>
</head>
<body class="min-h-screen font-sans text-white">
    <!-- Background -->
    <div class="stars" id="stars"></div>
    <div class="moon"></div>
    <div class="vignette"></div>

    <!-- Navigation -->
    <nav class="nav-gradient shadow-2xl sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <a href="/" class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-neonCyan to-teitanBlue flex items-center justify-center">
                        <i class="fa-solid fa-book text-lg"></i>
                    </div>
                    <div>
                        <h1 class="font-bold text-xl" data-i18n="diary.title">My Growth Diary</h1>
                        <p class="text-xs text-white/50" data-i18n="diary.subtitle">Record your journey</p>
                    </div>
                </a>
                <div class="flex items-center gap-4">
                    <!-- Language Switcher -->
                    <div class="lang-switcher flex items-center gap-1 text-sm">
                        <button data-lang="zh-CN" class="lang-btn px-2 py-1 rounded hover:text-neonCyan">中文</button>
                        <span class="text-white/30">|</span>
                        <button data-lang="en-US" class="lang-btn px-2 py-1 rounded hover:text-neonCyan">EN</button>
                    </div>
                    <a href="/diary/list" class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all">
                        <i class="fa-solid fa-clock-rotate-left mr-2"></i>
                        <span data-i18n="diary.history">History</span>
                    </a>
                    <a href="/app" class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all">
                        <i class="fa-solid fa-arrow-left mr-2"></i>
                        <span data-i18n="diary.backToQA">Back to Q&A</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8 relative z-10">
        <div class="max-w-3xl mx-auto">
            <!-- Date Display -->
            <div class="text-center mb-8">
                <p class="text-detectiveGold text-lg" id="currentDate"></p>
                <h2 class="text-3xl font-bold mt-2" data-i18n="diary.prompt">How was your day?</h2>
            </div>

            <!-- Diary Input Card -->
            <div class="diary-card rounded-2xl p-6 mb-6">
                <textarea
                    id="diaryContent"
                    class="diary-textarea w-full h-64 px-4 py-3 rounded-xl text-white placeholder-white/30"
                    data-i18n-placeholder="diary.placeholder"
                    placeholder="Write about your day... What happened? How do you feel?"
                ></textarea>

                <div class="flex justify-between items-center mt-4">
                    <span class="text-white/50 text-sm">
                        <span id="charCount">0</span> / 5000
                    </span>
                    <button
                        id="saveBtn"
                        class="px-6 py-3 bg-gradient-to-r from-detectiveGold to-neonCyan rounded-xl font-bold hover:scale-105 transition-all"
                    >
                        <i class="fa-solid fa-paper-plane mr-2"></i>
                        <span data-i18n="diary.save">Save & Get Response</span>
                    </button>
                </div>
            </div>

            <!-- AI Response Card (initially hidden) -->
            <div id="aiResponseCard" class="ai-response-card rounded-2xl p-6 hidden">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-detectiveGold to-conanRed flex items-center justify-center">
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <div>
                        <h3 class="font-bold" data-i18n="diary.aiTitle">Conan Jr. says:</h3>
                        <p class="text-xs text-white/50" data-i18n="diary.aiSubtitle">Your AI companion</p>
                    </div>
                </div>
                <div id="aiResponse" class="text-white/90 leading-relaxed"></div>
            </div>

            <!-- Loading State -->
            <div id="loadingState" class="text-center py-8 hidden">
                <div class="w-16 h-16 border-4 border-detectiveGold/20 border-t-detectiveGold rounded-full animate-spin mx-auto mb-4"></div>
                <p class="text-white/70" data-i18n="diary.thinking">AI is reading your diary...</p>
            </div>
        </div>
    </main>

    <!-- Scripts -->
    <script src="{{ url_for('static', filename='js/translations/zh-CN.js') }}"></script>
    <script src="{{ url_for('static', filename='js/translations/en-US.js') }}"></script>
    <script src="{{ url_for('static', filename='js/i18n.js') }}"></script>
    <script>
        // Generate stars background
        function createStars() {
            const container = document.getElementById('stars');
            if (!container) return;
            for (let i = 0; i < 100; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.animationDelay = Math.random() * 3 + 's';
                container.appendChild(star);
            }
        }
        createStars();

        // Display current date
        function displayDate() {
            const now = new Date();
            const options = {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            };
            const lang = window.i18n ? i18n.getCurrentLang() : 'zh-CN';
            document.getElementById('currentDate').textContent = now.toLocaleDateString(lang, options);
        }
        displayDate();

        // Character count
        const textarea = document.getElementById('diaryContent');
        const charCount = document.getElementById('charCount');
        textarea.addEventListener('input', () => {
            charCount.textContent = textarea.value.length;
        });

        // Save diary
        document.getElementById('saveBtn').addEventListener('click', async () => {
            const content = textarea.value.trim();
            if (!content) {
                alert(window.i18n ? i18n.t('diary.errors.empty') : 'Please write something first!');
                return;
            }

            const saveBtn = document.getElementById('saveBtn');
            const loadingState = document.getElementById('loadingState');
            const aiResponseCard = document.getElementById('aiResponseCard');

            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>' +
                (window.i18n ? i18n.t('diary.saving') : 'Saving...');
            loadingState.classList.remove('hidden');
            aiResponseCard.classList.add('hidden');

            try {
                const response = await fetch('/api/diary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content })
                });
                const data = await response.json();

                if (data.success) {
                    loadingState.classList.add('hidden');

                    if (data.ai_response) {
                        document.getElementById('aiResponse').textContent = data.ai_response;
                        aiResponseCard.classList.remove('hidden');
                    }

                    // Clear textarea for next entry
                    textarea.value = '';
                    charCount.textContent = '0';

                    saveBtn.innerHTML = '<i class="fa-solid fa-check mr-2"></i>' +
                        (window.i18n ? i18n.t('diary.saved') : 'Saved!');

                    setTimeout(() => {
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '<i class="fa-solid fa-paper-plane mr-2"></i>' +
                            (window.i18n ? i18n.t('diary.save') : 'Save & Get Response');
                    }, 2000);
                } else {
                    throw new Error(data.message);
                }
            } catch (err) {
                loadingState.classList.add('hidden');
                alert(err.message || (window.i18n ? i18n.t('diary.errors.saveFailed') : 'Failed to save diary'));
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="fa-solid fa-paper-plane mr-2"></i>' +
                    (window.i18n ? i18n.t('diary.save') : 'Save & Get Response');
            }
        });
    </script>
</body>
</html>
```

### 1.5 Translation Keys

Add to `zh-CN.js`:

```javascript
// Add to translations_zh object
diary: {
    pageTitle: "我的成长日记 | 名侦探作业帮",
    title: "我的成长日记",
    subtitle: "记录你的成长轨迹",
    history: "历史记录",
    backToQA: "返回问答",
    prompt: "今天过得怎么样？",
    placeholder: "写下你的一天... 发生了什么？心情如何？",
    save: "保存并获取回复",
    saving: "保存中...",
    saved: "已保存！",
    thinking: "AI正在阅读你的日记...",
    aiTitle: "小柯说：",
    aiSubtitle: "你的AI伙伴",
    errors: {
        empty: "请先写点什么！",
        saveFailed: "保存失败，请重试"
    }
}
```

Add to `en-US.js`:

```javascript
// Add to translations_en object
diary: {
    pageTitle: "My Growth Diary | Detective Study Helper",
    title: "My Growth Diary",
    subtitle: "Record your journey",
    history: "History",
    backToQA: "Back to Q&A",
    prompt: "How was your day?",
    placeholder: "Write about your day... What happened? How do you feel?",
    save: "Save & Get Response",
    saving: "Saving...",
    saved: "Saved!",
    thinking: "AI is reading your diary...",
    aiTitle: "Conan Jr. says:",
    aiSubtitle: "Your AI companion",
    errors: {
        empty: "Please write something first!",
        saveFailed: "Failed to save diary"
    }
}
```

---

## Phase 2: Smart Features

### 2.1 Calendar Integration

Use FullCalendar (vanilla JS version):

```html
<!-- Add to diary.html head -->
<link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>
```

### 2.2 Mood & Sleep Inputs

Add to diary form:

```html
<div class="grid grid-cols-2 gap-4 mt-4">
    <div>
        <label class="text-sm text-white/70 mb-2 block">
            <i class="fa-solid fa-face-smile mr-2"></i>Today's Mood
        </label>
        <input type="range" id="moodScore" min="1" max="5" value="3" class="w-full">
        <div class="flex justify-between text-xs text-white/50 mt-1">
            <span>😢</span><span>😐</span><span>😊</span><span>😄</span><span>🥳</span>
        </div>
    </div>
    <div>
        <label class="text-sm text-white/70 mb-2 block">
            <i class="fa-solid fa-bed mr-2"></i>Sleep Hours
        </label>
        <input type="number" id="sleepHours" min="0" max="24" step="0.5"
            class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
            placeholder="e.g. 7.5">
    </div>
</div>
```

### 2.3 Plan Generation Prompt

```python
PLAN_GENERATION_PROMPT = """You are a professional high school growth planner.
Based on the user's diary data from the past 7 days, generate a SMART weekly plan.

User's 7-day summary:
- Average mood: {avg_mood}/5
- Average sleep: {avg_sleep} hours
- Key themes from diaries: {themes}

Generate a plan with 3 dimensions: academic, life, exercise.
Each dimension should have 2-3 specific, actionable tasks.

IMPORTANT: Return ONLY valid JSON in this exact format:
```json
{
  "academic": [
    {"task": "...", "deadline": "Monday", "priority": "high"},
    {"task": "...", "deadline": "Wednesday", "priority": "medium"}
  ],
  "life": [
    {"task": "...", "deadline": "Daily", "priority": "medium"}
  ],
  "exercise": [
    {"task": "...", "deadline": "Tuesday/Thursday", "priority": "medium"}
  ],
  "summary": "Brief encouraging message about the week ahead"
}
```"""
```

---

## Phase 3: Engagement Features

### 3.1 Homepage Reminder

Add to `home.html`:

```html
<!-- Diary Reminder (show if not written today) -->
<div id="diaryReminder" class="fixed bottom-4 right-4 bg-detectiveGold/90 text-mysteryBlack px-4 py-3 rounded-xl shadow-lg hidden z-50">
    <p class="font-bold"><i class="fa-solid fa-pen mr-2"></i>Did you record your growth today?</p>
    <div class="flex gap-2 mt-2">
        <a href="/diary" class="px-3 py-1 bg-mysteryBlack text-white rounded-lg text-sm">Write Now</a>
        <button onclick="dismissReminder()" class="px-3 py-1 bg-white/30 rounded-lg text-sm">Later</button>
    </div>
</div>

<script>
async function checkDiaryReminder() {
    try {
        const res = await fetch('/api/diary/today');
        const data = await res.json();
        if (data.success && !data.has_diary) {
            document.getElementById('diaryReminder').classList.remove('hidden');
        }
    } catch (e) {}
}
// Check after page load
setTimeout(checkDiaryReminder, 2000);
</script>
```

### 3.2 Data Visualization

Use Chart.js:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<canvas id="moodChart"></canvas>

<script>
async function loadStats() {
    const res = await fetch('/api/diary/stats');
    const data = await res.json();

    new Chart(document.getElementById('moodChart'), {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Mood',
                data: data.moods,
                borderColor: '#ffd700',
                tension: 0.3
            }, {
                label: 'Sleep (hrs)',
                data: data.sleep,
                borderColor: '#00d4ff',
                tension: 0.3
            }]
        }
    });
}
</script>
```

---

## Challenges & Solutions

| Challenge | Difficulty | Solution |
|-----------|------------|----------|
| Calendar without React | Medium | Use FullCalendar vanilla JS CDN |
| AI JSON reliability | Medium-Hard | Strict prompt + validation + retry (3 attempts) |
| Data visualization | Medium | Chart.js works with vanilla JS |
| Database migrations | Low | Design full schema upfront (include Phase 2 fields) |
| i18n for new pages | Low | Extend existing translation files |

---

## Development Checklist

### Phase 1 (MVP)
- [ ] Create `diaries` table in MySQL
- [ ] Add database functions to `database.py`
- [ ] Create `diary_prompts.py`
- [ ] Add diary routes to `app.py`
- [ ] Create `diary.html` template
- [ ] Create `diary_list.html` template
- [ ] Add navigation links to `home.html` and `index.html`
- [ ] Add diary translations to `zh-CN.js` and `en-US.js`
- [ ] Test full flow: write → AI response → view history

### Phase 2 (Smart Features)
- [ ] Integrate FullCalendar
- [ ] Add mood/sleep inputs
- [ ] Create `plans` table
- [ ] Implement plan generation API
- [ ] Create `plan.html` template
- [ ] Add plan translations

### Phase 3 (Engagement)
- [ ] Add homepage diary reminder
- [ ] Implement task completion toggle
- [ ] Add Chart.js visualization
- [ ] Create stats API endpoint

---

## Timeline Estimate

| Phase | Tasks | Complexity |
|-------|-------|------------|
| Phase 1 | Database + API + UI | Straightforward |
| Phase 2 | Calendar + Plans | Medium complexity |
| Phase 3 | Polish + Visualization | Medium complexity |

---

## Notes

1. **Reuse Existing Patterns**: Follow the same code style as `app.py` for routes, `database.py` for DB operations
2. **Test Incrementally**: Complete and test each phase before moving to next
3. **AI Prompt Iteration**: Spend time refining prompts for better emotional responses
4. **Mobile Responsive**: Ensure diary pages work well on mobile devices
