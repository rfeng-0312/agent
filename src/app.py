from flask import Flask, request, jsonify, render_template, Response, session
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
from prompts import get_subject_prompt, get_competition_prompt, get_verification_prompt
from doubao_api import DoubaoClient

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

# Initialize OpenAI client for DeepSeek
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
)

# Get model name from environment
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')

# Initialize Doubao client for image queries
doubao_client = DoubaoClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

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
        session_data = {
            'question': question,
            'subject': subject,
            'deep_think': deep_think,  # 存储深度思考标记
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

            # Save session data with image path
            session_data = {
                'question': question,
                'subject': subject,
                'deep_think': deep_think,  # 存储深度思考标记
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

            question = session_data['question']
            subject = session_data['subject']
            query_type = session_data.get('type', 'text')
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
            system_prompt = get_subject_prompt(subject)

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

    # 获取竞赛级提示词
    competition_prompt = get_competition_prompt(subject)

    solve_thinking = ""
    solve_answer = ""
    verify_thinking = ""
    verify_answer = ""

    try:
        # ==================== 阶段1：解答问题 ====================
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'solving', 'message': '正在深度分析问题...'}, ensure_ascii=False)}\n\n"

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
        yield f"data: {json.dumps({'type': 'stage', 'stage': 'verifying', 'message': '正在验证答案...'}, ensure_ascii=False)}\n\n"

        # 构造验证提示词
        verification_prompt = get_verification_prompt(subject, question, solve_answer)

        if query_type == 'image_deep':
            # 图片问题：使用DeepSeek验证（交叉验证）
            logger.info(f"Deep think image query - Stage 2: DeepSeek verifying")

            messages = [
                {"role": "system", "content": "你是一位严谨的理科审稿专家，请独立验证解答的正确性。"},
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)