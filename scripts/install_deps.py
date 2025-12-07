import subprocess
import sys

def install_requirements():
    """安装必要的依赖包"""
    packages = [
        'openai==1.14.3',
        'python-dotenv==1.0.0',
        'Flask==2.3.3',
        'Flask-CORS==4.0.0'
    ]

    print("正在安装必要的Python包...")
    print("-" * 60)

    for package in packages:
        print(f"安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安装失败: {e}")

    print("\n安装完成！现在可以运行测试了。")

if __name__ == "__main__":
    install_requirements()