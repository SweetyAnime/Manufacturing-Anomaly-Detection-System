# Manufacturing Anomaly Detection System

## IBM Hackathon Project - Anomaly Detection in Manufacturing Processes

This web application provides real-time anomaly detection for manufacturing processes using machine learning. It supports both file upload analysis and live data generation with real-time monitoring.

## Features

### 🔍 **Anomaly Detection**
- Uses Isolation Forest algorithm for unsupervised anomaly detection
- Detects anomalies in Temperature, Vibration, and Pressure sensors
- Provides anomaly scores and confidence levels

### 📊 **Data Visualization**
- Interactive Plotly charts with real-time updates
- Multi-axis plotting for different sensor types
- Color-coded anomaly highlighting

### 🚨 **Root Cause Analysis**
- Intelligent pattern recognition for anomaly causes
- Predefined patterns for common manufacturing issues
- Detailed recommendations for each anomaly type

### 📁 **File Upload Support**
- CSV file upload and analysis
- Automatic data validation
- Batch processing of historical data

### 🔴 **Live Data Generation**
- Real-time sensor data simulation
- Configurable anomaly injection rates
- Live alerts and notifications

## Installation

1. Install Python 3.8+ if not already installed
2. Run the startup script:
   ```
   run.bat
   ```

## Manual Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## CSV File Format

Your CSV file should contain the following columns:
- **Time**: Timestamp (HH:MM:SS format)
- **Temperature**: Temperature readings in Celsius
- **Vibration**: Vibration levels in units
- **Pressure**: Pressure readings in Pascals

Example:
```csv
Time,Temperature,Vibration,Pressure
10:00:00,65,0.3,101200
10:00:05,65.5,0.4,101350
10:00:10,92.3,1.2,101800
```

## Usage

### File Upload Mode
1. Click "Choose File" and select your CSV file
2. Click "Analyze Data" to process the file
3. View results in the visualization and anomaly reports

### Live Generation Mode
1. Click "Start Live Generation" to begin real-time monitoring
2. Watch the live charts update every 2 seconds
3. Monitor alerts for real-time anomaly detection
4. Click "Stop Generation" to end monitoring

## Anomaly Types Detected

The system can detect and analyze the following anomaly patterns:

### Temperature Anomalies
- **High Temperature**: >80°C
  - Possible causes: Cooling system failure, excessive friction, blocked ventilation
- **Low Temperature**: <55°C
  - Possible causes: Heating system malfunction, ambient temperature drop

### Vibration Anomalies
- **High Vibration**: >1.0 units
  - Possible causes: Bearing wear, misalignment, loose components
- **Low Vibration**: <0.1 units
  - Possible causes: Motor shutdown, belt slippage, sensor malfunction

### Pressure Anomalies
- **High Pressure**: >102,500 Pa
  - Possible causes: Valve blockage, pump overperformance, downstream restriction
- **Low Pressure**: <100,500 Pa
  - Possible causes: System leak, pump failure, filter clogging

### System-Wide Anomalies
- Multiple parameter failures indicating cascading equipment issues
- Power supply problems
- Control system malfunctions

## Technical Details

### Machine Learning Model
- **Algorithm**: Isolation Forest
- **Contamination Rate**: 25% (configurable)
- **Features**: Temperature, Vibration, Pressure (normalized)
- **Preprocessing**: MinMax scaling (0-1 range)

### Architecture
- **Backend**: Flask web framework
- **Frontend**: Bootstrap 5 + Plotly.js
- **Data Processing**: Pandas + Scikit-learn
- **Real-time Updates**: AJAX polling every 3 seconds

### Performance
- Processes up to 1000+ data points efficiently
- Real-time generation: 1 data point every 2 seconds
- Memory efficient: maintains only last 50 live data points

## Customization

### Adjusting Normal Ranges
Edit the `NORMAL_RANGES` dictionary in `app.py`:

```python
NORMAL_RANGES = {
    'Temperature': (60, 75),    # Min, Max in Celsius
    'Vibration': (0.2, 0.8),   # Min, Max in units
    'Pressure': (101000, 102000) # Min, Max in Pascals
}
```

### Adding New Anomaly Patterns
Add new patterns to the `ANOMALY_PATTERNS` dictionary:

```python
'New_Pattern': {
    'condition': lambda row: row['Temperature'] > 90 and row['Vibration'] > 1.5,
    'causes': ['Specific cause 1', 'Specific cause 2']
}
```

### Changing Update Frequency
Modify the intervals in the JavaScript:
- Live data generation: Change `time.sleep(2)` in `generate_live_data()`
- Frontend updates: Change `3000` in `setInterval()` calls

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   - Change port in `app.py`: `app.run(port=5001)`

2. **CSV file not recognized**
   - Ensure file has .csv extension
   - Check that all required columns are present
   - Verify data format matches examples

3. **Live generation not starting**
   - Check if port is accessible
   - Ensure no firewall blocking
   - Try refreshing the page

### Error Messages

- **"CSV must contain columns"**: Your file is missing required columns
- **"Error processing data"**: Data format issue or corrupted file
- **"No file selected"**: Select a CSV file before uploading

## License

This project is created for the IBM Hackathon on Anomaly Detection in Manufacturing Processes.

## Contributors

- Developed for IBM Hackathon
- Topic: Anomaly Detection in Manufacturing Processes
- Framework: Flask + Machine Learning + Real-time Analytics
