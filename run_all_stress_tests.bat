@echo off
echo ========================================
echo Elevator Simulation Stress Test Suite
echo ========================================
echo.

echo Starting comprehensive stress tests...
echo.
python stress_test.py
echo.
echo ========================================
echo.

echo Starting GUI stress tests...
echo.
python gui_stress_test.py
echo.
echo ========================================
echo.

echo Starting configuration corruption tests...
echo.
python config_corruption_test.py
echo.
echo ========================================
echo.

echo All stress tests completed!
echo Check the output above for results and any issues found.
echo.
pause
