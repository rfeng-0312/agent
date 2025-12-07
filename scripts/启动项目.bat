@echo off
chcp 65001 > nul
title 名侦探作业帮 - 启动脚本

echo ========================================
echo  名侦探作业帮 - AI智能解题助手
echo ========================================
echo.

:: 检查Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo 检查到Python版本:
python --version
echo.

:: 检查虚拟环境（可选）
if exist "venv\Scripts\activate.bat" (
    echo 使用虚拟环境...
    call venv\Scripts\activate.bat
    echo.
)

:: 检查并安装依赖
echo 检查依赖包...
pip show flask > nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包，请稍候...
    pip install -r requirements.txt
    echo.
)

:: 检查.env文件
if not exist ".env" (
    echo 警告: 未找到.env文件！
    echo.
    echo 请按照以下步骤配置：
    echo 1. 复制 .env.example 为 .env
    echo 2. 在 .env 文件中填入你的 DeepSeek API Key
    echo.
    set /p continue="是否继续启动？(Y/N): "
    if /i not "%continue%"=="Y" goto :end
    echo.
)

:: 启动应用
echo 正在启动服务器...
echo.
echo 访问地址：
echo - 本地访问: http://localhost:5000
echo - 局域网访问: http://你的IP地址:5000
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

:: 启动Flask应用
python app.py

:end
echo.
echo 服务器已停止
pause