# 名侦探作业帮 - AI解题助手

一个基于Flask后端和现代前端的教育工具，支持物理和化学问题的智能解答。

## 功能特性

- 🎯 **双模式支持**: 物理（蓝色主题）和化学（红色主题）
- 🤖 **AI智能解答**:
  - 纯文本问题使用DeepSeek API
  - 图片问题使用ChatGLM API
- 🖼️ **图片识别**: 支持上传图片进行问题解析
- 🎨 **精美UI**: Detective Conan主题，炫酷动画效果
- 📱 **响应式设计**: 支持手机、平板和桌面设备

## 技术栈

### 后端
- **Flask**: Web框架
- **Flask-CORS**: 跨域请求支持
- **Python**: 后端编程语言

### 前端
- **HTML5**: 页面结构
- **Tailwind CSS**: 样式框架（通过CDN）
- **Vanilla JavaScript**: 前端交互逻辑
- **Font Awesome**: 图标库

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动

### 3. 访问应用

在浏览器中打开 `http://localhost:5000`

## 项目结构

```
new_agent/
├── app.py              # Flask主应用
├── requirements.txt    # Python依赖
├── uploads/           # 图片上传目录
├── static/            # 静态文件
│   ├── styles.css     # 自定义样式
│   ├── script.js      # 前端JavaScript
│   └── *.jpg          # 图片资源
├── templates/         # HTML模板
│   └── test.html      # 主页面
└── CLAUDE.md         # Claude AI开发指南
```

## API接口

### 文本问题接口
- **URL**: `/api/query/text`
- **方法**: POST
- **请求体**:
  ```json
  {
    "question": "你的问题",
    "subject": "physics" 或 "chemistry"
  }
  ```

### 图片问题接口
- **URL**: `/api/query/image`
- **方法**: POST
- **请求体**: FormData
  - `image`: 图片文件
  - `question`: 文字问题（可选）
  - `subject`: 学科

### Base64图片接口
- **URL**: `/api/query/base64`
- **方法**: POST
- **请求体**:
  ```json
  {
    "image": "base64编码的图片",
    "question": "文字问题",
    "subject": "physics" 或 "chemistry"
  }
  ```

## 使用说明

1. **选择学科**: 点击顶部导航栏的"物理"或"化学"标签
2. **输入问题**: 在文本框中输入你的问题
3. **上传图片**: 如有图片，点击上传按钮选择图片
4. **提交问题**: 点击"提交问题"按钮或使用Ctrl+Enter快捷键
5. **查看解答**: AI将自动分析问题并提供解答

## 开发说明

详细的开发指南请参考 [CLAUDE.md](CLAUDE.md)

## 注意事项

- 图片大小限制：16MB
- 支持的图片格式：PNG, JPG, JPEG, GIF, WEBP
- 后端端口：5000（可在app.py中修改）

## 贡献

欢迎提交Issues和Pull Requests来改进这个项目！

## 许可证

MIT License