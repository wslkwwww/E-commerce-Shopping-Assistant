@echo off
:: 切换代码页到 UTF-8 以正确显示中文字符
chcp 65001 > nul

:: =================================================================
::  智能电商导购助手 (Dianshan Agent) 启动脚本
:: =================================================================
::
::  此脚本会自动执行以下操作:
::  1. 激活名为 'dianshan-agent' 的 Conda 环境。
::  2. 启动后端的 Flask Web 服务器。
::
::  使用方法:
::  直接双击运行此文件，或在终端中执行 "start.bat"。
::

title Dianshan Agent Backend

echo.
echo [INFO] ==================================================
echo [INFO]      正在启动智能电商导购助手后端服务...
echo [INFO] ==================================================
echo.

:: 1. 激活 Conda 环境
echo [STEP 1/2] 正在激活 Conda 环境 'dianshan-agent'...
:: 如果您的 conda 不在系统路径中，您可能需要先运行 conda.bat
call conda activate dianshan-agent

:: 检查 conda 环境是否成功激活
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 激活 Conda 环境 'dianshan-agent' 失败！
    echo [ERROR] 请确认您已正确安装 Conda 并创建了该环境。
    pause
    exit /b
)

echo [INFO] Conda 环境已成功激活。
echo.

:: 2. 启动 Flask 应用
echo [STEP 2/2] 正在启动 Flask 服务器...
echo [INFO] API 服务将运行在 http://0.0.0.0:5000
echo [INFO] 按下 CTRL+C 可以停止服务器。
echo.

python -m ecommerce_agent.app

echo.
echo [INFO] 服务器已停止。
pause