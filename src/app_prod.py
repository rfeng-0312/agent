from flask import Flask, request, jsonify, render_template, Response, session
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
import json
from openai import OpenAI
from dotenv import load_dotenv
from prompts import get_subject_prompt

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration for production
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

# File upload configuration
UPLOAD_FOLDER = '../data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenAI client for DeepSeek
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
)

# Get model name from environment
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')

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
    """
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400

        question = data['question']
        subject = data.get('subject', 'physics')  # physics or chemistry

        # Get subject-specific prompt
        system_prompt = get_subject_prompt(subject)

        # Create messages for DeepSeek API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        # Store question in session for result page
        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        session_data = {
            'question': question,
            'subject': subject,
            'timestamp': str(datetime.now())
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
    Handle image + text queries
    Will integrate with ChatGLM API later
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        question = request.form.get('question', '')
        subject = request.form.get('subject', 'physics')

        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # TODO: Integrate with ChatGLM API
            # Placeholder response
            response = {
                'status': 'success',
                'type': 'image',
                'subject': subject,
                'question': question,
                'image_path': filepath,
                'answer': f'This is a placeholder response for your {subject} image question. ChatGLM API integration coming soon.',
                'timestamp': str(datetime.now())
            }

            return jsonify(response)
        else:
            return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/base64', methods=['POST'])
def handle_base64_query():
    """
    Handle base64 encoded image queries
    Will integrate with ChatGLM API later
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image']  # Base64 string
        question = data.get('question', '')
        subject = data.get('subject', 'physics')

        # TODO: Process base64 image and integrate with ChatGLM API
        # Placeholder response
        response = {
            'status': 'success',
            'type': 'image_base64',
            'subject': subject,
            'question': question,
            'answer': f'This is a placeholder response for your {subject} base64 image question. ChatGLM API integration coming soon.',
            'timestamp': str(datetime.now())
        }

        return jsonify(response)

    except Exception as e:
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

# Streaming endpoint for DeepSeek response
@app.route('/api/stream/<session_id>', methods=['GET'])
def stream_response(session_id):
    """Stream DeepSeek response with thinking process"""

    def generate():
        try:
            # Load session data
            with open(f'../data/sessions/{session_id}.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            question = session_data['question']
            subject = session_data['subject']
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

            thinking_content = ""
            answer_content = ""

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
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

if __name__ == '__main__':
    # For development use only
    app.run(host='0.0.0.0', port=5000)