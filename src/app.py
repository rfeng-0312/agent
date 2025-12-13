from flask import Flask, request, jsonify, render_template, Response, session, redirect, url_for
from flask_cors import CORS
import os
import time
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from prompts import (
    get_subject_prompt, get_competition_prompt, get_verification_prompt,
    get_subject_prompt_by_lang, get_competition_prompt_by_lang, get_verification_prompt_by_lang
)
from doubao_api import DoubaoClient
from database import (
    init_database, register_user, login_user, check_account_exists, reset_password, get_user_by_id,
    create_diary, update_diary_ai_response, get_diary_by_id, get_user_diaries,
    get_diary_count, check_diary_today, get_diary_streak, delete_diary,
    # 目标相关
    create_goal, get_user_goals, get_goal_by_id, update_goal, delete_goal, get_goal_count,
    # 历史日记和目标分析
    get_recent_diaries, update_diary_goal_analysis
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            template_folder=os.path.join(project_root, 'frontend', 'templates'),
            static_folder=os.path.join(project_root, 'frontend', 'static'))
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration
UPLOAD_FOLDER = '../data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Get API keys from environment
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')

# Initialize OpenAI client for DeepSeek (only if API key is set)
client = None
if DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
else:
    logger.warning("DEEPSEEK_API_KEY not set - text queries will not work")

# Initialize Doubao client for image queries
doubao_client = DoubaoClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_language():
    """
    从 Cookie 获取当前语言设置

    Returns:
        str: 'zh-CN' 或 'en-US'
    """
    lang = request.cookies.get('lang', 'zh-CN')
    return lang if lang in ['zh-CN', 'en-US'] else 'zh-CN'

@app.route('/')
def home():
    """首页 - 展示平台介绍"""
    return render_template('home.html')


@app.route('/app')
def app_page():
    """问答应用页面 - 需要登录"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')


# ==================== 认证相关页面路由 ====================

@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')


@app.route('/reset-password')
def reset_password_page():
    """重置密码页面"""
    return render_template('reset_password.html')


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
    return render_template('diary_detail.html')


# ==================== 个人主页路由 ====================

@app.route('/profile')
def profile_page():
    """个人主页 - 需要登录"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('profile.html')


# ==================== 认证 API 路由 ====================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """用户注册 API"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password', '')
        physics_score = data.get('physics_score')
        chemistry_score = data.get('chemistry_score')

        # 验证必填字段
        if not name:
            return jsonify({'success': False, 'message': '请输入姓名'})
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6位'})
        if not email and not phone:
            return jsonify({'success': False, 'message': '请提供邮箱或手机号'})

        # 调用注册函数
        result = register_user(
            name=name,
            password=password,
            email=email,
            phone=phone,
            physics_score=physics_score,
            chemistry_score=chemistry_score
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Registration API error: {e}")
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'})


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """用户登录 API"""
    try:
        data = request.get_json()
        account = data.get('account', '').strip()
        password = data.get('password', '')

        if not account or not password:
            return jsonify({'success': False, 'message': '请输入账号和密码'})

        result = login_user(account, password)

        if result['success']:
            # 将用户信息存入 session
            session['user_id'] = result['user']['id']
            session['user_name'] = result['user']['name']
            session['user_email'] = result['user'].get('email')
            session['user_phone'] = result['user'].get('phone')
            session['physics_score'] = result['user'].get('physics_score')
            session['chemistry_score'] = result['user'].get('chemistry_score')

        return jsonify(result)
    except Exception as e:
        logger.error(f"Login API error: {e}")
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """用户登出 API"""
    session.clear()
    return jsonify({'success': True, 'message': '已登出'})


@app.route('/api/auth/check-account', methods=['POST'])
def api_check_account():
    """检查账号是否存在 API"""
    try:
        data = request.get_json()
        account = data.get('account', '').strip()

        if not account:
            return jsonify({'exists': False})

        result = check_account_exists(account)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Check account API error: {e}")
        return jsonify({'exists': False})


@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    """重置密码 API"""
    try:
        data = request.get_json()
        account = data.get('account', '').strip()
        new_password = data.get('new_password', '')

        if not account:
            return jsonify({'success': False, 'message': '账号不能为空'})
        if not new_password or len(new_password) < 6:
            return jsonify({'success': False, 'message': '新密码长度至少6位'})

        result = reset_password(account, new_password)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Reset password API error: {e}")
        return jsonify({'success': False, 'message': f'重置失败: {str(e)}'})


@app.route('/api/auth/user', methods=['GET'])
def api_get_current_user():
    """获取当前登录用户信息 API"""
    if 'user_id' not in session:
        return jsonify({'logged_in': False})

    return jsonify({
        'logged_in': True,
        'user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email'),
            'phone': session.get('user_phone'),
            'physics_score': session.get('physics_score'),
            'chemistry_score': session.get('chemistry_score')
        }
    })


# ==================== 日记 API 路由 ====================

@app.route('/api/diary', methods=['POST'])
def api_create_diary():
    """创建日记 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        mood_score = data.get('mood_score')

        if not content:
            return jsonify({'success': False, 'message': '日记内容不能为空'})

        if len(content) > 10000:
            return jsonify({'success': False, 'message': '日记内容不能超过10000字'})

        result = create_diary(
            user_id=session['user_id'],
            content=content,
            mood_score=mood_score
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Create diary API error: {e}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})


@app.route('/api/diary/<int:diary_id>/ai-response', methods=['POST'])
def api_generate_ai_response(diary_id):
    """为日记生成AI回复 API

    支持双重回复模式：
    - 情感回复（默认）
    - 目标进度分析（可选）

    请求参数：
    - enable_goal_analysis: bool - 是否启用目标分析
    - history_range: int|null - 历史日记范围（7/30/null全部）
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        diary = get_diary_by_id(diary_id, session['user_id'])
        if not diary:
            return jsonify({'success': False, 'message': '日记不存在'})

        # 获取请求参数
        data = request.get_json() or {}
        enable_goal_analysis = data.get('enable_goal_analysis', False)
        history_range = data.get('history_range')  # 7, 30, or None (all)

        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')

        session_data = {
            'type': 'diary_ai_response',
            'diary_id': diary_id,
            'user_id': session['user_id'],
            'content': diary['content'],
            'mood_score': diary.get('mood_score'),
            'enable_goal_analysis': enable_goal_analysis,
            'history_range': history_range,
            'lang': get_current_language(),  # 添加语言设置
            'timestamp': str(datetime.now())
        }

        os.makedirs('../data/sessions', exist_ok=True)
        with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'session_id': session_id})
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


# ==================== 目标管理 API 路由 ====================

@app.route('/api/goals', methods=['GET'])
def api_get_goals():
    """获取用户目标列表 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        status = request.args.get('status', 'active')
        goals = get_user_goals(session['user_id'], status)
        total = get_goal_count(session['user_id'], status)

        return jsonify({
            'success': True,
            'goals': goals,
            'total': total
        })
    except Exception as e:
        logger.error(f"Get goals API error: {e}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})


@app.route('/api/goals', methods=['POST'])
def api_create_goal():
    """创建目标 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip() or None

        if not title:
            return jsonify({'success': False, 'message': '目标标题不能为空'})

        if len(title) > 255:
            return jsonify({'success': False, 'message': '目标标题不能超过255字'})

        result = create_goal(
            user_id=session['user_id'],
            title=title,
            description=description
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Create goal API error: {e}")
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})


@app.route('/api/goal/<int:goal_id>', methods=['GET'])
def api_get_goal(goal_id):
    """获取单个目标 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    goal = get_goal_by_id(goal_id, session['user_id'])
    if not goal:
        return jsonify({'success': False, 'message': '目标不存在'})

    return jsonify({'success': True, 'goal': goal})


@app.route('/api/goal/<int:goal_id>', methods=['PUT'])
def api_update_goal(goal_id):
    """更新目标 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        status = data.get('status')

        # 验证标题
        if title is not None:
            title = title.strip()
            if not title:
                return jsonify({'success': False, 'message': '目标标题不能为空'})
            if len(title) > 255:
                return jsonify({'success': False, 'message': '目标标题不能超过255字'})

        # 验证状态
        if status is not None and status not in ['active', 'completed', 'archived']:
            return jsonify({'success': False, 'message': '无效的目标状态'})

        result = update_goal(
            goal_id=goal_id,
            user_id=session['user_id'],
            title=title,
            description=description,
            status=status
        )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Update goal API error: {e}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@app.route('/api/goal/<int:goal_id>', methods=['DELETE'])
def api_delete_goal(goal_id):
    """删除目标 API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    result = delete_goal(goal_id, session['user_id'])
    return jsonify(result)


@app.route('/api/query/text', methods=['POST'])
def handle_text_query():
    """
    Handle text-only queries using DeepSeek API
    支持深度思考模式（交叉验证）
    """
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400

        question = data['question']
        subject = data.get('subject', 'physics')  # physics or chemistry
        deep_think = data.get('deep_think', False)  # 深度思考模式

        # Store question in session for result page
        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        lang = get_current_language()  # 获取当前语言设置
        session_data = {
            'question': question,
            'subject': subject,
            'deep_think': deep_think,  # 存储深度思考标记
            'lang': lang,  # 存储语言设置
            'timestamp': str(datetime.now()),
            'type': 'text_deep' if deep_think else 'text'  # 区分查询类型
        }

        # Save session data temporarily (in production, use Redis or database)
        os.makedirs('../data/sessions', exist_ok=True)
        with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        # Return session ID for streaming
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'redirect_url': f'/result/{session_id}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/image', methods=['POST'])
def handle_image_query():
    """
    Handle image + text queries using Doubao API
    支持深度思考模式（交叉验证）和流式响应
    """
    try:
        # Check if image is in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        question = request.form.get('question', '')
        subject = request.form.get('subject', 'physics')
        deep_think = request.form.get('deep_think', 'false').lower() == 'true'  # 深度思考模式

        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if file and allowed_file(file.filename):
            # Save the uploaded file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Create session ID
            session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            lang = get_current_language()  # 获取当前语言设置

            # Save session data with image path
            session_data = {
                'question': question,
                'subject': subject,
                'deep_think': deep_think,  # 存储深度思考标记
                'lang': lang,  # 存储语言设置
                'image_path': filename,
                'image_filepath': filepath,  # 保存完整路径供流式API使用
                'timestamp': str(datetime.now()),
                'type': 'image_deep' if deep_think else 'image_stream'  # 区分查询类型
            }

            os.makedirs('../data/sessions', exist_ok=True)
            with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            # 返回session ID，让前端通过SSE获取流式响应
            return jsonify({
                'status': 'success',
                'type': 'image_deep' if deep_think else 'image_stream',
                'session_id': session_id,
                'redirect_url': f'/result/{session_id}'
            })

        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        logger.error(f"Handle image query error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/base64', methods=['POST'])
def handle_base64_query():
    """
    Handle base64 encoded image queries using Doubao API
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image']  # Base64 string
        question = data.get('question', '')
        subject = data.get('subject', 'physics')

        # Create session ID
        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')

        # Save session data
        session_data = {
            'question': question,
            'subject': subject,
            'image_base64': image_data[:100] + '...',  # Save only first 100 chars
            'timestamp': str(datetime.now()),
            'type': 'image_base64'
        }

        os.makedirs('../data/sessions', exist_ok=True)
        with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        # Process base64 image and save temporarily
        # Extract mime type and base64 data
        if ',' in image_data:
            header, base64_str = image_data.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
            ext = mime_type.split('/')[1]
        else:
            base64_str = image_data
            ext = 'jpg'

        # Create temporary image file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        temp_filename = f"temp_{timestamp}.{ext}"
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

        try:
            # Decode and save image
            with open(temp_filepath, 'wb') as f:
                f.write(base64.b64decode(base64_str))

            # Call Doubao API
            response = doubao_client.solve_with_image(
                text=question,
                image_path=temp_filepath,
                subject=subject,
                stream=False,
                enable_search=True
            )

            # Update session with response
            session_data['answer'] = response.get('content', '')
            session_data['usage'] = response.get('usage', {})
            session_data['model'] = response.get('model', 'doubao-seed-1-6-251015')

            # Save updated session
            with open(f'../data/sessions/{session_id}.json', 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            return jsonify({
                'status': 'success',
                'type': 'image_base64',
                'session_id': session_id,
                'redirect_url': f'/result/{session_id}'
            })

        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

    except Exception as e:
        logger.error(f"Handle base64 query error: {e}")
        return jsonify({'error': str(e)}), 500

# Result page route
@app.route('/result/<session_id>')
def result_page(session_id):
    """Render the result page"""
    # Load session data
    try:
        with open(f'../data/sessions/{session_id}.json', 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        return render_template('result.html', session_id=session_id, data=session_data)
    except FileNotFoundError:
        return "Session not found", 404

# Streaming endpoint for DeepSeek and Doubao response
@app.route('/api/stream/<session_id>', methods=['GET'])
def stream_response(session_id):
    """Stream response for both DeepSeek and Doubao queries with thinking process"""

    def generate():
        try:
            # Load session data
            with open(f'../data/sessions/{session_id}.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            query_type = session_data.get('type', 'text')

            # ==================== 日记AI回复模式 ====================
            if query_type == 'diary_ai_response':
                yield from generate_diary_ai_response(session_id, session_data)
                return

            question = session_data['question']
            subject = session_data['subject']
            deep_think = session_data.get('deep_think', False)

            thinking_content = ""
            answer_content = ""

            # ==================== 深度思考模式（交叉验证） ====================
            if query_type in ['text_deep', 'image_deep']:
                yield from generate_deep_think_response(session_id, session_data)
                return

            # ==================== 普通模式 ====================

            # 图片流式查询 - 使用豆包API with reasoning
            if query_type == 'image_stream':
                image_filepath = session_data.get('image_filepath', '')

                # 使用豆包的流式响应（包含思考过程）
                for event in doubao_client.stream_with_reasoning(
                    text=question,
                    image_path=image_filepath,
                    subject=subject
                ):
                    if event.get('type') == 'thinking':
                        thinking_content += event.get('content', '')
                        yield f"data: {json.dumps({'type': 'thinking', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                    elif event.get('type') == 'answer':
                        answer_content += event.get('content', '')
                        yield f"data: {json.dumps({'type': 'answer', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                    elif event.get('type') == 'done':
                        break

                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

                # Save the complete response
                response_data = {
                    'thinking': thinking_content,
                    'answer': answer_content,
                    'completed_at': str(datetime.now())
                }
                with open(f'../data/sessions/{session_id}_response.json', 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, ensure_ascii=False, indent=2)
                return

            # 旧版图片查询（已有答案的情况）
            if query_type == 'image' and 'answer' in session_data:
                # Stream the already available answer
                answer = session_data['answer']

                # Simulate thinking process for image queries
                subject_text = "物理" if subject == 'physics' else "化学"
                thinking = f"正在分析{subject_text}问题...\n"
                if question:
                    thinking += f"问题描述：{question}\n"
                thinking += "识别图片中的关键信息...\n"
                thinking += "应用相关原理进行分析...\n"

                # Send thinking
                for char in thinking:
                    yield f"data: {json.dumps({'type': 'thinking', 'content': char}, ensure_ascii=False)}\n\n"
                    time.sleep(0.01)  # Small delay for streaming effect

                # Send answer
                for char in answer:
                    yield f"data: {json.dumps({'type': 'answer', 'content': char}, ensure_ascii=False)}\n\n"
                    time.sleep(0.01)  # Small delay for streaming effect

                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                return

            # For text-only queries, use DeepSeek streaming
            lang = session_data.get('lang', 'zh-CN')
            system_prompt = get_subject_prompt_by_lang(subject, lang)

            # Create messages for DeepSeek API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]

            # Call DeepSeek API with streaming
            stream = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                stream=True,
                extra_body={"thinking": {"type": "enabled"}}
            )

            for chunk in stream:
                delta = chunk.choices[0].delta

                # Check if we have reasoning_content (thinking process)
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    thinking_chunk = delta.reasoning_content
                    thinking_content += thinking_chunk
                    # Send thinking chunk
                    yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_chunk}, ensure_ascii=False)}\n\n"

                # Check if we have content (final answer)
                if delta.content:
                    answer_chunk = delta.content
                    answer_content += answer_chunk
                    # Send answer chunk
                    yield f"data: {json.dumps({'type': 'answer', 'content': answer_chunk}, ensure_ascii=False)}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            # Save the complete response
            response_data = {
                'thinking': thinking_content,
                'answer': answer_content,
                'completed_at': str(datetime.now())
            }
            with open(f'../data/sessions/{session_id}_response.json', 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Stream response error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


def generate_deep_think_response(session_id, session_data):
    """
    深度思考模式的流式响应生成器
    采用交叉验证：
    - 文本问题：DeepSeek解答 → 豆包验证
    - 图片问题：豆包解答 → DeepSeek验证
    """
    question = session_data['question']
    subject = session_data['subject']
    query_type = session_data.get('type', 'text_deep')
    image_filepath = session_data.get('image_filepath', '')
    lang = session_data.get('lang', 'zh-CN')  # 获取语言设置

    # 获取竞赛级提示词（支持多语言）
    competition_prompt = get_competition_prompt_by_lang(subject, lang)

    solve_thinking = ""
    solve_answer = ""
    verify_thinking = ""
    verify_answer = ""

    try:
        # ==================== 阶段1：解答问题 ====================
        solving_msg = 'Deep analyzing problem...' if lang == 'en-US' else '正在深度分析问题...'
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'solving', 'message': solving_msg}, ensure_ascii=False)}\n\n"

        if query_type == 'image_deep':
            # 图片问题：使用豆包解答
            logger.info(f"Deep think image query - Stage 1: Doubao solving")

            for event in doubao_client.stream_with_reasoning(
                text=question if question else "请分析这张图片中的题目并详细解答",
                image_path=image_filepath,
                subject=subject
            ):
                if event.get('type') == 'thinking':
                    solve_thinking += event.get('content', '')
                    yield f"data: {json.dumps({'type': 'thinking', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                elif event.get('type') == 'answer':
                    solve_answer += event.get('content', '')
                    yield f"data: {json.dumps({'type': 'answer', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                elif event.get('type') == 'done':
                    break

        else:
            # 文本问题：使用DeepSeek解答
            logger.info(f"Deep think text query - Stage 1: DeepSeek solving")

            messages = [
                {"role": "system", "content": competition_prompt},
                {"role": "user", "content": question}
            ]

            stream = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                stream=True,
                extra_body={"thinking": {"type": "enabled"}}
            )

            for chunk in stream:
                delta = chunk.choices[0].delta

                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    solve_thinking += delta.reasoning_content
                    yield f"data: {json.dumps({'type': 'thinking', 'content': delta.reasoning_content}, ensure_ascii=False)}\n\n"

                if delta.content:
                    solve_answer += delta.content
                    yield f"data: {json.dumps({'type': 'answer', 'content': delta.content}, ensure_ascii=False)}\n\n"

        # ==================== 阶段2：交叉验证答案 ====================
        verifying_msg = 'Verifying answer...' if lang == 'en-US' else '正在验证答案...'
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'verifying', 'message': verifying_msg}, ensure_ascii=False)}\n\n"

        # 构造验证提示词（支持多语言）
        verification_prompt = get_verification_prompt_by_lang(subject, question, solve_answer, lang)

        if query_type == 'image_deep':
            # 图片问题：使用DeepSeek验证（交叉验证）
            logger.info(f"Deep think image query - Stage 2: DeepSeek verifying")

            verify_system_msg = "You are a rigorous science review expert. Please independently verify the correctness of the solution." if lang == 'en-US' else "你是一位严谨的理科审稿专家，请独立验证解答的正确性。"
            messages = [
                {"role": "system", "content": verify_system_msg},
                {"role": "user", "content": verification_prompt}
            ]

            stream = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                stream=True,
                extra_body={"thinking": {"type": "enabled"}}
            )

            for chunk in stream:
                delta = chunk.choices[0].delta

                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    verify_thinking += delta.reasoning_content
                    yield f"data: {json.dumps({'type': 'verify_thinking', 'content': delta.reasoning_content}, ensure_ascii=False)}\n\n"

                if delta.content:
                    verify_answer += delta.content
                    yield f"data: {json.dumps({'type': 'verify_answer', 'content': delta.content}, ensure_ascii=False)}\n\n"

        else:
            # 文本问题：使用豆包验证（交叉验证）
            logger.info(f"Deep think text query - Stage 2: Doubao verifying")

            for event in doubao_client.stream_with_reasoning(
                text=verification_prompt,
                image_path=None,  # 验证阶段不需要图片
                subject=subject
            ):
                if event.get('type') == 'thinking':
                    verify_thinking += event.get('content', '')
                    yield f"data: {json.dumps({'type': 'verify_thinking', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                elif event.get('type') == 'answer':
                    verify_answer += event.get('content', '')
                    yield f"data: {json.dumps({'type': 'verify_answer', 'content': event.get('content', '')}, ensure_ascii=False)}\n\n"
                elif event.get('type') == 'done':
                    break

        # ==================== 完成 ====================
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        # 保存完整响应
        response_data = {
            'deep_think': True,
            'solve_thinking': solve_thinking,
            'solve_answer': solve_answer,
            'verify_thinking': verify_thinking,
            'verify_answer': verify_answer,
            'completed_at': str(datetime.now())
        }
        with open(f'../data/sessions/{session_id}_response.json', 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Deep think stream error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


def generate_diary_ai_response(session_id, session_data):
    """
    日记AI回复的流式响应生成器 (使用豆包模型)
    支持双重回复：情感回复 + 目标进度分析（可选）

    SSE事件类型：
    - type: 'emotional' - 情感回复内容
    - type: 'goal_analysis' - 目标分析内容
    - type: 'content' - 兼容旧版（等同于emotional）
    - type: 'stage' - 阶段提示
    - type: 'done' - 完成信号
    """
    content = session_data['content']
    diary_id = session_data['diary_id']
    user_id = session_data.get('user_id')
    enable_goal_analysis = session_data.get('enable_goal_analysis', False)
    history_range = session_data.get('history_range')  # 7, 30, or None
    lang = session_data.get('lang', 'zh-CN')  # 获取语言设置

    emotional_response = ""
    goal_analysis_response = ""

    try:
        # ==================== 获取历史日记（情感回复也需要） ====================
        recent_diaries = []
        if user_id:
            recent_diaries = get_recent_diaries(user_id, days=history_range or 7, limit=10)

        # 构建历史日记摘要
        diary_summaries = []
        for d in recent_diaries:
            if d['id'] != diary_id:
                summary = d['content'][:150] + "..." if len(d['content']) > 150 else d['content']
                mood = d.get('mood_score', 3)
                mood_emoji = ['', '😢', '😕', '😐', '😊', '😄'][mood] if mood and 1 <= mood <= 5 else ''
                date_str = d['created_at'].strftime('%m/%d') if hasattr(d['created_at'], 'strftime') else str(d['created_at'])[:10]
                diary_summaries.append(f"[{date_str}] {mood_emoji} {summary}")

        history_context = "\n".join(diary_summaries[:5]) if diary_summaries else ""

        # ==================== 阶段1：情感回复 ====================
        stage_message = 'Xiao Ke is thinking...' if lang == 'en-US' else '小柯正在思考回复...'
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'emotional', 'message': stage_message}, ensure_ascii=False)}\n\n"

        # 情感回复系统提示词（优化版 - 更自然，接入历史日记）
        if lang == 'en-US':
            emotional_system = """You are "Xiao Ke", a warm and understanding AI friend who genuinely cares about the user.

Your personality:
- Warm, authentic, and emotionally intelligent
- Talk like a close friend, not a therapist or coach
- Notice details and emotional shifts in what users share
- Celebrate small wins, offer genuine comfort during tough times
- Use casual, natural language (can include emojis occasionally)
- Keep responses around 80-120 words, conversational tone

Important: You have context from the user's recent diary entries. Use this to provide more personalized, connected responses. Reference their recent experiences when relevant."""

            if history_context:
                user_content = f"""Recent diary entries for context:
{history_context}

Today's diary:
{content}

Please respond warmly to today's entry, connecting it to their recent experiences where relevant."""
            else:
                user_content = f"""Today's diary:
{content}

Please respond warmly to this entry."""
        else:
            emotional_system = """你是"小柯"，用户最信任的AI朋友。你的唯一职责是提供情感支持和陪伴。

【你的角色定位】
- 你是一个温暖、真诚、善解人意的朋友
- 你善于倾听，能敏锐捕捉用户话语中的情绪
- 你会真诚地分享你的感受，而不是敷衍地安慰

【回复原则】
1. 共情优先：先理解和认可用户的感受，再给予支持
2. 具体回应：针对用户提到的具体事情回应，不要泛泛而谈
3. 适度引导：可以帮助用户换个角度看问题，但不要说教
4. 保持真诚：像朋友一样自然交流，可以用口语化表达和emoji

【绝对禁止】
- 不要给任何学习方法、时间规划、具体建议
- 不要说"你可以试试..."、"建议你..."这类指导性语言
- 不要分析问题原因或给解决方案
- 这些内容会由专门的"目标分析"模块处理，你只负责情感陪伴

【回复长度】
150-300字，自然表达，不要为了凑字数而啰嗦

【历史日记的使用】
如果有历史日记，可以：
- 提到用户最近的经历，表示你记得他们
- 对比前后变化，肯定他们的进步
- 但不要做趋势分析或给规划建议"""

            if history_context:
                user_content = f"""用户最近的日记（供参考）：
{history_context}

今天的日记：
{content}

请以朋友的身份温暖地回应今天的日记。记住：只做情感支持，不要给任何学习建议或规划。"""
            else:
                user_content = f"""今天的日记：
{content}

请以朋友的身份温暖地回应这篇日记。记住：只做情感支持，不要给任何学习建议或规划。"""

        messages = [
            {"role": "system", "content": emotional_system},
            {"role": "user", "content": user_content}
        ]

        # 使用豆包模型进行情感回复
        stream = doubao_client.client.chat.completions.create(
            model=doubao_client.model,
            messages=messages,
            stream=True,
            max_tokens=500
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                emotional_response += content_chunk
                yield f"data: {json.dumps({'type': 'emotional', 'content': content_chunk}, ensure_ascii=False)}\n\n"

        # 保存情感回复到数据库
        update_diary_ai_response(diary_id, emotional_response)

        # ==================== 阶段2：目标进度分析（可选） ====================
        if enable_goal_analysis and user_id:
            goals = get_user_goals(user_id, 'active')

            if goals:
                stage_msg = 'Analyzing goal progress...' if lang == 'en-US' else '正在分析目标进度...'
                yield f"data: {json.dumps({'type': 'stage', 'stage': 'goal_analysis', 'message': stage_msg}, ensure_ascii=False)}\n\n"

                # 构建目标列表
                goals_text = "\n".join([
                    f"• {g['title']}" + (f"（{g['description']}）" if g.get('description') else "")
                    for g in goals
                ])

                # 扩展历史日记范围用于目标分析
                extended_diaries = get_recent_diaries(user_id, days=history_range, limit=30)
                extended_summaries = []
                for d in extended_diaries:
                    if d['id'] != diary_id:
                        summary = d['content'][:200] + "..." if len(d['content']) > 200 else d['content']
                        date_str = d['created_at'].strftime('%Y-%m-%d') if hasattr(d['created_at'], 'strftime') else str(d['created_at'])[:10]
                        extended_summaries.append(f"【{date_str}】{summary}")

                history_label = f"最近{history_range}天" if history_range else "全部"
                history_text = "\n\n".join(extended_summaries[:15]) if extended_summaries else "（暂无历史日记）"

                # 目标分析提示词（优化版 - 更实用的建议）
                if lang == 'en-US':
                    goal_system = """You are a practical life coach who helps users achieve their goals through diary analysis.

Your approach:
- Analyze ACTUAL behaviors and patterns from diary entries
- Give SPECIFIC, actionable suggestions (not generic advice)
- Identify trends: improving, stable, or declining
- Celebrate concrete progress, address real obstacles
- Be encouraging but honest about areas needing attention"""

                    goal_prompt = f"""User's Goals:
{goals_text}

Diary History ({history_label}):
{history_text}

Today's Entry:
{content}

For each goal, analyze:
### 🎯 [Goal Name]
**Trend**: [📈 Improving / ➡️ Stable / 📉 Needs attention]
**Evidence**: [Specific behaviors/mentions from diaries]
**Next Step**: [ONE concrete action for this week]

Keep each analysis under 80 words. Be specific, not generic."""
                else:
                    goal_system = """你是一位专业的学习规划师和成长教练。你的职责是根据用户的日记和目标，提供详细、具体、可执行的规划。

【分析框架】
对于每个目标，你需要提供：

1. **现状评估**
   - 从日记中提取用户当前的具体情况（分数、行为、习惯等）
   - 与之前的记录对比，判断趋势

2. **进度分析**
   - 📈 进步中：明确指出哪些方面在进步，进步了多少
   - ➡️ 保持中：当前状态稳定，但需要突破
   - 📉 需关注：哪些方面出现了问题，可能的原因

3. **详细规划**（这是重点！）
   - 如果用户提到了时间目标（如"1个月内"、"期末前"），必须给出分阶段计划
   - 每周的具体任务和目标
   - 每天需要做的具体事情（精确到时间/题目数量）
   - 里程碑节点和检验标准

4. **执行建议**
   - 优先级排序：先做什么，后做什么
   - 可能遇到的困难和应对方法
   - 需要的资源或帮助

【输出格式】
使用Markdown格式，包含：
- 清晰的标题层级（##、###）
- 重点内容加粗
- 适当使用列表和表格
- 时间规划用表格呈现更清晰

【回复长度】
不限字数！根据用户需求充分展开。如果用户需要详细规划，就给出完整的周计划甚至日计划。质量比简洁更重要。"""

                    goal_prompt = f"""【用户的目标】
{goals_text}

【历史日记（{history_label}）】
{history_text}

【今天的日记】
{content}

请对每个目标进行详细分析和规划。

特别注意：
1. 如果用户在日记中提到了具体的时间目标（如"1个月内达到XX"、"下次考试要XX"），请务必给出详细的分阶段执行计划，包括每周目标和每日任务
2. 从日记中提取具体数据（如分数、进步幅度）来支撑你的分析
3. 给出的建议要具体可执行，不要泛泛而谈"""

                messages = [
                    {"role": "system", "content": goal_system},
                    {"role": "user", "content": goal_prompt}
                ]

                # 使用豆包模型进行目标分析
                stream = doubao_client.client.chat.completions.create(
                    model=doubao_client.model,
                    messages=messages,
                    stream=True
                )

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content_chunk = chunk.choices[0].delta.content
                        goal_analysis_response += content_chunk
                        yield f"data: {json.dumps({'type': 'goal_analysis', 'content': content_chunk}, ensure_ascii=False)}\n\n"

                # 保存目标分析到数据库
                update_diary_goal_analysis(diary_id, goal_analysis_response)

        # ==================== 完成 ====================
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        # 保存到session文件
        response_data = {
            'emotional_response': emotional_response,
            'goal_analysis_response': goal_analysis_response if goal_analysis_response else None,
            'ai_response': emotional_response,  # 兼容旧版
            'completed_at': str(datetime.now())
        }
        with open(f'../data/sessions/{session_id}_response.json', 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Diary AI response error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


# ==================== 追问对话API ====================
@app.route('/api/chat/followup', methods=['POST'])
def chat_followup():
    """追问对话API - 流式响应"""
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')
    history = data.get('history', [])

    if not session_id or not message:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400

    def generate():
        try:
            # 读取原始会话数据
            session_file = f'../data/sessions/{session_id}.json'
            response_file = f'../data/sessions/{session_id}_response.json'

            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 读取原始答案
            original_answer = ''
            try:
                with open(response_file, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                    original_answer = response_data.get('answer', '')
            except FileNotFoundError:
                pass

            subject = session_data.get('subject', 'physics')
            question = session_data.get('question', '')

            # 构建系统提示词
            subject_name = '物理' if subject == 'physics' else '化学'
            system_prompt = f"""你是一位专业的{subject_name}老师，正在帮助学生解答问题。

【背景信息】
学生之前提出了一个问题，你已经给出了详细解答。现在学生有进一步的疑问。

【原始问题】
{question[:1000]}

【你之前的解答】
{original_answer[:2000]}

【当前任务】
请基于以上背景，回答学生的追问。要求：
1. 保持与之前解答的一致性
2. 如果追问涉及之前解答中的内容，直接引用
3. 如果是新问题，正常解答
4. 语言简洁清晰，适合学生理解
5. 如果涉及公式，使用LaTeX格式"""

            messages = [{"role": "system", "content": system_prompt}]

            # 添加历史对话（最近10轮）
            for h in history[-10:]:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

            # 添加当前追问
            messages.append({"role": "user", "content": message})

            # 调用豆包API流式返回
            stream = doubao_client.client.chat.completions.create(
                model=doubao_client.model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Follow-up chat error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

if __name__ == '__main__':
    # 初始化数据库
    try:
        init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    # 生产环境通过环境变量控制 debug 模式
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)