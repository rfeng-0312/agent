# 🚀 快速启动指南

## 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 2. 配置环境变量

1. 复制环境变量模板文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 DeepSeek API 密钥：
```
DEEPSEEK_API_KEY=your_actual_api_key_here
```

## 3. 启动应用

```bash
python app.py
```

应用将在 http://localhost:5000 启动

## 4. 使用说明

1. **输入问题**：在首页输入物理或化学问题
2. **选择科目**：点击顶部的"物理"或"化学"标签
3. **提交问题**：点击"提交问题"按钮
4. **查看解答**：系统将自动跳转到结果页面，展示AI的思考过程和最终答案

## 功能特点

- ✨ **AI思考过程展示**：查看AI的解题思路
- 🔄 **流式回答**：实时显示AI的回答内容
- 📚 **科目专用Prompt**：针对物理和化学优化了解答方式
- 🎯 **DeepSeek Reasoner模型**：使用最新的大语言模型

## 故障排除

1. **API密钥错误**：确保 `.env` 文件中的 `DEEPSEEK_API_KEY` 正确
2. **端口占用**：如果5000端口被占用，修改 `app.py` 最后一行的端口号
3. **依赖安装失败**：确保Python版本在3.8以上

## 下一步计划

- [ ] 集成ChatGLM API处理图片问题
- [ ] 添加用户登录和问题历史记录
- [ ] 支持更多文件格式上传
- [ ] 添加问题分享功能