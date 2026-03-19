@echo off
REM ====================================================
REM Interview Coach - 自动环境安装脚本
REM ====================================================
REM 此脚本将自动安装Python 3.11并设置虚拟环境
REM ====================================================

echo.
echo =====================================================
echo   Interview Coach - 环境自动安装
echo =====================================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 已获取管理员权限
) else (
    echo [WARNING] 建议以管理员身份运行此脚本
    echo.
)

REM 步骤1: 下载Python 3.11安装程序
echo [1/5] 下载Python 3.11安装程序...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe

if not exist "%PYTHON_INSTALLER%" (
    echo 正在下载Python 3.11.9...
    powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"
    if %errorLevel% == 0 (
        echo [OK] 下载完成
    ) else (
        echo [ERROR] 下载失败，请手动下载: %PYTHON_URL%
        pause
        exit /b 1
    )
) else (
    echo [OK] 安装程序已存在
)

REM 步骤2: 静默安装Python 3.11
echo [2/5] 安装Python 3.11...
echo 正在安装Python到: C:\Python311
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=0 Include_test=0 TargetDir=C:\Python311
if %errorLevel% == 0 (
    echo [OK] Python 3.11安装成功
) else (
    echo [WARNING] 安装可能失败，请检查
)

REM 步骤3: 创建虚拟环境
echo [3/5] 创建虚拟环境...
cd /d "%~dp0"
if exist venv (
    echo [OK] 虚拟环境已存在
) else (
    C:\Python311\python.exe -m venv venv
    if %errorLevel% == 0 (
        echo [OK] 虚拟环境创建成功
    ) else (
        echo [ERROR] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

REM 步骤4: 激活虚拟环境并安装依赖
echo [4/5] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat

echo 升级pip...
python -m pip install --upgrade pip

echo 安装项目依赖...
pip install -r requirements.txt

if %errorLevel% == 0 (
    echo [OK] 依赖安装成功
) else (
    echo [WARNING] 部分依赖安装失败
)

REM 步骤5: 验证安装
echo [5/5] 验证安装...
echo.
echo =====================================================
echo   安装验证
echo =====================================================
echo.

C:\Python311\python.exe --version
echo.

echo 已安装的包:
pip list | findstr /i "pydantic anthropic pytest"
echo.

REM 测试导入
echo 测试模块导入...
cd /d "%~dp0"
C:\Python311\python.exe -c "from models import ParsedResume; print('[OK] models imported')" 2>nul
if %errorLevel% == 0 (
    echo [OK] 模块导入成功
) else (
    echo [WARNING] 模块导入失败，可能需要进一步检查
)

echo.
echo =====================================================
echo   安装完成！
echo =====================================================
echo.
echo 使用说明:
echo   1. 激活虚拟环境: venv\Scripts\activate.bat
echo   2. 运行测试: pytest tests/unit/ -v
echo   3. 运行验证: python validate_tdd.py
echo   4. 退出虚拟环境: deactivate
echo.
echo 按任意键退出...
pause >nul
