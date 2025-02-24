import os
import pickle

import pandas as pd
from flask import Flask, jsonify, render_template, request
from sklearn.preprocessing import LabelEncoder

# Load the model and encoders
with open('model.pkl', 'rb') as model_file:
    model, label_encoders, scaler = pickle.load(model_file)

app = Flask(__name__)

PING_ATTACK_THRESHOLD = 35
PORT_ATTACK_THRESHOLD = 150

def load_dataset(dataset_path):
    dataset_path = dataset_path.strip().strip('"')
    if os.path.exists(dataset_path):
        return pd.read_csv(dataset_path)
    else:
        return None

def preprocess_data(df):
    df = df.drop(columns=['No.', 'Time', 'Info'], errors='ignore')

    for col in ['Source', 'Destination', 'Protocol']:
        if col in df.columns:
            df[col] = label_encoders[col].transform(df[col].astype(str))

    if 'Length' in df.columns:
        df[['Length']] = scaler.transform(df[['Length']])

    return df

def detect_intrusion(df):
    protocol_series = df['Protocol']

    ping_attack = (protocol_series.rolling(window=PING_ATTACK_THRESHOLD).apply(lambda x: (x == "eth:ethertype:ip:data").all(), raw=True).any())
    port_attack = (protocol_series.rolling(window=PORT_ATTACK_THRESHOLD).apply(lambda x: (x == "eth:ethertype:ip:tcp").all(), raw=True).any())

    if ping_attack and port_attack:
        return "Multiple attacks detected: Ping and Port Attack"
    elif ping_attack:
        return "Ping Attack Detected!"
    elif port_attack:
        return "Port Attack Detected!"
    else:
        return "No Intrusion Detected, Monitoring Ongoing...!!"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_monitoring():
    dataset_path = request.form.get('file_path', '').strip()
    df = load_dataset(dataset_path)

    if df is None or df.empty:
        return jsonify({'status': 'Error: Invalid or empty dataset'})

    df = preprocess_data(df)
    intrusion_alert = detect_intrusion(df)
    
    return jsonify({'status': intrusion_alert})

if __name__ == '__main__':
    app.run(debug=True)
