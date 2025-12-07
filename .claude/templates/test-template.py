#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时测试文件模板 - 自动删除
测试功能：[在此填写测试功能描述]
创建时间：{timestamp}
作者：[测试作者]
预期结果：[测试通过后的预期结果]
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime

# 测试元数据
TEST_META = {
    "test_name": "test_{function}_{timestamp}",
    "created_at": datetime.now().isoformat(),
    "auto_delete": True,
    "description": "[测试描述]",
}

def log_test_result(result, details=""):
    """记录测试结果"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "test_file": __file__,
        "result": result,
        "details": details
    }

    # 保存到测试日志
    log_file = os.path.join(
        os.path.dirname(__file__),
        "..", "tests", "test_logs.json"
    )

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass  # 日志记录失败不影响测试

def cleanup_test_file():
    """测试结束后自删除"""
    try:
        # 等待一小段时间确保输出完成
        time.sleep(0.1)

        # 删除自身
        os.remove(__file__)

        # 如果所在目录为空，也删除目录
        parent_dir = os.path.dirname(__file__)
        try:
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        except:
            pass

        print(f"\n✓ 测试文件已自动删除: {os.path.basename(__file__)}")
    except Exception as e:
        print(f"\n⚠️ 自动删除失败（请手动删除）: {e}")

def setup_test_environment():
    """设置测试环境"""
    print("=" * 60)
    print("🧪 临时测试环境")
    print("=" * 60)
    print(f"测试文件: {os.path.basename(__file__)}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # 添加项目路径到sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    return project_root

def teardown_test_environment():
    """清理测试环境"""
    print("\n" + "-" * 60)
    print("🔧 清理测试环境...")

def run_test():
    """
    主测试函数 - 在这里编写你的测试代码
    """
    try:
        # ====== 在这里编写你的测试代码 ======

        # 示例1：测试Flask应用
        print("测试1: 检查Flask应用导入...")
        try:
            from app import app
            print("✓ Flask应用导入成功")

            # 测试路由
            with app.test_client() as client:
                response = client.get('/')
                assert response.status_code == 200
                print("✓ 主页路由测试通过")

        except Exception as e:
            raise AssertionError(f"Flask应用测试失败: {e}")

        # 示例2：测试API端点
        print("\n测试2: 检查API端点...")
        with app.test_client() as client:
            # 测试健康检查
            response = client.get('/health')
            assert response.status_code == 200
            print("✓ 健康检查端点正常")

        # 示例3：测试配置
        print("\n测试3: 检查配置文件...")
        import os
        env_path = os.path.join(os.path.dirname(app.root_path), '.env')
        assert os.path.exists(env_path), ".env文件不存在"
        print("✓ 配置文件检查通过")

        # ====== 测试代码结束 ======

        print("\n✅ 所有测试通过！")
        return True, "测试成功完成"

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False, str(e)

    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        traceback.print_exc()
        return False, f"测试异常: {e}"

def main():
    """主函数"""
    project_root = None
    test_success = False

    try:
        # 设置测试环境
        project_root = setup_test_environment()

        # 运行测试
        print("\n🚀 开始执行测试...\n")
        success, details = run_test()

        # 记录测试结果
        log_test_result("PASS" if success else "FAIL", details)

        test_success = success

    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        log_test_result("INTERRUPTED", "用户中断")

    except Exception as e:
        print(f"\n💥 测试环境异常: {e}")
        log_test_result("ERROR", str(e))

    finally:
        # 清理测试环境
        if project_root:
            teardown_test_environment()

        # 自动删除测试文件
        print("\n🗑️ 准备自动清理...")
        cleanup_test_file()

        # 返回适当的退出码
        sys.exit(0 if test_success else 1)

if __name__ == "__main__":
    main()