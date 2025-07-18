@echo off
echo Testing Flask installation...
python test_imports.py
echo.
echo Starting the Manufacturing Anomaly Detection System...
echo Open your browser and go to: http://localhost:5000
echo.
python app.py
