@echo off
REM ====================================================
REM 快速环境检查 - 不需要完整安装
REM ====================================================

echo.
echo =====================================================
echo   Interview Coach - 环境检查
echo =====================================================
echo.

REM 检查Python版本
echo 检测到的Python版本:
py -0 2>nul
if %errorLevel% == 0 (
    echo.
) else (
    echo Python Launcher未找到
)

REM 检查当前Python
echo 当前Python版本:
python --version 2>nul
if %errorLevel% == 0 (
    echo.
) else (
    echo Python不在PATH中
)

REM 检查pip
echo.
echo 检查pip:
pip --version 2>nul
if %errorLevel% == 0 (
    echo [OK] pip可用
) else (
    echo [WARNING] pip不可用
)

REM 检查已安装的包
echo.
echo 已安装的关键包:
pip list 2>nul | findstr /i "pydantic anthropic pytest python-dotenv"
if %errorLevel% == 0 (
    echo [OK] 找到关键包
) else (
    echo [WARNING] 未找到完整的关键包
)

echo.
echo =====================================================
echo   建议
echo =====================================================
echo.

REM 检查Python版本是否为3.14
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo %PYVER% | findstr "3.14" >nul
if %errorLevel% == 0 (
    echo [WARNING] 检测到Python 3.14 (alpha版本)
    echo   此版本与pydantic存在兼容性问题
    echo.
    echo 建议方案:
    echo   1. 运行 setup_env.bat 自动安装Python 3.11
    echo   2. 或手动从 https://www.python.org/downloads/ 下载Python 3.11
    echo   3. 或使用conda: conda create -n ic python=3.11
) else (
    echo [OK] Python版本看起来正常
    echo   可以尝试运行: python validate_tdd.py
)

echo.
echo 按任意键退出...
pause >nul
