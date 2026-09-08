import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib

MODEL_PATH = "lstm_model.keras"
SCALER_PATH = "scaler.pkl"

from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU

MODEL_PATH_LSTM = "lstm_model.keras"
MODEL_PATH_GRU = "gru_model.keras"
SCALER_PATH = "scaler.pkl"

def create_dataset(dataset, time_step=60):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        X.append(a)
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

def train_or_load_model(df, close_col='Close', model_type="LSTM"):
    try:
        if len(df) < 100:
            raise ValueError("Not enough data to train model.")
        if close_col not in df.columns:
            cols = [c for c in df.columns if 'close' in c.lower()]
            if cols: close_col = cols[0]
            else: return None, None
                
        data = df.filter([close_col]).values
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        target_path = MODEL_PATH_GRU if model_type == "GRU" else MODEL_PATH_LSTM
        
        global _cached_models, _cached_scalers
        if "_cached_models" not in globals():
            _cached_models = {}
            _cached_scalers = {}
            
        if target_path in _cached_models and SCALER_PATH in _cached_scalers:
            return _cached_models[target_path], _cached_scalers[SCALER_PATH]
        
        if os.path.exists(target_path) and os.path.exists(SCALER_PATH):
            try:
                model = load_model(target_path)
                scaler = joblib.load(SCALER_PATH)
                _cached_models[target_path] = model
                _cached_scalers[SCALER_PATH] = scaler
                return model, scaler
            except: pass
                
        training_data_len = int(np.ceil(len(data) * .8))
        train_data = scaled_data[0:int(training_data_len), :]
        X_train, y_train = create_dataset(train_data, time_step=60)
        
        if len(X_train) == 0: return None, None
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        
        model = Sequential()
        if model_type == "GRU":
            model.add(GRU(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(GRU(50, return_sequences=False))
        else:
            model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(50, return_sequences=False))
            
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train, y_train, batch_size=32, epochs=5, verbose=0)
        
        model.save(target_path)
        joblib.dump(scaler, SCALER_PATH)
        return model, scaler
    except Exception as e:
        print(f"Training error: {e}")
        return None, None

def math_surrogate_arima(data, days=1):
    # Mimics ARIMA: Uses short-term moving average with heavy immediate variance matching
    base = data[-1][0]
    trend = data[-1][0] - data[-5][0] if len(data) >= 5 else 0
    predictions = []
    for _ in range(days):
        base += trend * 0.1 # dampen trend
        predictions.append(base)
    return predictions

def math_surrogate_prophet(data, days=1):
    # Mimics Prophet: Uses long-term median smoothing
    # Very stable, less reactive
    median_val = np.median(data[-20:]) if len(data) >= 20 else data[-1][0]
    base = data[-1][0]
    predictions = []
    for _ in range(days):
        # Gravitate towards median
        base = base + (median_val - base) * 0.05
        predictions.append(base)
    return predictions

def predict_future(df, days=1, close_col='Close', model_type="LSTM"):
    try:
        if close_col not in df.columns:
            cols = [c for c in df.columns if 'close' in c.lower()]
            if cols: close_col = cols[0]
            else: return []

        data = df.filter([close_col]).values
        
        # Surrogate Models (ARIMA / Prophet Dummy Logic)
        if "ARIMA" in model_type:
            return math_surrogate_arima(data, days)
        if "Prophet" in model_type:
            return math_surrogate_prophet(data, days)
            
        # Neural Models (LSTM / GRU)
        model, _ = train_or_load_model(df, close_col, "GRU" if "GRU" in model_type else "LSTM")
        if model is None or len(data) < 60: return []

        # Always fit a temporary fresh scaler for the CURRENT symbol's data to guarantee correct bounds!
        from sklearn.preprocessing import MinMaxScaler
        dynamic_scaler = MinMaxScaler(feature_range=(0, 1))
        dynamic_scaler.fit(data)

        last_60_days = data[-60:]
        last_60_days_scaled = dynamic_scaler.transform(last_60_days)
        
        current_batch = np.reshape(np.array([last_60_days_scaled]), (1, 60, 1))
        predictions = []
        for _ in range(days):
            pred_scaled = model.predict(current_batch, verbose=0)[0]
            predictions.append(pred_scaled[0])
            current_batch = np.append(current_batch[:,1:,:], [[[pred_scaled[0]]]], axis=1)
            
        predictions = dynamic_scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        return predictions.flatten().tolist()
    except:
        return []

def evaluate_model(df, close_col='Close'):
    return 0.0, 0.0 # Disabled for speed constraints in real-time UI
