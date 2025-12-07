# 🕵️ 名侦探作业帮 - AI智能解题助手

一个基于Flask后端和原生JavaScript前端的教育应用，专门用于解答物理和化学问题。

## 🎯 功能特点

- **双学科支持**：物理和化学问题解答
- **AI思考过程展示**：查看DeepSeek AI的解题思路
- **流式响应**：实时显示答案生成过程
- **图片识别**：支持上传图片进行问题解答（豆包API）
- **深度思考**：启用高级推理模式进行专业分析
- **联网搜索**：实时获取最新信息支持解答
- **精美UI设计**：Detective Conan主题，炫酷动画效果

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- pip 包管理器

### 2. 安装依赖
```bash
cd scripts
python install_all.py
```

### 3. 配置API密钥
```bash
cp config/.env.example src/.env
# 编辑 src/.env，填入你的API密钥
# 需要配置：
# - DEEPSEEK_API_KEY：DeepSeek API密钥（文本问题）
# - DOUBAO_API_KEY：豆包API密钥（图片问题）
```

### 4. 启动应用
```bash
# 方式1：使用启动脚本
python start.py

# 方式2：手动启动
cd src
python app.py
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## 📁 项目结构

```
detective-study-helper/
├── src/                    # 源代码
│   ├── app.py             # Flask主应用
│   ├── prompts.py         # Prompt模板
│   └── .env               # 环境变量配置（需手动创建）
├── frontend/              # 前端资源
│   ├── static/            # CSS, JS, 图片
│   │   ├── css/           # 样式文件
│   │   ├── js/            # JavaScript文件
│   │   └── images/        # 图片资源
│   └── templates/         # HTML模板
│       └── index.html     # 主页面
├── tests/                 # 正式测试文件
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── e2e/               # 端到端测试
├── .claude/               # 项目管理和工具
│   ├── rules/             # 项目规范文档
│   ├── scripts/           # 自动化脚本
│   │   ├── cleanup.py     # 项目清理脚本
│   │   └── validate.py    # 文件结构验证脚本
│   ├── templates/         # 模板文件
│   └── tests/temporary/   # 临时测试文件（自动清理）
├── data/                  # 运行时数据
│   ├── uploads/           # 用户上传文件
│   ├── sessions/          # 会话数据
│   └── logs/              # 日志文件
├── config/                # 配置文件
│   └── .env.example       # 环境变量模板
├── start.py               # 快速启动脚本
├── scripts/               # 工具脚本
│   ├── install_all.py     # 一键安装依赖
│   ├── install_deps.py    # 安装Python依赖
│   └── 启动项目.bat      # Windows启动脚本
├── requirements.txt       # Python依赖
└── .gitignore            # Git忽略规则
```

## 📚 文档

- [项目架构详解](docs/architecture/PROJECT_ARCHITECTURE.md)
- [API文档](docs/API/deepseekAPI.md)
- [豆包API集成](.claude/docs/api/doubao-api-integration.md) - 图片处理API集成
- [.claude 目录说明](.claude/README.md) - 项目管理和自动化工具
- [文件组织规则](.claude/rules/file-organization.md) - 文件存放规范

## 🛠️ 项目管理

### 验证项目结构
检查项目是否符合文件组织规范：
```bash
python .claude/scripts/validate.py
```

### 清理临时文件
自动清理临时测试文件和过期日志：
```bash
python .claude/scripts/cleanup.py
```

### 创建临时测试
使用模板创建测试文件（运行后自动删除）：
```bash
cp .claude/templates/test-template.py .claude/tests/temporary/test_myfeature_$(date +%Y%m%d_%H%M%S).py
```

## 🛠️ 开发

### 运行测试
```bash
cd tests/api
python test_deepseek_simple.py
```

### 项目重组
查看 [重组计划](PROJECT_REORGANIZATION.md) 了解最新的项目结构。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！