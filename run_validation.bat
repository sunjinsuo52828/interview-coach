@echo off
cd /d "C:\Practice\learning\interview-coach"
echo Running TDD validation...
python validate_tdd.py
if %errorLevel% == 0 (
    echo.
    echo ================================
    echo VALIDATION SUCCESSFUL
    echo ================================
) else (
    echo.
    echo ================================
    echo VALIDATION FAILED - Exit code: %errorLevel%
    echo ================================
)
pause
