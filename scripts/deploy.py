#!/usr/bin/env python3
"""
名侦探作业帮 - 部署脚本
支持本地部署和云服务器部署
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(command, check=True):
    """运行命令并返回结果"""
    print(f"执行: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"错误: 命令执行失败")
        print(f"输出: {result.stderr}")
        sys.exit(1)
    return result

def check_requirements():
    """检查部署要求"""
    print("检查部署要求...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✓ Python版本: {python_version.major}.{python_version.minor}")

    # 检查pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✓ pip已安装")
    except subprocess.CalledProcessError:
        print("错误: pip未安装")
        sys.exit(1)

    # 检查环境变量文件
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', '.env')
    if not os.path.exists(env_file):
        print("警告: .env文件不存在")
        print("请确保配置了以下环境变量:")
        print("- DEEPSEEK_API_KEY")
        print("- DOUBAO_API_KEY")
        print("- SECRET_KEY")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✓ 环境变量文件存在")

def install_dependencies():
    """安装依赖"""
    print("\n安装Python依赖...")
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'requirements.txt')
    if os.path.exists(requirements_file):
        run_command(f"{sys.executable} -m pip install -r {requirements_file}")
        print("✓ 依赖安装完成")
    else:
        print("警告: requirements.txt不存在，跳过依赖安装")

def create_directories():
    """创建必要的目录"""
    print("\n创建目录结构...")
    directories = [
        'data/uploads',
        'data/sessions',
        'data/logs',
        'logs'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")

def setup_production_config():
    """设置生产环境配置"""
    print("\n设置生产环境配置...")

    # 创建生产环境配置文件
    config = {
        "production": True,
        "host": "0.0.0.0",
        "port": 5000,
        "debug": False,
        "log_level": "INFO",
        "upload_folder": "data/uploads",
        "max_content_length": 16777216,
        "session_timeout": 3600
    }

    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'production.json')
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✓ 生产配置已保存到: {config_file}")

def create_systemd_service():
    """创建systemd服务文件（Linux）"""
    if sys.platform != "linux":
        print("跳过systemd服务创建（非Linux系统）")
        return

    print("\n创建systemd服务...")

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_content = f"""[Unit]
Description=名侦探作业帮
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={project_path}
Environment=PATH={project_path}/venv/bin
ExecStart={project_path}/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_file = "/etc/systemd/system/detective-study-helper.service"

    # 检查是否有写入权限
    if os.access(os.path.dirname(service_file), os.W_OK):
        with open(service_file, 'w') as f:
            f.write(service_content)
        print(f"✓ Systemd服务已创建: {service_file}")
        print("运行以下命令启用服务:")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable detective-study-helper")
        print("  sudo systemctl start detective-study-helper")
    else:
        print("没有权限创建systemd服务，请手动创建:")
        print(f"文件路径: {service_file}")
        print("内容:")
        print(service_content)

def create_nginx_config():
    """创建Nginx配置"""
    print("\n创建Nginx配置...")

    nginx_config = """server {
    listen 80;
    server_name your_domain.com;  # 替换为你的域名或IP

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件缓存
    location /static/ {
        alias /path/to/project/frontend/static/;  # 替换为实际路径
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""

    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'nginx.conf')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(nginx_config)

    print(f"✓ Nginx配置已保存到: {config_file}")
    print("请将配置文件复制到 /etc/nginx/sites-available/ 并创建软链接")

def main():
    """主函数"""
    print("="*60)
    print("名侦探作业帮 - 部署脚本")
    print("="*60)

    # 解析命令行参数
    if len(sys.argv) > 1:
        deploy_type = sys.argv[1]
    else:
        print("\n请选择部署类型:")
        print("1. 本地开发环境")
        print("2. 生产服务器环境")
        choice = input("请输入选择 (1/2): ")
        deploy_type = "development" if choice == "1" else "production"

    # 执行部署步骤
    check_requirements()
    install_dependencies()
    create_directories()

    if deploy_type == "production":
        setup_production_config()
        create_systemd_service()
        create_nginx_config()

        print("\n" + "="*60)
        print("生产环境部署完成！")
        print("\n后续步骤:")
        print("1. 配置环境变量 (src/.env)")
        print("2. 配置Nginx反向代理")
        print("3. 设置SSL证书（推荐）")
        print("4. 配置防火墙规则")
        print("5. 启动服务")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("开发环境部署完成！")
        print("\n运行应用:")
        print("  python start.py")
        print("\n访问地址: http://localhost:5000")
        print("="*60)

if __name__ == "__main__":
    main()