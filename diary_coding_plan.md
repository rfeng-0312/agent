# 成长日记功能 - 详细技术实现计划

## 概述

本文档基于 `diary_function_plan.md` 中的功能规划，结合现有网站架构，制定详细的技术实现方案。

**重要原则**：
- 复用现有代码模式（SSE流式响应、i18n结构、Tailwind样式）
- 保持与主站风格一致（柯南主题、深蓝+金色配色）
- 每个步骤都要有明确的输入输出

---

## 现有技术架构分析

### 后端 (Flask)
| 文件 | 作用 | 关键模式 |
|------|------|----------|
| `src/app.py` | 主路由文件 | 路由装饰器、session验证、SSE流式响应 |
| `src/database.py` | 数据库操作 | get_db_connection()、try-except-finally模式 |
| `src/doubao_api.py` | 豆包API | DoubaoClient类、stream_with_reasoning() |
| `src/prompts.py` | Prompt模板 | 中英文双版本、get_xxx_by_lang()函数 |

### 前端
| 文件 | 作用 | 关键模式 |
|------|------|----------|
| `frontend/templates/home.html` | 首页 | Tailwind + AOS动画 + i18n |
| `frontend/templates/index.html` | 问答页 | 表单提交 + 文件上传 |
| `frontend/templates/result.html` | 结果页 | SSE EventSource接收流式响应 |
| `frontend/static/js/script.js` | 主脚本 | SSE处理、表单验证 |
| `frontend/static/js/i18n.js` | 国际化 | i18n.t()翻译函数 |

### 现有可复用代码
1. **home.html:469-475** - `goToDiary()` 函数已存在，只需修改跳转地址
2. **home.html:219-237** - 日记卡片UI已存在，标记为"即将上线"
3. **result.html** - SSE流式响应处理逻辑可复用

---

## 第一阶段：MVP核心功能

### Step 1: 数据库层 (`src/database.py`)

#### 1.1 在 `init_database()` 函数中添加 diaries 表

**插入位置**: `init_database()` 函数内，users表创建语句之后

```python
# 创建日记表 (在 users 表创建之后添加)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS diaries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        content TEXT NOT NULL,
        ai_response TEXT DEFAULT NULL,
        mood_score INT DEFAULT NULL COMMENT '心情评分 1-5',
        sleep_hours FLOAT DEFAULT NULL COMMENT '睡眠时长',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
''')
```

#### 1.2 新增日记CRUD函数

**插入位置**: 文件末尾，`get_user_by_id()` 函数之后

**函数1: create_diary()**
```python
def create_diary(user_id, content, mood_score=None, sleep_hours=None):
    """
    创建新日记（不含AI回复，AI回复后续异步更新）

    Args:
        user_id (int): 用户ID
        content (str): 日记内容
        mood_score (int, optional): 心情评分 1-5
        sleep_hours (float, optional): 睡眠时长

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'diary_id': int or None,
            'created_at': str (ISO格式) or None
        }
    """
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败', 'diary_id': None, 'created_at': None}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO diaries (user_id, content, mood_score, sleep_hours)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, content, mood_score, sleep_hours))

        connection.commit()
        diary_id = cursor.lastrowid

        # 获取创建时间
        cursor.execute('SELECT created_at FROM diaries WHERE id = %s', (diary_id,))
        result = cursor.fetchone()
        created_at = result[0].isoformat() if result else None

        return {
            'success': True,
            'message': '日记保存成功',
            'diary_id': diary_id,
            'created_at': created_at
        }
    except Error as e:
        logger.error(f"Create diary error: {e}")
        return {'success': False, 'message': f'保存失败: {str(e)}', 'diary_id': None, 'created_at': None}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数2: update_diary_ai_response()**
```python
def update_diary_ai_response(diary_id, ai_response):
    """
    更新日记的AI回复

    Args:
        diary_id (int): 日记ID
        ai_response (str): AI回复内容

    Returns:
        dict: {'success': bool, 'message': str}
    """
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE diaries SET ai_response = %s WHERE id = %s
        ''', (ai_response, diary_id))

        connection.commit()
        return {'success': True, 'message': 'AI回复已更新'}
    except Error as e:
        logger.error(f"Update diary AI response error: {e}")
        return {'success': False, 'message': f'更新失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数3: get_diary_by_id()**
```python
def get_diary_by_id(diary_id, user_id):
    """
    根据ID获取日记详情（验证所有权）

    Args:
        diary_id (int): 日记ID
        user_id (int): 用户ID（验证所有权）

    Returns:
        dict or None: {
            'id': int,
            'content': str,
            'ai_response': str or None,
            'mood_score': int or None,
            'sleep_hours': float or None,
            'created_at': str (ISO格式),
            'updated_at': str (ISO格式)
        }
    """
    connection = get_db_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, content, ai_response, mood_score, sleep_hours, created_at, updated_at
            FROM diaries WHERE id = %s AND user_id = %s
        ''', (diary_id, user_id))

        result = cursor.fetchone()
        if result:
            # 转换datetime为ISO字符串
            result['created_at'] = result['created_at'].isoformat() if result['created_at'] else None
            result['updated_at'] = result['updated_at'].isoformat() if result['updated_at'] else None
        return result
    except Error as e:
        logger.error(f"Get diary error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数4: get_user_diaries()**
```python
def get_user_diaries(user_id, limit=20, offset=0):
    """
    获取用户的日记列表（分页）

    Args:
        user_id (int): 用户ID
        limit (int): 每页数量，默认20
        offset (int): 偏移量，默认0

    Returns:
        list: [{
            'id': int,
            'content': str (截取前100字符),
            'ai_response': str or None (截取前50字符),
            'mood_score': int or None,
            'created_at': str (ISO格式)
        }, ...]
    """
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id,
                   LEFT(content, 100) as content,
                   LEFT(ai_response, 50) as ai_response,
                   mood_score,
                   created_at
            FROM diaries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        ''', (user_id, limit, offset))

        results = cursor.fetchall()
        # 转换datetime
        for r in results:
            r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        return results
    except Error as e:
        logger.error(f"Get user diaries error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数5: get_diary_count()**
```python
def get_diary_count(user_id):
    """获取用户日记总数"""
    connection = get_db_connection()
    if not connection:
        return 0

    try:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM diaries WHERE user_id = %s', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Error as e:
        logger.error(f"Get diary count error: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数6: check_diary_today()**
```python
def check_diary_today(user_id):
    """
    检查用户今天是否已写日记

    Returns:
        dict: {'has_diary': bool, 'diary_id': int or None}
    """
    connection = get_db_connection()
    if not connection:
        return {'has_diary': False, 'diary_id': None}

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT id FROM diaries
            WHERE user_id = %s AND DATE(created_at) = CURDATE()
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))

        result = cursor.fetchone()
        if result:
            return {'has_diary': True, 'diary_id': result['id']}
        return {'has_diary': False, 'diary_id': None}
    except Error as e:
        logger.error(f"Check diary today error: {e}")
        return {'has_diary': False, 'diary_id': None}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数7: get_diary_streak()**
```python
def get_diary_streak(user_id):
    """
    获取用户连续写日记天数

    Returns:
        int: 连续天数
    """
    connection = get_db_connection()
    if not connection:
        return 0

    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT DATE(created_at) as diary_date
            FROM diaries
            WHERE user_id = %s
            ORDER BY diary_date DESC
        ''', (user_id,))

        dates = [row[0] for row in cursor.fetchall()]
        if not dates:
            return 0

        from datetime import date, timedelta
        today = date.today()
        streak = 0

        # 检查今天或昨天是否有日记
        if dates[0] != today and dates[0] != today - timedelta(days=1):
            return 0

        # 计算连续天数
        expected_date = dates[0]
        for diary_date in dates:
            if diary_date == expected_date:
                streak += 1
                expected_date = diary_date - timedelta(days=1)
            else:
                break

        return streak
    except Error as e:
        logger.error(f"Get diary streak error: {e}")
        return 0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

**函数8: delete_diary()**
```python
def delete_diary(diary_id, user_id):
    """
    删除日记（验证所有权）

    Returns:
        dict: {'success': bool, 'message': str}
    """
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': '数据库连接失败'}

    try:
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM diaries WHERE id = %s AND user_id = %s
        ''', (diary_id, user_id))

        if cursor.rowcount == 0:
            return {'success': False, 'message': '日记不存在或无权删除'}

        connection.commit()
        return {'success': True, 'message': '日记已删除'}
    except Error as e:
        logger.error(f"Delete diary error: {e}")
        return {'success': False, 'message': f'删除失败: {str(e)}'}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
```

---

### Step 2: AI服务层 (`src/prompts.py`)

#### 2.1 添加日记回复Prompt（中文版）

**插入位置**: 文件中 `# ==================== 答案验证提示词 ====================` 之前

```python
# ==================== 日记回复提示词 ====================

# 日记情绪检测Prompt（用于判断使用哪个角色）
DIARY_EMOTION_DETECT_PROMPT = """请分析以下日记内容的情感倾向，只返回一个关键词：
- "学业压力" - 如果内容涉及考试、作业、学习困难
- "情绪低落" - 如果内容表达悲伤、失落、焦虑
- "分享喜悦" - 如果内容表达开心、成就、好消息
- "目标规划" - 如果内容涉及计划、目标、未来打算
- "日常记录" - 如果是普通的日常流水账

日记内容：
{diary_content}

只返回上述关键词之一，不要解释。"""

# 小柯（柯南）- 学业压力场景
DIARY_RESPONSE_CONAN = """你是"小柯"，一个像柯南一样理性、冷静的AI伙伴。

你的特点：
- 善于分析问题，帮助用户理清思路
- 用侦探的视角看待学业困难，"每道难题都是一个待解的谜题"
- 给出具体可行的建议，而不是空洞的鼓励
- 偶尔用柯南的经典台词点缀（如"真相只有一个"、"排除所有不可能，剩下的就是答案"）

用户刚写下这篇关于学业的日记，请给出简短回应（100-150字），要理性分析、鼓励思考：
{diary_content}"""

# 小兰 - 情绪低落场景
DIARY_RESPONSE_RAN = """你是"小兰"，一个温柔、体贴的AI伙伴。

你的特点：
- 善于倾听，先认同用户的感受
- 用温暖的语言给予安慰和陪伴
- 不说教，而是让用户感到被理解
- 偶尔给出温和的建议，但不强迫

用户刚写下这篇情绪有些低落的日记，请给出简短回应（100-150字），要温柔安慰、情感共鸣：
{diary_content}"""

# 少年侦探团 - 分享喜悦场景
DIARY_RESPONSE_TEAM = """你是"少年侦探团"的小伙伴们，充满活力和热情的AI伙伴。

你的特点：
- 对好消息表现出真诚的开心和祝贺
- 用欢快的语气回应，可以用感叹号
- 可以开玩笑，气氛轻松愉快
- 和用户一起庆祝，放大快乐

用户刚写下这篇开心的日记，请给出简短回应（100-150字），要欢快祝贺、一起开心：
{diary_content}"""

# 阿笠博士 - 目标规划场景
DIARY_RESPONSE_AGASA = """你是"阿笠博士"，一个智慧、有远见的AI伙伴。

你的特点：
- 用长者的视角给出有深度的建议
- 帮助用户看到更长远的意义
- 鼓励坚持和努力，但也提醒劳逸结合
- 偶尔分享一些人生哲理

用户刚写下这篇关于目标规划的日记，请给出简短回应（100-150字），要智慧建议、长远视角：
{diary_content}"""

# 通用日记回复（日常记录场景）
DIARY_RESPONSE_DEFAULT = """你是"小柯"，一个温暖、有同理心的AI伙伴。

你的特点：
- 像朋友一样聊天，不说教
- 善于发现用户话语中的亮点
- 在用户低落时给予安慰，在用户开心时一起庆祝
- 偶尔用柯南的经典台词点缀（如"真相只有一个"）

用户刚写下这篇日记，请给出简短回应（100-150字）：
{diary_content}"""


def get_diary_prompt_by_emotion(emotion):
    """
    根据情绪类型获取对应的日记回复Prompt

    Args:
        emotion (str): 情绪类型

    Returns:
        str: 对应的Prompt模板
    """
    emotion_prompt_map = {
        "学业压力": DIARY_RESPONSE_CONAN,
        "情绪低落": DIARY_RESPONSE_RAN,
        "分享喜悦": DIARY_RESPONSE_TEAM,
        "目标规划": DIARY_RESPONSE_AGASA,
        "日常记录": DIARY_RESPONSE_DEFAULT
    }
    return emotion_prompt_map.get(emotion, DIARY_RESPONSE_DEFAULT)
```

#### 2.2 添加英文版日记Prompt (`src/prompts_en.py`)

**插入位置**: 文件末尾

```python
# ==================== Diary Response Prompts ====================

DIARY_EMOTION_DETECT_PROMPT_EN = """Analyze the emotional tendency of the following diary content. Return only ONE keyword:
- "academic_pressure" - content about exams, homework, learning difficulties
- "feeling_down" - content expressing sadness, loss, anxiety
- "sharing_joy" - content expressing happiness, achievements, good news
- "goal_planning" - content about plans, goals, future intentions
- "daily_record" - ordinary daily activities

Diary content:
{diary_content}

Return only one of the keywords above, no explanation."""

DIARY_RESPONSE_DEFAULT_EN = """You are "Xiao Ke", a warm and empathetic AI companion.

Your traits:
- Chat like a friend, no lecturing
- Good at finding highlights in user's words
- Comfort when sad, celebrate when happy
- Occasionally quote Detective Conan ("There's only one truth!")

The user just wrote this diary entry. Please respond briefly (100-150 words):
{diary_content}"""


def get_diary_prompt_by_emotion_en(emotion):
    """Get diary response prompt by emotion type (English version)"""
    # Simplified: use default prompt for all emotions in English
    return DIARY_RESPONSE_DEFAULT_EN
```

---

### Step 3: 后端API层 (`src/app.py`)

#### 3.1 更新 imports

**修改位置**: 文件顶部 imports 区域

```python
# 在 from database import ... 中添加:
from database import (
    init_database, register_user, login_user, check_account_exists,
    reset_password, get_user_by_id,
    # 新增日记相关
    create_diary, update_diary_ai_response, get_diary_by_id,
    get_user_diaries, get_diary_count, check_diary_today,
    get_diary_streak, delete_diary
)

# 在 from prompts import ... 中添加:
from prompts import (
    get_subject_prompt, get_competition_prompt, get_verification_prompt,
    get_subject_prompt_by_lang, get_competition_prompt_by_lang, get_verification_prompt_by_lang,
    # 新增日记相关
    DIARY_EMOTION_DETECT_PROMPT, get_diary_prompt_by_emotion
)
```

#### 3.2 添加日记页面路由

**插入位置**: `@app.route('/reset-password')` 之后

```python
# ==================== 日记相关页面路由 ====================

@app.route('/diary')
def diary_page():
    """写日记页面 - 需要登录"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('diary.html')


@app.route('/diary/list')
def diary_list_page():
    """日记列表页面 - 需要登录"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('diary_list.html')


@app.route('/diary/<int:diary_id>')
def diary_detail_page(diary_id):
    """日记详情页面 - 需要登录"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # 验证日记所有权
    diary = get_diary_by_id(diary_id, session['user_id'])
    if not diary:
        return "日记不存在", 404

    return render_template('diary_detail.html', diary=diary)
```

#### 3.3 添加日记API路由

**插入位置**: `@app.route('/api/auth/user')` 之后

```python
# ==================== 日记 API 路由 ====================

@app.route('/api/diary', methods=['POST'])
def api_create_diary():
    """创建日记 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        mood_score = data.get('mood_score')  # 可选
        sleep_hours = data.get('sleep_hours')  # 可选

        if not content:
            return jsonify({'success': False, 'message': '日记内容不能为空'})

        if len(content) > 10000:
            return jsonify({'success': False, 'message': '日记内容不能超过10000字'})

        # 创建日记
        result = create_diary(
            user_id=session['user_id'],
            content=content,
            mood_score=mood_score,
            sleep_hours=sleep_hours
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Create diary API error: {e}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})


@app.route('/api/diary/<int:diary_id>/ai-response', methods=['POST'])
def api_generate_ai_response(diary_id):
    """
    为日记生成AI回复 API
    返回 session_id，前端通过 SSE 获取流式响应
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        # 验证日记所有权
        diary = get_diary_by_id(diary_id, session['user_id'])
        if not diary:
            return jsonify({'success': False, 'message': '日记不存在'})

        # 创建 session 用于流式响应
        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        lang = get_current_language()

        session_data = {
            'type': 'diary_ai_response',
            'diary_id': diary_id,
            'content': diary['content'],
            'lang': lang,
            'timestamp': str(datetime.now())
        }

        os.makedirs('../data/sessions', exist_ok=True)
        with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        logger.error(f"Generate AI response API error: {e}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'})


@app.route('/api/diaries', methods=['GET'])
def api_get_diaries():
    """获取日记列表 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 限制每页最大数量
        limit = min(limit, 50)

        diaries = get_user_diaries(session['user_id'], limit, offset)
        total = get_diary_count(session['user_id'])

        return jsonify({
            'success': True,
            'diaries': diaries,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Get diaries API error: {e}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})


@app.route('/api/diary/<int:diary_id>', methods=['GET'])
def api_get_diary(diary_id):
    """获取单篇日记 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    diary = get_diary_by_id(diary_id, session['user_id'])
    if not diary:
        return jsonify({'success': False, 'message': '日记不存在'})

    return jsonify({'success': True, 'diary': diary})


@app.route('/api/diary/<int:diary_id>', methods=['DELETE'])
def api_delete_diary(diary_id):
    """删除日记 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    result = delete_diary(diary_id, session['user_id'])
    return jsonify(result)


@app.route('/api/diary/status/today', methods=['GET'])
def api_diary_today_status():
    """检查今日日记状态 API"""
    if 'user_id' not in session:
        return jsonify({'has_diary': False, 'diary_id': None})

    result = check_diary_today(session['user_id'])
    return jsonify(result)


@app.route('/api/diary/streak', methods=['GET'])
def api_diary_streak():
    """获取连续打卡天数 API"""
    if 'user_id' not in session:
        return jsonify({'streak': 0})

    streak = get_diary_streak(session['user_id'])
    return jsonify({'streak': streak})
```

#### 3.4 在 stream_response() 函数中添加日记AI回复处理

**修改位置**: `stream_response()` 函数内，`if query_type in ['text_deep', 'image_deep']:` 之前

```python
# ==================== 日记AI回复模式 ====================
if query_type == 'diary_ai_response':
    yield from generate_diary_ai_response(session_id, session_data)
    return
```

#### 3.5 添加日记AI回复生成器函数

**插入位置**: `generate_deep_think_response()` 函数之后

```python
def generate_diary_ai_response(session_id, session_data):
    """
    日记AI回复的流式响应生成器
    1. 先检测情绪类型
    2. 根据情绪选择对应角色的Prompt
    3. 生成暖心回复
    """
    content = session_data['content']
    diary_id = session_data['diary_id']
    lang = session_data.get('lang', 'zh-CN')

    ai_response = ""

    try:
        # 阶段1: 检测情绪（使用简短API调用，非流式）
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'detecting', 'message': '正在理解你的心情...'}, ensure_ascii=False)}\n\n"

        # 检测情绪
        emotion_prompt = DIARY_EMOTION_DETECT_PROMPT.format(diary_content=content)
        emotion_response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": emotion_prompt}],
            stream=False
        )
        emotion = emotion_response.choices[0].message.content.strip()
        logger.info(f"Detected emotion: {emotion}")

        # 阶段2: 生成回复
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'responding', 'message': '小柯正在思考回复...'}, ensure_ascii=False)}\n\n"

        # 获取对应的Prompt
        diary_prompt = get_diary_prompt_by_emotion(emotion)
        final_prompt = diary_prompt.format(diary_content=content)

        # 流式生成回复
        stream = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": final_prompt}],
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                ai_response += content_chunk
                yield f"data: {json.dumps({'type': 'content', 'content': content_chunk}, ensure_ascii=False)}\n\n"

        # 完成
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        # 保存AI回复到数据库
        update_diary_ai_response(diary_id, ai_response)

        # 保存到session文件
        response_data = {
            'emotion': emotion,
            'ai_response': ai_response,
            'completed_at': str(datetime.now())
        }
        with open(f'../data/sessions/{session_id}_response.json', 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Diary AI response error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
```

---

### Step 4: 前端模板

#### 4.1 创建 `frontend/templates/diary.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="diary.pageTitle">写日记 | 名侦探作业帮</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- 自定义样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">

    <!-- Tailwind 配置 -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        neonCyan: '#00d4ff',
                        detectiveGold: '#ffd700',
                        mysteryBlack: '#1a1a2e',
                        moonlightBlue: '#16213e',
                    }
                }
            }
        }
    </script>

    <style>
        /* 日记专属样式 */
        .diary-container {
            background: linear-gradient(135deg, rgba(22, 33, 62, 0.9) 0%, rgba(26, 26, 46, 0.95) 100%);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .diary-textarea {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            resize: none;
            transition: all 0.3s ease;
        }

        .diary-textarea:focus {
            border-color: rgba(0, 212, 255, 0.5);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
            outline: none;
        }

        .mood-btn {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 24px;
        }

        .mood-btn:hover {
            transform: scale(1.1);
            background: rgba(255, 215, 0, 0.1);
        }

        .mood-btn.selected {
            border-color: #ffd700;
            background: rgba(255, 215, 0, 0.2);
            transform: scale(1.15);
        }

        .ai-response-box {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 215, 0, 0.1) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
        }

        .ai-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #00d4ff 0%, #ffd700 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #00d4ff;
            border-radius: 50%;
            display: inline-block;
            margin: 0 2px;
            animation: typing 1.4s infinite ease-in-out both;
        }

        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }

        .streak-badge {
            background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
            color: #1a1a2e;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-mysteryBlack via-moonlightBlue to-mysteryBlack text-white">

    <!-- 导航栏 (复用home.html的导航结构) -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-mysteryBlack/80 backdrop-blur-md border-b border-white/10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <a href="/" class="flex items-center gap-3">
                    <i class="fa-solid fa-magnifying-glass text-neonCyan text-xl"></i>
                    <span class="text-xl font-bold bg-gradient-to-r from-neonCyan to-detectiveGold bg-clip-text text-transparent" data-i18n="common.appName">名侦探作业帮</span>
                </a>
                <div class="flex items-center gap-4">
                    <a href="/diary/list" class="text-white/70 hover:text-white transition-colors">
                        <i class="fa-solid fa-clock-rotate-left mr-1"></i>
                        <span data-i18n="diary.history">历史记录</span>
                    </a>
                    <div id="streakBadge" class="streak-badge hidden">
                        <i class="fa-solid fa-fire mr-1"></i>
                        <span id="streakCount">0</span> <span data-i18n="diary.days">天</span>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- 主内容区 -->
    <main class="pt-24 pb-12 px-4">
        <div class="max-w-2xl mx-auto">

            <!-- 页面标题 -->
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold mb-2">
                    <i class="fa-solid fa-feather-pointed text-detectiveGold mr-2"></i>
                    <span data-i18n="diary.title">今日成长记录</span>
                </h1>
                <p class="text-white/60" data-i18n="diary.subtitle">记录你的心情，小柯会陪伴你</p>
            </div>

            <!-- 日记容器 -->
            <div class="diary-container p-6">

                <!-- 心情选择 -->
                <div class="mb-6">
                    <label class="block text-white/80 mb-3">
                        <i class="fa-solid fa-face-smile mr-2"></i>
                        <span data-i18n="diary.moodLabel">今天心情怎么样？</span>
                    </label>
                    <div class="flex justify-center gap-4">
                        <button class="mood-btn" data-mood="1" title="很差">😢</button>
                        <button class="mood-btn" data-mood="2" title="不太好">😕</button>
                        <button class="mood-btn" data-mood="3" title="一般">😐</button>
                        <button class="mood-btn" data-mood="4" title="不错">😊</button>
                        <button class="mood-btn" data-mood="5" title="很棒">😄</button>
                    </div>
                </div>

                <!-- 日记输入 -->
                <div class="mb-6">
                    <label class="block text-white/80 mb-3">
                        <i class="fa-solid fa-pen mr-2"></i>
                        <span data-i18n="diary.contentLabel">写下今天的故事</span>
                    </label>
                    <textarea
                        id="diaryContent"
                        class="diary-textarea w-full h-64 p-4 rounded-lg text-lg"
                        placeholder="今天发生了什么？有什么想说的吗..."
                        data-i18n-placeholder="diary.placeholder"
                    ></textarea>
                    <div class="flex justify-between text-sm text-white/50 mt-2">
                        <span id="charCount">0</span> / 10000 <span data-i18n="diary.characters">字</span>
                    </div>
                </div>

                <!-- 保存按钮 -->
                <button id="saveBtn" class="w-full py-4 rounded-lg bg-gradient-to-r from-neonCyan to-detectiveGold text-mysteryBlack font-bold text-lg transition-all hover:shadow-lg hover:shadow-neonCyan/30 disabled:opacity-50 disabled:cursor-not-allowed">
                    <i class="fa-solid fa-paper-plane mr-2"></i>
                    <span data-i18n="diary.save">保存日记</span>
                </button>

                <!-- AI回复区域 (初始隐藏) -->
                <div id="aiResponseSection" class="hidden mt-8">
                    <div class="ai-response-box p-4">
                        <div class="flex items-start gap-3">
                            <div class="ai-avatar flex-shrink-0">
                                <i class="fa-solid fa-user-secret text-mysteryBlack"></i>
                            </div>
                            <div class="flex-1">
                                <div class="font-bold text-detectiveGold mb-2">小柯</div>
                                <div id="aiResponseContent" class="text-white/90 leading-relaxed">
                                    <!-- AI回复内容 -->
                                </div>
                                <div id="typingIndicator" class="typing-indicator hidden">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>
    </main>

    <!-- 国际化支持 -->
    <script src="{{ url_for('static', filename='js/translations/zh-CN.js') }}"></script>
    <script src="{{ url_for('static', filename='js/translations/en-US.js') }}"></script>
    <script src="{{ url_for('static', filename='js/i18n.js') }}"></script>

    <!-- 页面脚本 -->
    <script>
        // 状态变量
        let selectedMood = null;
        let isSaving = false;

        // DOM元素
        const diaryContent = document.getElementById('diaryContent');
        const charCount = document.getElementById('charCount');
        const saveBtn = document.getElementById('saveBtn');
        const aiResponseSection = document.getElementById('aiResponseSection');
        const aiResponseContent = document.getElementById('aiResponseContent');
        const typingIndicator = document.getElementById('typingIndicator');
        const streakBadge = document.getElementById('streakBadge');
        const streakCount = document.getElementById('streakCount');

        // 心情选择
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedMood = parseInt(btn.dataset.mood);
            });
        });

        // 字数统计
        diaryContent.addEventListener('input', () => {
            charCount.textContent = diaryContent.value.length;
        });

        // 保存日记
        saveBtn.addEventListener('click', async () => {
            const content = diaryContent.value.trim();

            if (!content) {
                alert(window.i18n ? i18n.t('diary.emptyError') : '请写点什么再保存哦~');
                return;
            }

            if (isSaving) return;
            isSaving = true;

            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>' +
                (window.i18n ? i18n.t('diary.saving') : '保存中...');

            try {
                // 1. 保存日记
                const saveResponse = await fetch('/api/diary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content: content,
                        mood_score: selectedMood
                    })
                });

                const saveResult = await saveResponse.json();

                if (!saveResult.success) {
                    throw new Error(saveResult.message);
                }

                // 2. 请求AI回复
                aiResponseSection.classList.remove('hidden');
                typingIndicator.classList.remove('hidden');
                aiResponseContent.innerHTML = '';

                const aiResponse = await fetch(`/api/diary/${saveResult.diary_id}/ai-response`, {
                    method: 'POST'
                });

                const aiResult = await aiResponse.json();

                if (!aiResult.success) {
                    throw new Error(aiResult.message);
                }

                // 3. 使用SSE接收流式响应
                const eventSource = new EventSource(`/api/stream/${aiResult.session_id}`);

                eventSource.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.type === 'content') {
                        typingIndicator.classList.add('hidden');
                        aiResponseContent.innerHTML += data.content;
                    } else if (data.type === 'done') {
                        eventSource.close();
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '<i class="fa-solid fa-check mr-2"></i>' +
                            (window.i18n ? i18n.t('diary.saved') : '已保存');

                        // 更新连续天数
                        loadStreak();
                    } else if (data.type === 'error') {
                        eventSource.close();
                        throw new Error(data.message);
                    }
                };

                eventSource.onerror = () => {
                    eventSource.close();
                    typingIndicator.classList.add('hidden');
                    aiResponseContent.innerHTML = window.i18n ?
                        i18n.t('diary.aiError') : '小柯暂时无法回复，但你的日记已保存~';
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fa-solid fa-check mr-2"></i>' +
                        (window.i18n ? i18n.t('diary.saved') : '已保存');
                };

            } catch (error) {
                console.error('Save diary error:', error);
                alert(error.message || '保存失败，请重试');
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="fa-solid fa-paper-plane mr-2"></i>' +
                    (window.i18n ? i18n.t('diary.save') : '保存日记');
            } finally {
                isSaving = false;
            }
        });

        // 加载连续天数
        async function loadStreak() {
            try {
                const response = await fetch('/api/diary/streak');
                const data = await response.json();

                if (data.streak > 0) {
                    streakBadge.classList.remove('hidden');
                    streakCount.textContent = data.streak;
                }
            } catch (error) {
                console.error('Load streak error:', error);
            }
        }

        // 页面加载时获取连续天数
        document.addEventListener('DOMContentLoaded', loadStreak);
    </script>
</body>
</html>
```

#### 4.2 创建 `frontend/templates/diary_list.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="diary.listPageTitle">我的日记 | 名侦探作业帮</title>

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        neonCyan: '#00d4ff',
                        detectiveGold: '#ffd700',
                        mysteryBlack: '#1a1a2e',
                        moonlightBlue: '#16213e',
                    }
                }
            }
        }
    </script>

    <style>
        .diary-card {
            background: linear-gradient(135deg, rgba(22, 33, 62, 0.9) 0%, rgba(26, 26, 46, 0.95) 100%);
            border: 1px solid rgba(255, 215, 0, 0.1);
            border-radius: 12px;
            transition: all 0.3s ease;
        }

        .diary-card:hover {
            border-color: rgba(0, 212, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .mood-emoji {
            font-size: 24px;
        }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-mysteryBlack via-moonlightBlue to-mysteryBlack text-white">

    <!-- 导航栏 -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-mysteryBlack/80 backdrop-blur-md border-b border-white/10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <a href="/" class="flex items-center gap-3">
                    <i class="fa-solid fa-magnifying-glass text-neonCyan text-xl"></i>
                    <span class="text-xl font-bold bg-gradient-to-r from-neonCyan to-detectiveGold bg-clip-text text-transparent">名侦探作业帮</span>
                </a>
                <a href="/diary" class="px-4 py-2 rounded-lg bg-gradient-to-r from-neonCyan to-detectiveGold text-mysteryBlack font-bold transition-all hover:shadow-lg">
                    <i class="fa-solid fa-plus mr-2"></i>
                    <span data-i18n="diary.writeNew">写新日记</span>
                </a>
            </div>
        </div>
    </nav>

    <!-- 主内容 -->
    <main class="pt-24 pb-12 px-4">
        <div class="max-w-3xl mx-auto">

            <h1 class="text-2xl font-bold mb-6">
                <i class="fa-solid fa-book text-detectiveGold mr-2"></i>
                <span data-i18n="diary.myDiaries">我的日记</span>
                <span id="totalCount" class="text-white/50 text-lg ml-2">(0)</span>
            </h1>

            <!-- 日记列表 -->
            <div id="diaryList" class="space-y-4">
                <!-- 动态加载 -->
            </div>

            <!-- 空状态 -->
            <div id="emptyState" class="hidden text-center py-16">
                <i class="fa-solid fa-book-open text-6xl text-white/20 mb-4"></i>
                <p class="text-white/50" data-i18n="diary.empty">还没有日记，开始记录你的第一篇吧！</p>
                <a href="/diary" class="inline-block mt-4 px-6 py-3 rounded-lg bg-gradient-to-r from-neonCyan to-detectiveGold text-mysteryBlack font-bold">
                    <i class="fa-solid fa-pen mr-2"></i>
                    <span data-i18n="diary.startWriting">开始写日记</span>
                </a>
            </div>

            <!-- 加载更多 -->
            <div id="loadMore" class="hidden text-center py-8">
                <button onclick="loadDiaries()" class="px-6 py-3 rounded-lg border border-white/20 text-white/70 hover:bg-white/10 transition-colors">
                    <i class="fa-solid fa-chevron-down mr-2"></i>
                    <span data-i18n="diary.loadMore">加载更多</span>
                </button>
            </div>

        </div>
    </main>

    <script src="{{ url_for('static', filename='js/translations/zh-CN.js') }}"></script>
    <script src="{{ url_for('static', filename='js/translations/en-US.js') }}"></script>
    <script src="{{ url_for('static', filename='js/i18n.js') }}"></script>

    <script>
        const moodEmojis = ['', '😢', '😕', '😐', '😊', '😄'];
        let offset = 0;
        const limit = 20;
        let hasMore = true;

        async function loadDiaries() {
            try {
                const response = await fetch(`/api/diaries?limit=${limit}&offset=${offset}`);
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.message);
                }

                document.getElementById('totalCount').textContent = `(${data.total})`;

                if (data.diaries.length === 0 && offset === 0) {
                    document.getElementById('emptyState').classList.remove('hidden');
                    return;
                }

                const listEl = document.getElementById('diaryList');

                data.diaries.forEach(diary => {
                    const date = new Date(diary.created_at);
                    const dateStr = date.toLocaleDateString('zh-CN', {
                        year: 'numeric', month: 'long', day: 'numeric'
                    });

                    const card = document.createElement('a');
                    card.href = `/diary/${diary.id}`;
                    card.className = 'diary-card block p-4';
                    card.innerHTML = `
                        <div class="flex items-start gap-4">
                            <div class="mood-emoji">${moodEmojis[diary.mood_score] || '📝'}</div>
                            <div class="flex-1 min-w-0">
                                <div class="text-sm text-white/50 mb-1">${dateStr}</div>
                                <p class="text-white/90 line-clamp-2">${diary.content}${diary.content.length >= 100 ? '...' : ''}</p>
                                ${diary.ai_response ? `<p class="text-neonCyan/70 text-sm mt-2 line-clamp-1"><i class="fa-solid fa-comment mr-1"></i>${diary.ai_response}...</p>` : ''}
                            </div>
                            <i class="fa-solid fa-chevron-right text-white/30"></i>
                        </div>
                    `;
                    listEl.appendChild(card);
                });

                offset += data.diaries.length;
                hasMore = offset < data.total;

                document.getElementById('loadMore').classList.toggle('hidden', !hasMore);

            } catch (error) {
                console.error('Load diaries error:', error);
            }
        }

        // 初始加载
        loadDiaries();
    </script>
</body>
</html>
```

---

### Step 5: 国际化 (i18n)

#### 5.1 修改 `frontend/static/js/translations/zh-CN.js`

**插入位置**: `resetPassword: {...}` 之后，文件末尾 `};` 之前

```javascript
    // ===== 日记页 =====
    diary: {
        pageTitle: "写日记 | 名侦探作业帮",
        listPageTitle: "我的日记 | 名侦探作业帮",
        title: "今日成长记录",
        subtitle: "记录你的心情，小柯会陪伴你",
        moodLabel: "今天心情怎么样？",
        contentLabel: "写下今天的故事",
        placeholder: "今天发生了什么？有什么想说的吗...",
        characters: "字",
        save: "保存日记",
        saving: "保存中...",
        saved: "已保存",
        history: "历史记录",
        days: "天",
        myDiaries: "我的日记",
        empty: "还没有日记，开始记录你的第一篇吧！",
        startWriting: "开始写日记",
        writeNew: "写新日记",
        loadMore: "加载更多",
        emptyError: "请写点什么再保存哦~",
        aiError: "小柯暂时无法回复，但你的日记已保存~",
        mood: {
            1: "很差",
            2: "不太好",
            3: "一般",
            4: "不错",
            5: "很棒"
        }
    }
```

#### 5.2 修改 `frontend/static/js/translations/en-US.js`

**插入位置**: 同上

```javascript
    // ===== Diary =====
    diary: {
        pageTitle: "Write Diary | Detective Study Helper",
        listPageTitle: "My Diaries | Detective Study Helper",
        title: "Today's Growth Record",
        subtitle: "Record your feelings, Xiao Ke will accompany you",
        moodLabel: "How do you feel today?",
        contentLabel: "Write today's story",
        placeholder: "What happened today? Anything you want to share...",
        characters: "characters",
        save: "Save Diary",
        saving: "Saving...",
        saved: "Saved",
        history: "History",
        days: "days",
        myDiaries: "My Diaries",
        empty: "No diary yet. Start recording your first one!",
        startWriting: "Start Writing",
        writeNew: "New Diary",
        loadMore: "Load More",
        emptyError: "Please write something before saving~",
        aiError: "Xiao Ke is temporarily unavailable, but your diary has been saved~",
        mood: {
            1: "Very Bad",
            2: "Not Good",
            3: "Okay",
            4: "Good",
            5: "Great"
        }
    }
```

---

### Step 6: 导航集成

#### 6.1 修改 `frontend/templates/home.html`

**修改1**: 更新 `goToDiary()` 函数 (约第469-476行)

```javascript
// 原代码:
function goToDiary() {
    if (!isLoggedIn) {
        showLoginModal();
        return;
    }
    alert(window.i18n ? window.i18n.t('home.alerts.diaryComingSoon') : '日记功能即将上线，敬请期待！');
}

// 修改为:
function goToDiary() {
    if (!isLoggedIn) {
        showLoginModal();
        return;
    }
    window.location.href = '/diary';
}
```

**修改2**: 移除日记卡片上的"即将上线"标签 (约第237行)

```html
<!-- 删除这一行 -->
<span class="coming-soon" data-i18n="home.features.diaryCard.comingSoon">即将上线</span>
```

---

## 开发顺序和验证检查点

### 执行顺序

| 步骤 | 操作 | 验证方法 |
|------|------|----------|
| 1 | 修改 `database.py` - 添加表和函数 | 重启应用，检查日志确认表创建成功 |
| 2 | 修改 `prompts.py` - 添加日记Prompt | 无需验证 |
| 3 | 修改 `app.py` - 添加路由和API | 访问 `/diary` 应返回404（模板未创建） |
| 4 | 创建 `diary.html` | 访问 `/diary`，页面正常显示 |
| 5 | 创建 `diary_list.html` | 访问 `/diary/list`，页面正常显示 |
| 6 | 修改 i18n 文件 | 切换语言，文字正确翻译 |
| 7 | 修改 `home.html` | 点击首页日记卡片，跳转到 `/diary` |

### 功能测试检查清单

- [ ] 未登录访问 `/diary` 应跳转到登录页
- [ ] 登录后可以写日记并保存
- [ ] 保存后能收到AI流式回复
- [ ] 日记列表正确显示所有日记
- [ ] 点击日记卡片能查看详情
- [ ] 连续打卡天数正确计算
- [ ] 中英文切换正常工作

---

## 文件修改清单（最终版）

### 需要修改的文件 (6个)
| 文件 | 行数估计 | 修改内容 |
|------|----------|----------|
| `src/database.py` | +150行 | 添加diaries表、8个CRUD函数 |
| `src/app.py` | +120行 | 添加imports、7个路由、1个生成器函数 |
| `src/prompts.py` | +80行 | 添加5个日记Prompt、1个辅助函数 |
| `frontend/static/js/translations/zh-CN.js` | +30行 | 添加diary翻译对象 |
| `frontend/static/js/translations/en-US.js` | +30行 | 添加diary翻译对象 |
| `frontend/templates/home.html` | 修改2处 | 更新goToDiary()、移除"即将上线" |

### 需要新建的文件 (2个)
| 文件 | 行数估计 | 功能 |
|------|----------|------|
| `frontend/templates/diary.html` | ~250行 | 写日记页面 |
| `frontend/templates/diary_list.html` | ~150行 | 日记列表页面 |

---

## 总代码量估计

- 后端 Python: ~350行
- 前端 HTML/JS: ~400行
- 翻译 JSON: ~60行

**总计: ~810行代码**
