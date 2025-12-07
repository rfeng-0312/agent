# 🗂️ 项目文件夹重组计划

## 📍 当前问题分析

### 根目录文件过多
- 测试文件（test_*.py）散落在根目录
- API测试响应文件（api_response.json, *.txt）
- 部署脚本混杂
- 文档文件分散

### 建议的新文件夹结构

```
detective-study-helper/
├── 📁 src/                          # 源代码目录
│   ├── app.py                      # Flask主应用
│   ├── prompts.py                  # Prompt模板
│   ├── requirements.txt            # Python依赖
│   ├── run.py                      # 启动脚本
│   └── .env                        # 环境变量（Git忽略）
│
├── 📁 frontend/                     # 前端资源
│   ├── static/                     # 静态文件
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   │       └── 67a99ed6f3db4z2m7bdnw17636.jpg
│   └── templates/                  # HTML模板
│       ├── index.html              # 主页面（重命名为index）
│       └── result.html             # 结果页面
│
├── 📁 tests/                        # 测试文件
│   ├── api/                        # API测试
│   │   ├── test_deepseek.py
│   │   ├── test_chinese.py
│   │   ├── test_save_response.py
│   │   └── test_results/           # 测试结果
│   │       ├── api_response.json
│   │       ├── chinese_response.json
│   │       ├── answer.txt
│   │       └── thinking_process.txt
│   └── integration/                # 集成测试
│
├── 📁 scripts/                      # 部署和工具脚本
│   ├── install_all.py
│   ├── install_deps.py
│   ├── deploy.py
│   └── 启动项目.bat
│
├── 📁 docs/                         # 文档
│   ├── API/                         # API文档
│   │   └── deepseekAPI.md
│   ├── architecture/                # 架构文档
│   │   ├── PROJECT_ARCHITECTURE.md
│   │   └── WORKFLOW_EXAMPLES.md
│   ├── deployment/                  # 部署文档
│   │   └── DEPLOYMENT.md
│   └── guides/                      # 用户指南
│       ├── README.md
│       ├── SETUP.md
│       └── CLAUDE.md
│
├── 📁 data/                         # 运行时数据（Git忽略）
│   ├── uploads/
│   └── sessions/
│
├── 📁 config/                       # 配置文件
│   └── .env.example                 # 环境变量模板
│
├── .gitignore                        # Git忽略文件
├── .env.example                     # 环境变量模板（保留在根目录）
└── README.md                         # 项目说明
```

## 🎯 重组步骤

### 第1步：创建新的文件夹结构
```bash
mkdir -p src
mkdir -p frontend/static/{css,js,images}
mkdir -p frontend/templates
mkdir -p tests/{api,test_results}
mkdir -p tests/integration
mkdir -p scripts
mkdir -p docs/{API,architecture,deployment,guides}
mkdir -p data
mkdir -p config
```

### 第2步：移动核心文件
```bash
# 移动源代码
mv app.py prompts.py run.py src/
mv .env src/
mv requirements.txt src/

# 移动前端文件
mv static/* frontend/static/
mv templates/* frontend/templates/
rmdir static templates

# 移动测试文件
mv test_*.py tests/api/
mv api_response.json *.txt tests/api/test_results/

# 移动脚本
mv install*.py deploy.py 启动项目.bat scripts/

# 移动文档
mv *.md docs/
mv docs/deepseekAPI.md docs/API/
mv docs/PROJECT_ARCHITECTURE.md docs/architecture/
mv docs/WORKFLOW_EXAMPLES.md docs/architecture/
mv docs/DEPLOYMENT.md docs/deployment/
mv docs/README.md docs/guides/
mv docs/SETUP.md docs/guides/
mv docs/CLAUDE.md docs/guides/

# 移动数据目录
mv uploads sessions data/
mv .env.example config/
```

### 第3步：重命名文件（可选）
```bash
mv frontend/templates/test.html frontend/templates/index.html
```

### 第4步：更新路径引用
- 更新 app.py 中的模板和静态文件路径
- 更新文档中的相对路径引用
- 更新任何硬编码的路径

## 📝 .gitignore 配置

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv/

# 数据目录
data/
sessions/
uploads/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 测试结果
tests/api/test_results/*.json
tests/api/test_results/*.txt
!tests/api/test_results/.gitkeep

# 临时文件
*.tmp
*.bak
*~
```

## ✅ 重组后的优势

1. **清晰的结构**：代码、测试、文档、配置分离
2. **易于维护**：相关文件集中管理
3. **团队协作**：新成员能快速理解项目结构
4. **可扩展性**：便于添加新功能模块
5. **版本控制**：.gitignore排除临时文件

## 🔄 迁移注意事项

1. **路径更新**：确保所有文件引用路径正确
2. **权限保持**：移动后检查文件执行权限
3. **测试验证**：重组后确保应用正常运行
4. **备份**：重组前先备份重要文件