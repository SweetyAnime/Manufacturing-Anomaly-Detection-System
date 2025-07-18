from flask import Flask, request, render_template, jsonify, send_file
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
import random
import time
import threading
from werkzeug.utils import secure_filename
import os
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for live data generation
live_data = []
anomaly_model = None
scaler = None
is_generating = False
generation_thread = None

# Normal operating ranges for manufacturing sensors
NORMAL_RANGES = {
    'Temperature': (60, 75),
    'Vibration': (0.2, 0.8),
    'Pressure': (101000, 102000)
}

# Anomaly patterns for root cause analysis
ANOMALY_PATTERNS = {
    'High Temperature': {
        'condition': lambda row: row['Temperature'] > 80,
        'causes': ['Cooling system failure', 'Excessive friction', 'Blocked ventilation', 'Overload operation']
    },
    'Low Temperature': {
        'condition': lambda row: row['Temperature'] < 55,
        'causes': ['Heating system malfunction', 'Ambient temperature drop', 'Sensor calibration error']
    },
    'High Vibration': {
        'condition': lambda row: row['Vibration'] > 1.0,
        'causes': ['Bearing wear', 'Misalignment', 'Loose components', 'Imbalanced rotating parts']
    },
    'Low Vibration': {
        'condition': lambda row: row['Vibration'] < 0.1,
        'causes': ['Motor shutdown', 'Belt slippage', 'Coupling failure', 'Sensor malfunction']
    },
    'High Pressure': {
        'condition': lambda row: row['Pressure'] > 102500,
        'causes': ['Valve blockage', 'Pump overperformance', 'Downstream restriction', 'Pressure relief valve failure']
    },
    'Low Pressure': {
        'condition': lambda row: row['Pressure'] < 100500,
        'causes': ['Leak in system', 'Pump failure', 'Filter clogging', 'Valve malfunction']
    },
    'Multiple Parameters': {
        'condition': lambda row: (row['Temperature'] > 80 and row['Vibration'] > 1.0) or (row['Temperature'] < 55 and row['Pressure'] < 100500),
        'causes': ['System-wide failure', 'Power supply issues', 'Control system malfunction', 'Cascading equipment failure']
    }
}

def analyze_anomaly_root_cause(row):
    """Analyze potential root causes for anomalies"""
    causes = []
    
    for pattern_name, pattern_info in ANOMALY_PATTERNS.items():
        if pattern_info['condition'](row):
            causes.extend(pattern_info['causes'])
    
    # Remove duplicates and return top 3 most likely causes
    unique_causes = list(set(causes))
    return unique_causes[:3] if unique_causes else ['Unknown cause - requires manual inspection']

def generate_live_data():
    """Generate live sensor data with occasional anomalies"""
    global live_data, is_generating
    
    while is_generating:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Generate normal data 80% of the time
            if random.random() < 0.8:
                temp = random.uniform(NORMAL_RANGES['Temperature'][0], NORMAL_RANGES['Temperature'][1])
                vibration = random.uniform(NORMAL_RANGES['Vibration'][0], NORMAL_RANGES['Vibration'][1])
                pressure = random.uniform(NORMAL_RANGES['Pressure'][0], NORMAL_RANGES['Pressure'][1])
            else:
                # Generate anomalous data 20% of the time
                anomaly_type = random.choice(['temp_high', 'temp_low', 'vib_high', 'vib_low', 'press_high', 'press_low'])
                
                if anomaly_type == 'temp_high':
                    temp = random.uniform(85, 95)
                    vibration = random.uniform(NORMAL_RANGES['Vibration'][0], NORMAL_RANGES['Vibration'][1])
                    pressure = random.uniform(NORMAL_RANGES['Pressure'][0], NORMAL_RANGES['Pressure'][1])
                elif anomaly_type == 'temp_low':
                    temp = random.uniform(45, 55)
                    vibration = random.uniform(NORMAL_RANGES['Vibration'][0], NORMAL_RANGES['Vibration'][1])
                    pressure = random.uniform(NORMAL_RANGES['Pressure'][0], NORMAL_RANGES['Pressure'][1])
                elif anomaly_type == 'vib_high':
                    temp = random.uniform(NORMAL_RANGES['Temperature'][0], NORMAL_RANGES['Temperature'][1])
                    vibration = random.uniform(1.2, 2.0)
                    pressure = random.uniform(NORMAL_RANGES['Pressure'][0], NORMAL_RANGES['Pressure'][1])
                elif anomaly_type == 'vib_low':
                    temp = random.uniform(NORMAL_RANGES['Temperature'][0], NORMAL_RANGES['Temperature'][1])
                    vibration = random.uniform(0.05, 0.15)
                    pressure = random.uniform(NORMAL_RANGES['Pressure'][0], NORMAL_RANGES['Pressure'][1])
                elif anomaly_type == 'press_high':
                    temp = random.uniform(NORMAL_RANGES['Temperature'][0], NORMAL_RANGES['Temperature'][1])
                    vibration = random.uniform(NORMAL_RANGES['Vibration'][0], NORMAL_RANGES['Vibration'][1])
                    pressure = random.uniform(103000, 105000)
                else:  # press_low
                    temp = random.uniform(NORMAL_RANGES['Temperature'][0], NORMAL_RANGES['Temperature'][1])
                    vibration = random.uniform(NORMAL_RANGES['Vibration'][0], NORMAL_RANGES['Vibration'][1])
                    pressure = random.uniform(99000, 100500)
            
            # Add some noise
            temp += random.uniform(-0.5, 0.5)
            vibration += random.uniform(-0.05, 0.05)
            pressure += random.uniform(-50, 50)
            
            new_data = {
                'Time': current_time,
                'Temperature': round(temp, 2),
                'Vibration': round(max(0, vibration), 3),
                'Pressure': round(pressure, 0)
            }
            
            live_data.append(new_data)
            
            # Keep only last 50 data points
            if len(live_data) > 50:
                live_data.pop(0)
            
            time.sleep(2)  # Generate new data every 2 seconds
            
        except Exception as e:
            print(f"Error in live data generation: {e}")
            break

def process_data(df):
    """Process data and detect anomalies"""
    try:
        # Make a copy to avoid modifying original
        df_copy = df.copy()
        
        # Preprocess (drop Time, normalize the rest)
        df_clean = df_copy.drop(columns=["Time"])
        
        # Normalize data between 0 and 1
        scaler = MinMaxScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df_clean), columns=df_clean.columns)
        
        # Train Isolation Forest model
        model = IsolationForest(contamination=0.25, random_state=42)
        predictions = model.fit_predict(df_scaled)
        
        # Add predictions back to original data
        df_copy["Anomaly"] = pd.Series(predictions).replace({1: "Normal", -1: "Anomaly"})
        
        # Add anomaly scores
        scores = model.decision_function(df_scaled)
        df_copy["Anomaly_Score"] = scores
        
        # Analyze root causes for anomalies
        root_causes = []
        for _, row in df_copy.iterrows():
            if row["Anomaly"] == "Anomaly":
                causes = analyze_anomaly_root_cause(row)
                root_causes.append(causes)
            else:
                root_causes.append([])
        
        df_copy["Root_Causes"] = root_causes
        
        return df_copy, model, scaler
        
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None, None

def create_visualization(df):
    """Create interactive plots using Plotly"""
    try:
        # Create subplots
        fig = go.Figure()
        
        # Add temperature trace
        fig.add_trace(go.Scatter(
            x=df['Time'],
            y=df['Temperature'],
            mode='lines+markers',
            name='Temperature (°C)',
            line=dict(color='red'),
            marker=dict(
                color=['red' if anomaly == 'Anomaly' else 'blue' for anomaly in df['Anomaly']],
                size=8
            )
        ))
        
        # Add vibration trace (secondary y-axis)
        fig.add_trace(go.Scatter(
            x=df['Time'],
            y=df['Vibration'],
            mode='lines+markers',
            name='Vibration (units)',
            line=dict(color='green'),
            marker=dict(
                color=['red' if anomaly == 'Anomaly' else 'green' for anomaly in df['Anomaly']],
                size=8
            ),
            yaxis='y2'
        ))
        
        # Add pressure trace (secondary y-axis)
        fig.add_trace(go.Scatter(
            x=df['Time'],
            y=df['Pressure'],
            mode='lines+markers',
            name='Pressure (Pa)',
            line=dict(color='purple'),
            marker=dict(
                color=['red' if anomaly == 'Anomaly' else 'purple' for anomaly in df['Anomaly']],
                size=8
            ),
            yaxis='y3'
        ))
        
        # Update layout
        fig.update_layout(
            title='Manufacturing Process Sensor Data with Anomaly Detection',
            xaxis_title='Time',
            yaxis=dict(
                title='Temperature (°C)',
                side='left',
                color='red'
            ),
            yaxis2=dict(
                title='Vibration (units)',
                overlaying='y',
                side='right',
                color='green'
            ),
            yaxis3=dict(
                title='Pressure (Pa)',
                overlaying='y',
                side='right',
                position=0.85,
                color='purple'
            ),
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read and process the CSV
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_columns = ['Time', 'Temperature', 'Vibration', 'Pressure']
            if not all(col in df.columns for col in required_columns):
                return jsonify({'error': f'CSV must contain columns: {required_columns}'})
            
            # Process data
            processed_df, model, scaler = process_data(df)
            
            if processed_df is None:
                return jsonify({'error': 'Error processing data'})
            
            # Create visualization
            plot_json = create_visualization(processed_df)
            
            # Get anomaly summary
            anomaly_count = len(processed_df[processed_df['Anomaly'] == 'Anomaly'])
            total_count = len(processed_df)
            
            # Get detailed anomaly information
            anomalies = processed_df[processed_df['Anomaly'] == 'Anomaly'].to_dict('records')
            
            return jsonify({
                'success': True,
                'data': processed_df.to_dict('records'),
                'plot': plot_json,
                'anomaly_count': anomaly_count,
                'total_count': total_count,
                'anomalies': anomalies
            })
        
        else:
            return jsonify({'error': 'Please upload a CSV file'})
            
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'})

@app.route('/start_live_generation', methods=['POST'])
def start_live_generation():
    global is_generating, generation_thread, live_data
    
    try:
        if not is_generating:
            is_generating = True
            live_data = []
            generation_thread = threading.Thread(target=generate_live_data)
            generation_thread.daemon = True
            generation_thread.start()
            return jsonify({'success': True, 'message': 'Live data generation started'})
        else:
            return jsonify({'success': False, 'message': 'Live generation already running'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting live generation: {str(e)}'})

@app.route('/stop_live_generation', methods=['POST'])
def stop_live_generation():
    global is_generating
    
    try:
        is_generating = False
        return jsonify({'success': True, 'message': 'Live data generation stopped'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping live generation: {str(e)}'})

@app.route('/get_live_data', methods=['GET'])
def get_live_data():
    global live_data
    
    try:
        if not live_data:
            return jsonify({'data': [], 'anomalies': []})
        
        # Create DataFrame from live data
        df = pd.DataFrame(live_data)
        
        # Process for anomaly detection
        processed_df, model, scaler = process_data(df)
        
        if processed_df is None:
            return jsonify({'data': live_data, 'anomalies': []})
        
        # Create visualization
        plot_json = create_visualization(processed_df)
        
        # Get current anomalies
        current_anomalies = processed_df[processed_df['Anomaly'] == 'Anomaly'].to_dict('records')
        
        # Get latest data point for alerts
        latest_data = processed_df.iloc[-1] if len(processed_df) > 0 else None
        
        return jsonify({
            'data': processed_df.to_dict('records'),
            'plot': plot_json,
            'anomalies': current_anomalies,
            'latest': latest_data.to_dict() if latest_data is not None else None,
            'is_generating': is_generating
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting live data: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
