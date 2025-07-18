@echo off
echo Installing required packages...
pip install -r requirements.txt

echo Starting the Manufacturing Anomaly Detection System...
python app.py

pause
