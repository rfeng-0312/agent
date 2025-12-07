#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本 - 自动清理临时测试文件和过期的日志
作者: 项目维护工具
版本: 1.0.0
"""

import os
import sys
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class ProjectCleaner:
    def __init__(self, project_root=None):
        """初始化清理器"""
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        # 定义需要清理的目录
        self.temp_dirs = [
            self.project_root / ".claude" / "tests" / "temporary",
            self.project_root / "data" / "logs",
            self.project_root / "data" / "sessions" / "temp",
        ]

        # 文件保留时间（小时）
        self.retain_hours = {
            "test_files": 24,      # 测试文件保留24小时
            "logs": 168,           # 日志保留7天
            "sessions": 24,        # 临时会话保留24小时
        }

        self.cleaned_files = []
        self.cleaned_dirs = []
        self.errors = []

    def clean_temp_files(self):
        """清理临时测试文件"""
        print("🧹 开始清理临时测试文件...")

        temp_dir = self.project_root / ".claude" / "tests" / "temporary"
        if not temp_dir.exists():
            print("✓ 临时测试目录不存在，跳过")
            return

        cutoff_time = time.time() - (self.retain_hours["test_files"] * 3600)

        for file_path in temp_dir.glob("test_*.py"):
            try:
                if file_path.stat().st_mtime < cutoff_time:
                    # 检查是否是测试文件（包含自删除代码）
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "cleanup_test_file" in content or "自删除" in content:
                            os.remove(file_path)
                            self.cleaned_files.append(str(file_path))
                            print(f"  ✓ 已删除: {file_path.name}")
            except Exception as e:
                self.errors.append(f"删除文件失败 {file_path}: {e}")

    def clean_old_logs(self):
        """清理过期日志"""
        print("\n📋 开始清理过期日志...")

        log_dir = self.project_root / "data" / "logs"
        if not log_dir.exists():
            print("✓ 日志目录不存在，跳过")
            return

        cutoff_time = time.time() - (self.retain_hours["logs"] * 3600)

        for log_file in log_dir.glob("*.log"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    os.remove(log_file)
                    self.cleaned_files.append(str(log_file))
                    print(f"  ✓ 已删除日志: {log_file.name}")
            except Exception as e:
                self.errors.append(f"删除日志失败 {log_file}: {e}")

    def clean_temp_sessions(self):
        """清理临时会话数据"""
        print("\n🗂️ 开始清理临时会话...")

        session_dir = self.project_root / "data" / "sessions" / "temp"
        if not session_dir.exists():
            print("✓ 临时会话目录不存在，跳过")
            return

        cutoff_time = time.time() - (self.retain_hours["sessions"] * 3600)

        for session_file in session_dir.glob("*"):
            try:
                if session_file.stat().st_mtime < cutoff_time:
                    if session_file.is_file():
                        os.remove(session_file)
                    else:
                        shutil.rmtree(session_file)
                    self.cleaned_files.append(str(session_file))
                    print(f"  ✓ 已删除: {session_file.name}")
            except Exception as e:
                self.errors.append(f"删除会话失败 {session_file}: {e}")

    def clean_empty_dirs(self):
        """清理空目录"""
        print("\n📁 清理空目录...")

        def remove_empty_dirs(path):
            """递归删除空目录"""
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        remove_empty_dirs(item)

                # 尝试删除空目录
                if path != self.project_root and not any(path.iterdir()):
                    path.rmdir()
                    self.cleaned_dirs.append(str(path))
                    print(f"  ✓ 已删除空目录: {path.relative_to(self.project_root)}")
            except:
                pass  # 目录不为空或其他错误

        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                remove_empty_dirs(temp_dir)

    def clean_python_cache(self):
        """清理Python缓存文件"""
        print("\n🐍 清理Python缓存...")

        cache_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
        ]

        for pattern in cache_patterns:
            for item in self.project_root.glob(pattern):
                try:
                    if item.is_file():
                        os.remove(item)
                        self.cleaned_files.append(str(item))
                    elif item.is_dir():
                        shutil.rmtree(item)
                        self.cleaned_dirs.append(str(item))
                except Exception as e:
                    self.errors.append(f"清理缓存失败 {item}: {e}")

        print("  ✓ Python缓存清理完成")

    def generate_report(self):
        """生成清理报告"""
        print("\n" + "="*60)
        print("📊 清理报告")
        print("="*60)

        print(f"\n清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if self.cleaned_files:
            print(f"\n✅ 已清理文件数量: {len(self.cleaned_files)}")
            print("文件列表:")
            for file in self.cleaned_files[:10]:  # 只显示前10个
                print(f"  - {Path(file).relative_to(self.project_root)}")
            if len(self.cleaned_files) > 10:
                print(f"  ... 还有 {len(self.cleaned_files) - 10} 个文件")
        else:
            print("\n✅ 没有需要清理的文件")

        if self.cleaned_dirs:
            print(f"\n✅ 已清理目录数量: {len(self.cleaned_dirs)}")
            for dir in self.cleaned_dirs:
                print(f"  - {Path(dir).relative_to(self.project_root)}")

        if self.errors:
            print(f"\n❌ 清理错误数量: {len(self.errors)}")
            for error in self.errors[:5]:  # 只显示前5个错误
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... 还有 {len(self.errors) - 5} 个错误")

        # 保存报告到文件
        report_file = self.project_root / ".claude" / "cleanup_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"清理报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(f"已清理文件: {len(self.cleaned_files)}\n")
            f.write(f"已清理目录: {len(self.cleaned_dirs)}\n")
            f.write(f"错误数量: {len(self.errors)}\n\n")

            if self.errors:
                f.write("错误详情:\n")
                for error in self.errors:
                    f.write(f"- {error}\n")

        print(f"\n📄 详细报告已保存到: {report_file}")

    def run(self, clean_cache=False):
        """执行清理"""
        print("🚀 开始项目清理...")
        print(f"项目路径: {self.project_root}")
        print("-"*60)

        self.clean_temp_files()
        self.clean_old_logs()
        self.clean_temp_sessions()
        self.clean_empty_dirs()

        if clean_cache:
            self.clean_python_cache()

        self.generate_report()

        print("\n✨ 清理完成！")

        return len(self.cleaned_files) + len(self.cleaned_dirs)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="项目清理工具")
    parser.add_argument("--cache", action="store_true", help="同时清理Python缓存")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要清理的文件")

    args = parser.parse_args()

    cleaner = ProjectCleaner()

    if args.dry_run:
        print("🔍 预览模式 - 仅显示将要清理的文件")
        # TODO: 实现预览功能
        return

    try:
        count = cleaner.run(clean_cache=args.cache)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️ 清理被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 清理过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()