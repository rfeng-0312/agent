#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文件结构验证脚本
验证项目是否符合文件组织规范
作者: 项目维护工具
版本: 1.0.0
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict

class ProjectValidator:
    def __init__(self, project_root=None):
        """初始化验证器"""
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        self.errors = []
        self.warnings = []
        self.success_count = 0

        # 必需的文件和目录
        self.required_structure = {
            "files": [
                "README.md",
                "requirements.txt",
                ".gitignore",
                ".env.example",
            ],
            "directories": [
                "src",
                "frontend",
                "data",
                "tests",
                ".claude",
            ],
        }

        # .claude目录下必需的结构
        self.claude_structure = {
            "files": [
                ".claude/rules/file-organization.md",
            ],
            "directories": [
                ".claude/rules",
                ".claude/tests",
                ".claude/docs",
                ".claude/scripts",
                ".claude/templates",
            ],
        }

        # src目录下必需的文件
        self.src_structure = {
            "files": [
                "src/app.py",
                "src/prompts.py",
                "src/.env",
            ],
        }

        # frontend目录结构
        self.frontend_structure = {
            "directories": [
                "frontend/templates",
                "frontend/static",
                "frontend/static/css",
                "frontend/static/js",
                "frontend/static/images",
            ],
            "files": [
                "frontend/templates/index.html",
                "frontend/static/css/styles.css",
                "frontend/static/js/script.js",
            ],
        }

    def check_file_exists(self, file_path: Path, description: str) -> bool:
        """检查文件是否存在"""
        if file_path.exists():
            print(f"  ✓ {description}")
            self.success_count += 1
            return True
        else:
            print(f"  ✗ {description} - 文件不存在: {file_path}")
            self.errors.append(f"缺少必需文件: {file_path}")
            return False

    def check_directory_exists(self, dir_path: Path, description: str) -> bool:
        """检查目录是否存在"""
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {description}")
            self.success_count += 1
            return True
        else:
            print(f"  ✗ {description} - 目录不存在: {dir_path}")
            self.errors.append(f"缺少必需目录: {dir_path}")
            return False

    def validate_root_structure(self):
        """验证项目根目录结构"""
        print("\n📁 验证项目根目录结构...")
        print("-" * 40)

        # 检查必需文件
        for file_name in self.required_structure["files"]:
            file_path = self.project_root / file_name
            self.check_file_exists(file_path, f"根目录文件: {file_name}")

        # 检查必需目录
        for dir_name in self.required_structure["directories"]:
            dir_path = self.project_root / dir_name
            self.check_directory_exists(dir_path, f"根目录: {dir_name}/")

    def validate_claude_structure(self):
        """验证.claude目录结构"""
        print("\n🔧 验证.claude目录结构...")
        print("-" * 40)

        claude_dir = self.project_root / ".claude"

        # 检查.claude目录存在
        if not claude_dir.exists():
            self.errors.append(".claude目录不存在")
            return

        # 检查必需文件
        for file_path in self.claude_structure["files"]:
            full_path = self.project_root / file_path
            self.check_file_exists(full_path, f".claude配置: {Path(file_path).name}")

        # 检查必需目录
        for dir_path in self.claude_structure["directories"]:
            full_path = self.project_root / dir_path
            self.check_directory_exists(full_path, f".claude目录: {Path(dir_path).name}")

    def validate_src_structure(self):
        """验证src目录结构"""
        print("\n💻 验证源代码目录结构...")
        print("-" * 40)

        src_dir = self.project_root / "src"

        # 检查src目录存在
        if not src_dir.exists():
            self.errors.append("src目录不存在")
            return

        # 检查必需文件
        for file_path in self.src_structure["files"]:
            full_path = self.project_root / file_path
            self.check_file_exists(full_path, f"源代码: {Path(file_path).name}")

        # 检查是否有临时测试文件需要清理
        temp_test_files = list(src_dir.glob("test_*.py"))
        if temp_test_files:
            print(f"  ⚠️ 发现 {len(temp_test_files)} 个临时测试文件在src目录中")
            for test_file in temp_test_files:
                self.warnings.append(f"src目录中不应有测试文件: {test_file}")

    def validate_frontend_structure(self):
        """验证frontend目录结构"""
        print("\n🎨 验证前端目录结构...")
        print("-" * 40)

        frontend_dir = self.project_root / "frontend"

        # 检查frontend目录存在
        if not frontend_dir.exists():
            self.errors.append("frontend目录不存在")
            return

        # 检查必需目录
        for dir_path in self.frontend_structure["directories"]:
            full_path = self.project_root / dir_path
            self.check_directory_exists(full_path, f"前端目录: {Path(dir_path).name}")

        # 检查必需文件
        for file_path in self.frontend_structure["files"]:
            full_path = self.project_root / file_path
            self.check_file_exists(full_path, f"前端文件: {Path(file_path).name}")

        # 检查静态文件引用是否正确
        index_html = self.project_root / "frontend/templates/index.html"
        if index_html.exists():
            with open(index_html, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'url_for(\'static\', filename=\'styles.css\'')' in content:
                    self.warnings.append("index.html中的静态文件路径可能需要更新（缺少子目录）")

    def validate_data_structure(self):
        """验证data目录结构"""
        print("\n📊 验证数据目录结构...")
        print("-" * 40)

        data_dir = self.project_root / "data"

        if data_dir.exists():
            # 检查必需的子目录
            required_subdirs = ["uploads", "sessions", "logs"]
            for subdir in required_subdirs:
                subdir_path = data_dir / subdir
                self.check_directory_exists(subdir_path, f"数据目录: data/{subdir}/")
        else:
            self.warnings.append("data目录不存在（运行时会自动创建）")

    def validate_file_permissions(self):
        """验证文件权限"""
        print("\n🔐 验证文件权限...")
        print("-" * 40)

        # 检查.env文件权限
        env_file = self.project_root / "src" / ".env"
        if env_file.exists():
            # 在Windows上检查是否为只读
            try:
                with open(env_file, 'a') as f:
                    pass
                print("  ✓ .env文件可写")
                self.success_count += 1
            except:
                self.errors.append(".env文件权限不正确（应为可写）")

        # 检查脚本文件是否可执行（在Unix系统上）
        if os.name != 'nt':  # 非Windows系统
            script_files = [
                "deploy.sh",
                ".claude/scripts/cleanup.py",
                ".claude/scripts/validate.py",
            ]
            for script in script_files:
                script_path = self.project_root / script
                if script_path.exists():
                    if os.access(script_path, os.X_OK):
                        print(f"  ✓ {script} 可执行")
                        self.success_count += 1
                    else:
                        self.warnings.append(f"{script} 不可执行")

    def validate_temp_files(self):
        """检查临时文件"""
        print("\n🧹 检查临时文件...")
        print("-" * 40)

        # 检查Python缓存
        cache_count = 0
        for cache in self.project_root.rglob("__pycache__"):
            cache_count += 1
        if cache_count > 0:
            self.warnings.append(f"发现 {cache_count} 个__pycache__目录")

        pyc_count = len(list(self.project_root.rglob("*.pyc")))
        if pyc_count > 0:
            self.warnings.append(f"发现 {pyc_count} 个.pyc文件")

        if cache_count == 0 and pyc_count == 0:
            print("  ✓ 没有Python缓存文件")
            self.success_count += 1

        # 检查临时测试文件
        temp_tests = list(self.project_root.glob("**/test_*.py"))
        if temp_tests:
            print(f"  ⚠️ 发现 {len(temp_tests)} 个临时测试文件")
            for test in temp_tests:
                self.warnings.append(f"临时测试文件未清理: {test.relative_to(self.project_root)}")
        else:
            print("  ✓ 没有临时测试文件")
            self.success_count += 1

    def generate_report(self) -> bool:
        """生成验证报告"""
        print("\n" + "="*60)
        print("📋 验证报告")
        print("="*60)

        print(f"\n✅ 验证通过项目: {self.success_count}")

        if self.warnings:
            print(f"\n⚠️ 警告数量: {len(self.warnings)}")
            print("警告详情:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print(f"\n❌ 错误数量: {len(self.errors)}")
            print("错误详情:")
            for error in self.errors:
                print(f"  - {error}")

        print("\n" + "="*60)

        # 返回是否验证通过
        is_valid = len(self.errors) == 0
        if is_valid:
            print("✨ 项目结构验证通过！")
        else:
            print("❌ 项目结构验证失败，请修复上述错误")

        # 保存报告
        report_file = self.project_root / ".claude" / "validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"验证报告 - {Path(__file__).name}\n")
            f.write("="*60 + "\n\n")
            f.write(f"验证通过: {self.success_count}\n")
            f.write(f"警告数量: {len(self.warnings)}\n")
            f.write(f"错误数量: {len(self.errors)}\n\n")

            if self.warnings:
                f.write("警告:\n")
                for warning in self.warnings:
                    f.write(f"- {warning}\n\n")

            if self.errors:
                f.write("错误:\n")
                for error in self.errors:
                    f.write(f"- {error}\n\n")

        return is_valid

    def run(self) -> bool:
        """执行完整验证"""
        print("🔍 开始验证项目文件结构...")
        print(f"项目路径: {self.project_root}")
        print("="*60)

        self.validate_root_structure()
        self.validate_claude_structure()
        self.validate_src_structure()
        self.validate_frontend_structure()
        self.validate_data_structure()
        self.validate_file_permissions()
        self.validate_temp_files()

        return self.generate_report()

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="项目结构验证工具")
    parser.add_argument("--fix", action="store_true", help="尝试修复部分问题")
    parser.add_argument("--path", help="指定项目路径（默认为当前目录）")

    args = parser.parse_args()

    validator = ProjectValidator(args.path)

    try:
        is_valid = validator.run()
        sys.exit(0 if is_valid else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()