# 🔄 代码工作流程示例

## 1. 用户提交流程（代码流程）

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as 前端JavaScript
    participant Backend as Flask后端
    participant DeepSeek as DeepSeek API

    User->>Frontend: 1. 输入问题
    User->>Frontend: 2. 点击"开始解题"

    Frontend->>Frontend: 3. handleQuestionSubmit()
        Note right of Frontend:
        - 获取输入框内容: document.getElementById('problemInput').value
        - 获取选中的科目: physics 或 chemistry

    Frontend->>Backend: 4. POST /api/query/text
        Note right of Frontend:
        fetch('/api/query/text', {
            method: 'POST',
            body: JSON.stringify({
                question: "问题内容",
                subject: "physics"
            })
        })

    Backend->>Backend: 5. 处理请求
        Note right of Backend:
        - 接收JSON数据
        - 生成session_id
        - 保存问题到sessions/目录

    Backend->>Frontend: 6. 返回session_id
        Note right of Backend:
        jsonify({
            session_id: "20251206153000123",
            redirect_url: "/result/20251206153000123"
        })

    Frontend->>Frontend: 7. 跳转到结果页
        Note right of Frontend:
        window.location.href = redirect_url

    Frontend->>Backend: 8. GET /result/session_id

    Backend->>Frontend: 9. 返回result.html页面

    Frontend->>Backend: 10. 建立SSE连接
        Note right of Frontend:
        new EventSource('/api/stream/session_id')

    Backend->>DeepSeek: 11. 调用DeepSeek API
        Note right of Backend:
        client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[...],
            stream=True
        )

    DeepSeek-->>Backend: 12. 流式返回数据
        Note right of DeepSeek:
        - 思考过程 (reasoning_content)
        - 最终答案 (content)

    Backend-->>Frontend: 13. SSE推送数据
        Note right of Backend:
        yield f"data: {{'type': 'thinking', 'content': '...' }}"
        yield f"data: {{'type': 'answer', 'content': '...' }}"

    Frontend->>Frontend: 14. 实时显示内容
        Note right of Frontend:
        - 更新思考过程区域
        - 打字机效果显示答案
```

## 2. 核心代码示例解析

### 前端：获取用户输入

```javascript
// static/script.js - 第216行
async function handleQuestionSubmit() {
    // 1. 获取用户输入的问题
    const questionText = document.getElementById('problemInput').value.trim();

    // 2. 获取当前选中的科目
    const currentSubject = document.querySelector('.tab-btn.tab-active-phy')
        ? 'physics'
        : 'chemistry';

    // 3. 验证输入
    if (!questionText) {
        alert('请输入问题！');
        return;
    }

    // 4. 发送请求到后端
    const response = await fetch('/api/query/text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            question: questionText,
            subject: currentSubject
        })
    });

    // 5. 处理响应
    const data = await response.json();
    window.location.href = data.redirect_url;
}
```

### 后端：Flask路由处理

```python
# app.py - 第44行
@app.route('/api/query/text', methods=['POST'])
def handle_text_query():
    # 1. 获取请求数据
    data = request.get_json()
    question = data['question']
    subject = data['subject']

    # 2. 生成唯一的会话ID
    session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')

    # 3. 保存会话数据（临时）
    session_data = {
        'question': question,
        'subject': subject,
        'timestamp': str(datetime.now())
    }

    # 4. 创建会话文件
    with open(f'sessions/{session_id}.json', 'w') as f:
        json.dump(session_data, f)

    # 5. 返回响应给前端
    return jsonify({
        'session_id': session_id,
        'redirect_url': f'/result/{session_id}'
    })
```

### 流式响应处理

```python
# app.py - 第178行
@app.route('/api/stream/<session_id>', methods=['GET'])
def stream_response(session_id):
    # 1. 加载会话数据
    with open(f'sessions/{session_id}.json', 'r') as f:
        session_data = json.load(f)

    # 2. 构建消息
    messages = [
        {"role": "system", "content": get_subject_prompt(session_data['subject'])},
        {"role": "user", "content": session_data['question']}
    ]

    # 3. 调用DeepSeek API（流式）
    stream = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=True,
        extra_body={"thinking": {"type": "enabled"}}
    )

    # 4. 流式返回数据
    def generate():
        for chunk in stream:
            if chunk.reasoning_content:
                yield f"data: {json.dumps({'type': 'thinking', 'content': chunk.reasoning_content})}\n\n"
            if chunk.content:
                yield f"data: {json.dumps({'type': 'answer', 'content': chunk.content})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
```

## 3. 数据结构说明

### 请求数据格式

```json
// POST /api/query/text
{
    "question": "一个物体从10米高自由落体...",
    "subject": "physics"  // 或 "chemistry"
}
```

### 响应数据格式

```json
// API响应
{
    "status": "success",
    "session_id": "20251206153000123",
    "redirect_url": "/result/20251206153000123"
}

// SSE流式数据
data: {"type": "thinking", "content": "用户问的是自由落体问题..."}
data: {"type": "thinking", "content": "需要使用运动学公式..."}
data: {"type": "answer", "content": "根据自由落体公式..."}
data: {"type": "answer", "content": "落地时间为1.41秒..."}
data: {"type": "done"}
```

## 4. 关键概念解释

### EventSource (Server-Sent Events)
```javascript
// 创建连接
const eventSource = new EventSource('/api/stream/session_id');

// 监听消息
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === 'thinking') {
        // 显示思考过程
        document.getElementById('thinkingText').textContent += data.content;
    } else if (data.type === 'answer') {
        // 显示答案
        document.getElementById('answerText').textContent += data.content;
    }
};
```

### Flask路由装饰器
```python
# 装饰器告诉Flask这个函数处理哪个URL的请求
@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return "Hello, World!"
    else:  # POST
        name = request.form.get('name')
        return f"Hello, {name}!"
```

### CORS (跨域资源共享)
```python
# 允许前端跨域请求
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求
```

## 5. 调试技巧

### 前端调试
```javascript
// 在浏览器控制台查看
console.log(questionText);  // 查看输入的问题
console.log(currentSubject);  // 查看选中的科目
console.log(response);  // 查看API响应

// 使用debugger语句
debugger;  // 代码会在此处暂停，方便调试
```

### 后端调试
```python
# 打印调试信息
print(f"接收到问题: {question}")
print(f"科目: {subject}")

# 使用Flask调试模式
app.run(debug=True)  # 显示详细错误信息
```

## 6. 常见问题解决

### 问题1：按钮点击没反应
```javascript
// 确保ID正确
const button = document.getElementById('submitBtn');
if (button) {
    button.addEventListener('click', handleClick);
}
```

### 问题2：API请求失败
```javascript
// 添加错误处理
try {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
} catch (error) {
    console.error('请求失败:', error);
    alert('请求失败，请重试');
}
```

### 问题3：中文乱码
```python
# 确保编码正确
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
```

## 7. 学习建议

1. **先理解流程**：从用户点击到看到答案的完整流程
2. **逐步调试**：使用console.log和print跟踪数据流
3. **阅读文档**：Flask、JavaScript、Fetch API的官方文档
4. **实践修改**：尝试添加新功能，比如：
   - 添加历史记录
   - 支持更多科目
   - 优化UI动画
5. **代码复用**：理解函数如何被调用和复用