@echo off
setlocal EnableDelayedExpansion

cd /d "C:\Practice\learning\interview-coach"

echo ========================================
echo TDD Validation Test
echo ========================================
echo.

echo [1] Python Version:
python --version
echo.

echo [2] Running validation...
echo ========================================
python validate_tdd.py
set RESULT=%errorLevel%
echo ========================================
echo.

if !RESULT! == 0 (
    echo SUCCESS: All tests passed
) else (
    echo FAILED: Exit code !RESULT!
)

echo.
echo [3] Validation result:
if exist validation_result.txt (
    type validation_result.txt
) else (
    echo No result file created
)

echo.
pause
