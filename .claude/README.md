# .claude 目录说明

这是名侦探作业帮项目的辅助配置和工具目录，用于管理项目规范、自动化脚本和测试文件。

## 📁 目录结构

```
.claude/
├── README.md                    # 本说明文件
├── rules/                       # 项目规范文档
│   └── file-organization.md     # 文件组织规则
├── scripts/                     # 自动化脚本
│   ├── cleanup.py              # 项目清理脚本
│   └── validate.py             # 文件结构验证脚本
└── templates/                   # 模板文件
    └── test-template.py         # 测试代码模板
```

## 🚀 快速使用

### 1. 验证项目结构
检查项目是否符合文件组织规范：
```bash
python .claude/scripts/validate.py
```

### 2. 清理临时文件
自动清理临时测试文件和过期日志：
```bash
python .claude/scripts/cleanup.py
# 同时清理Python缓存
python .claude/scripts/cleanup.py --cache
```

### 3. 创建临时测试
使用模板创建新的测试文件：
```bash
cp .claude/templates/test-template.py .claude/tests/temporary/test_myfeature_$(date +%Y%m%d_%H%M%S).py
# 然后编辑测试文件，运行后会自动删除
```

## 📋 规范说明

### 文件存放原则
1. **源代码**：存放在 `src/` 目录
2. **前端资源**：存放在 `frontend/` 目录
3. **正式测试**：存放在 `tests/` 目录
4. **临时测试**：存放在 `.claude/tests/temporary/` 目录（运行后自删除）
5. **文档**：存放在 `.claude/docs/` 目录

### 测试代码管理
- 临时测试文件必须包含自删除功能
- 测试文件命名格式：`test_<功能>_<时间戳>.py`
- 测试成功运行后自动清理
- 失败的测试保留24小时后由清理脚本处理

### 自动化工具
- **validate.py**：验证项目结构是否符合规范
- **cleanup.py**：清理临时文件和过期数据
- 测试模板：提供带自删除功能的测试代码模板

## 🛠️ 开发建议

1. **编写测试时**：
   - 使用提供的测试模板
   - 测试完成后检查文件是否自动删除
   - 查看测试日志：`.claude/tests/test_logs.json`

2. **提交代码前**：
   - 运行 `validate.py` 检查项目结构
   - 运行 `cleanup.py` 清理临时文件
   - 确保没有敏感信息提交

3. **定期维护**：
   - 每周运行一次完整清理
   - 检查并更新文档
   - 审查并优化自动化脚本

## ⚡ 快捷命令

创建alias或快捷方式：
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias validate-project='python .claude/scripts/validate.py'
alias clean-project='python .claude/scripts/cleanup.py'
```

## 📞 支持

如有问题或建议，请：
1. 查看规范文档：`.claude/rules/file-organization.md`
2. 运行验证脚本检查项目状态
3. 查看清理报告：`.claude/cleanup_report.txt`

---
最后更新：2025-12-06
版本：1.0.0