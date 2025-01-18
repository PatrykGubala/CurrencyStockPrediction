import os
import time
from math import sqrt
from datetime import timedelta
import numpy as np
import pandas as pd
import tensorflow as tf
from django.utils import timezone
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense, Input
from tensorflow.keras.callbacks import EarlyStopping, Callback
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from decimal import Decimal, ROUND_HALF_UP, DecimalException
from myapp.models import Currency, CurrenciesPrediction, CurrenciesTrainedModels
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository
from myapp.services.currencies_data_service import CurrenciesDataService, logger

def plot_line_graph(x_data_list, y_data_list, labels, title, x_label, y_label, legend_labels, output_path, figure_size=(14, 7)):
    plt.figure(figsize=figure_size)
    for x_data, y_data, lbl in zip(x_data_list, y_data_list, legend_labels):
        plt.plot(x_data, y_data, label=lbl)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

def decompose_time_series(data, currency, output_dir):
    from statsmodels.tsa.seasonal import seasonal_decompose
    close_col = f'Close_{currency}'
    result = seasonal_decompose(data[close_col], model='multiplicative', period=252)
    plt.figure(figsize=(15, 10))
    plt.subplot(411)
    plt.title('Original Time Series')
    plt.plot(data.index, result.observed)
    plt.subplot(412)
    plt.title('Trend')
    plt.plot(data.index, result.trend)
    plt.subplot(413)
    plt.title('Seasonal')
    plt.plot(data.index, result.seasonal)
    plt.subplot(414)
    plt.title('Residual')
    plt.plot(data.index, result.resid)
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f'{currency}_seasonal_decomposition.png'))
    plt.close()
    return result

def plot_results(currency, y_train_seq, y_test_plot, predictions, y_train_dates, y_test_dates, scaler_y, currency_output_dir, dataset_time):
    y_train_plot = scaler_y.inverse_transform(y_train_seq.reshape(-1, 1)).flatten()
    train_plot_path = os.path.join(currency_output_dir, f'{currency}_train_plot.png')
    plt.figure(figsize=(12, 6))
    plt.plot(y_train_dates, y_train_plot, label='Train Actual')
    plt.title(f'{currency} Training Data (Last {dataset_time} Years)')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    os.makedirs(currency_output_dir, exist_ok=True)
    plt.savefig(train_plot_path)
    plt.close()
    test_plot_path = os.path.join(currency_output_dir, f'{currency}_test_plot.png')
    plt.figure(figsize=(12, 6))
    plt.plot(y_test_dates, y_test_plot, label='Test Actual')
    plt.plot(y_test_dates, predictions, label='Test Predicted')
    plt.title(f'{currency} Test Data (Actual vs. Predicted)')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.savefig(test_plot_path)
    plt.close()

def visualize_data(data, currency, output_dir):
    close_col = 'close'
    plot_path = os.path.join(output_dir, f'{currency}_closing_prices.png')
    plot_line_graph(
        x_data_list=[data.index],
        y_data_list=[data[close_col]],
        labels=[close_col],
        title=f'{currency} Closing Prices',
        x_label='Date',
        y_label='Price',
        legend_labels=[close_col],
        output_path=plot_path,
        figure_size=(14, 7)
    )
    numeric_data = data.select_dtypes(include=[np.number])
    correlation = numeric_data.corr()
    heatmap_path = os.path.join(output_dir, f'{currency}_correlation_heatmap.png')

def seasonal_decompose_local(data, freq=252):
    from statsmodels.tsa.seasonal import seasonal_decompose
    return seasonal_decompose(data, model='multiplicative', period=freq)

def add_stochastic_features_local(df):
    if 'close' not in df.columns or df['close'].empty:
        return df
    if df['close'].sum() != 0:
        probabilities = df['close'] / df['close'].sum()
        df['Entropy'] = - (probabilities * np.log2(probabilities + 1e-10))
    else:
        df['Entropy'] = 0
    df['Random_Component'] = np.random.normal(0, df['close'].std(), len(df))
    def ornstein_uhlenbeck_process(mu, sigma, theta, T, N):
        dt = T / N
        process = np.zeros(N)
        process[0] = mu
        for t in range(1, N):
            process[t] = process[t - 1] + theta * (mu - process[t - 1]) * dt + sigma * np.sqrt(dt) * np.random.normal(0, 1)
        return process
    df['OU_Simulated'] = ornstein_uhlenbeck_process(df['close'].mean(), df['close'].std(), 0.1, 1, len(df))
    return df

def add_seasonal_features_local(df):
    df['Month'] = df.index.month
    df['Day_of_Week'] = df.index.dayofweek
    df['Quarter'] = df.index.quarter
    df['Sin_Month'] = np.sin(df['Month'] * (2 * np.pi / 12))
    df['Cos_Month'] = np.cos(df['Month'] * (2 * np.pi / 12))
    return df

def create_lstm_sequences_local(X, y, seq_len):
    X_seq = []
    y_seq = []
    for i in range(len(X) - seq_len):
        X_seq.append(X.iloc[i:i + seq_len].values)
        y_seq.append(y.iloc[i + seq_len])
    return np.array(X_seq), np.array(y_seq)

class IterationLogger(Callback):
    def __init__(self):
        super().__init__()
        self.batch_count = 0
    def on_batch_end(self, batch, logs=None):
        self.batch_count += 1

class CurrenciesTrainedModelsService:
    def __init__(self):
        self.data_service = CurrenciesDataService()
        self.trained_models_repo = CurrenciesTrainedModelsRepository()
    def _load_data(self, currency_code, dataset_time=3):
        data = self.data_service.get_currency_data(currency_code=currency_code, frequency='daily', range_param='all_data')
        if not data:
            logger.error(f"No data for {currency_code}.")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df = df.set_index('timestamp').sort_index()
        cutoff_date = timezone.now() - timedelta(days=365 * dataset_time)
        df = df[df.index >= cutoff_date]
        local_timezone = timezone.get_default_timezone()
        df = df.tz_convert(local_timezone)
        df.index = df.index.normalize()
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df.dropna(subset=['close'], inplace=True)
        all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        missing_dates = all_dates.difference(df.index)
        if not missing_dates.empty:
            logger.warning(f"Missing dates for {currency_code}: {missing_dates.tolist()}")
            df = df.reindex(all_dates)
            df['close'] = df['close'].ffill()
        df.dropna(subset=['close'], inplace=True)
        df['day_of_week'] = df.index.dayofweek
        return df
    def _prepare_seasonal_data(self, df, currency_code, output_dir):
        if len(df) < 252:
            logger.warning(f"Not enough rows for full seasonal decomposition on {currency_code}. Skipping.")
            decomposition_result = None
        else:
            try:
                decomposition_result = seasonal_decompose_local(df['close'], freq=252)
            except ValueError as e:
                logger.warning(f"Decomposition failed for {currency_code}: {e}")
                decomposition_result = None
        df = add_seasonal_features_local(df)
        df = add_stochastic_features_local(df)
        if decomposition_result is not None and decomposition_result.seasonal is not None:
            seasonal_series = decomposition_result.seasonal
            seasonal_series = seasonal_series.reindex(df.index).ffill().bfill()
            df['Seasonal_Adjusted_Close'] = df['close'] / seasonal_series
        else:
            df['Seasonal_Adjusted_Close'] = df['close']
        return df
    def train_model_for_currency(self, currency_code, model_name="SeasonalRNN", param_grid=None, is_latest=True):
        if param_grid is None:
            param_grid = {}
        defaults = {
            'rnn_type': 'LSTM',
            'n_layers': 1,
            'units': 50,
            'activation': 'relu',
            'optimizer': 'adam',
            'batch_size': 32,
            'epochs': 30,
            'sequence_length': 14,
            'dropout': 0.0
        }
        for k, v in defaults.items():
            if k not in param_grid:
                param_grid[k] = v
        currency = Currency.objects.filter(code=currency_code).first()
        if not currency:
            return {"error": f"Currency {currency_code} not found."}
        df_raw = self._load_data(currency_code, dataset_time=3)
        if df_raw.empty:
            return {"error": f"No data for {currency_code}."}
        output_dir = "forecasting_outputs"
        currency_output_dir = os.path.join(output_dir, currency_code)
        os.makedirs(currency_output_dir, exist_ok=True)
        df = self._prepare_seasonal_data(df_raw.copy(), currency_code, currency_output_dir)
        visualize_data(df, currency_code, currency_output_dir)
        df['Close_Lag_7'] = df['close'].shift(7)
        df['Close_Lag_30'] = df['close'].shift(30)
        df.dropna(inplace=True)
        feature_cols = [
            'close','Close_Lag_7','Close_Lag_30','Month','Day_of_Week','Quarter','Sin_Month',
            'Cos_Month','Entropy','Random_Component','OU_Simulated','Seasonal_Adjusted_Close'
        ]
        feature_cols = [c for c in feature_cols if c in df.columns]
        X_all = df[feature_cols].copy()
        y_all = df['close'].copy()
        train_size = int(len(X_all) * 0.8)
        X_train_df = X_all.iloc[:train_size]
        X_test_df = X_all.iloc[train_size:]
        y_train_series = y_all.iloc[:train_size]
        y_test_series = y_all.iloc[train_size:]
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_train_scaled = scaler_X.fit_transform(X_train_df)
        X_test_scaled = scaler_X.transform(X_test_df)
        y_train_scaled = scaler_y.fit_transform(y_train_series.values.reshape(-1, 1)).flatten()
        y_test_scaled = scaler_y.transform(y_test_series.values.reshape(-1, 1)).flatten()
        seq_len = param_grid['sequence_length']
        X_train_seq, y_train_seq = create_lstm_sequences_local(
            pd.DataFrame(X_train_scaled, index=X_train_df.index, columns=feature_cols),
            pd.Series(y_train_scaled, index=y_train_series.index),
            seq_len
        )
        X_test_seq, y_test_seq = create_lstm_sequences_local(
            pd.DataFrame(X_test_scaled, index=X_test_df.index, columns=feature_cols),
            pd.Series(y_test_scaled, index=y_test_series.index),
            seq_len
        )
        y_train_dates = y_train_series.index[seq_len:]
        y_test_dates = y_test_series.index[seq_len:]
        if X_train_seq.shape[0] == 0 or X_test_seq.shape[0] == 0:
            logger.error(f"Insufficient sequence data for {currency_code}.")
            return {"error": f"Not enough data for {currency_code}."}
        rnn_type = param_grid['rnn_type']
        n_layers = param_grid['n_layers']
        units = param_grid['units']
        activation = param_grid['activation']
        optimizer = param_grid['optimizer']
        dropout = param_grid['dropout']
        model = Sequential()
        for i in range(n_layers):
            return_sequences = True if i < n_layers - 1 else False
            if i == 0:
                model.add(Input(shape=(seq_len, X_train_seq.shape[2])))
            if rnn_type == 'LSTM':
                model.add(LSTM(units=units, activation=activation, return_sequences=return_sequences, dropout=dropout))
            elif rnn_type == 'GRU':
                model.add(GRU(units=units, activation=activation, return_sequences=return_sequences, dropout=dropout))
            else:
                model.add(SimpleRNN(units=units, activation=activation, return_sequences=return_sequences, dropout=dropout))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer=optimizer)
        iteration_logger = IterationLogger()
        es = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)
        history = model.fit(X_train_seq, y_train_seq, epochs=param_grid['epochs'], batch_size=param_grid['batch_size'], verbose=1, callbacks=[es, iteration_logger])
        preds_test_scaled = model.predict(X_test_seq).flatten()
        mse_test = mean_squared_error(y_test_seq, preds_test_scaled)
        rmse_test = sqrt(mse_test)
        r2_test = r2_score(y_test_seq, preds_test_scaled)
        preds_test = scaler_y.inverse_transform(preds_test_scaled.reshape(-1,1)).flatten()
        actual_test = scaler_y.inverse_transform(y_test_seq.reshape(-1,1)).flatten()
        preds_train_scaled = model.predict(X_train_seq).flatten()
        preds_train = scaler_y.inverse_transform(preds_train_scaled.reshape(-1,1)).flatten()
        actual_train = scaler_y.inverse_transform(y_train_seq.reshape(-1,1)).flatten()
        model_filename = f"{currency_code.lower()}_{model_name}_{int(time.time())}.keras"
        model_path = os.path.join("saved_models", model_filename)
        os.makedirs("saved_models", exist_ok=True)
        model.save(model_path)
        param_grid["features_used"] = feature_cols
        self.trained_models_repo.create_trained_model(
            currency=currency,
            model_name=model_name,
            model_file_path=model_path,
            metrics={"mse_test": float(mse_test), "rmse_test": float(rmse_test), "r2_test": float(r2_test)},
            param_grid=param_grid,
            is_latest=is_latest
        )
        plot_results(currency_code, y_train_seq, actual_test, preds_test, y_train_dates, y_test_dates, scaler_y, currency_output_dir, 3)
        future_preds = self._recursive_predict(model, df, feature_cols, scaler_X, scaler_y, param_grid, days_ahead=14)
        self.trained_models_repo.add_predictions_bulk(currency=currency, predictions=future_preds)
        return {
            "model_path": model_path,
            "mse_test": mse_test,
            "rmse_test": rmse_test,
            "r2_test": r2_test,
            "train_samples": X_train_seq.shape[0],
            "test_samples": X_test_seq.shape[0],
            "future_preds_saved": len(future_preds)
        }

    def _recursive_predict(self, model, df, feature_cols, scaler_X, scaler_y, param_grid, days_ahead=30):
        seq_len = param_grid['sequence_length']
        X_all = scaler_X.transform(df[feature_cols].values)
        logger.info(f"Data shape for recursion: {X_all.shape}, seq_len={seq_len}")

        if X_all.shape[0] < seq_len:
            logger.error("Not enough rows for recursion.")
            return []

        # Take the last seq_len rows and reshape correctly
        current_seq = X_all[-seq_len:].reshape(1, seq_len, len(feature_cols))

        last_dt = df.index[-1]
        if timezone.is_naive(last_dt):
            last_dt = timezone.make_aware(last_dt, timezone.get_default_timezone())

        col_index = {col: i for i, col in enumerate(feature_cols)}
        results = []

        # Keep track of the last 30 predictions for lag features
        recent_predictions = list(df['close'].iloc[-30:])

        for i in range(days_ahead):
            # Predict using current sequence
            pred_scaled = model.predict(current_seq)[0, 0]
            pred_value = scaler_y.inverse_transform([[pred_scaled]])[0, 0]
            pred_dt = last_dt + timedelta(days=i + 1)
            results.append({"prediction_date": pred_dt, "predicted_value": float(pred_value)})

            # Update recent predictions list
            recent_predictions.append(pred_value)
            if len(recent_predictions) > 30:
                recent_predictions.pop(0)

            # Prepare next sequence by shifting and updating the last prediction
            next_seq = current_seq[0, 1:, :].copy()  # Remove first timestep
            next_row = next_seq[-1:, :].copy()  # Copy last row for modification

            # Update feature values for the next prediction
            for col in feature_cols:
                if col == 'close':
                    next_row[0, col_index[col]] = pred_scaled
                elif col == 'Close_Lag_7' and len(recent_predictions) >= 7:
                    # Scale the 7-day lag value
                    lag_7_value = recent_predictions[-7]
                    lag_7_scaled = scaler_y.transform([[lag_7_value]])[0, 0]
                    next_row[0, col_index[col]] = lag_7_scaled
                elif col == 'Close_Lag_30' and len(recent_predictions) >= 30:
                    # Scale the 30-day lag value
                    lag_30_value = recent_predictions[-30]
                    lag_30_scaled = scaler_y.transform([[lag_30_value]])[0, 0]
                    next_row[0, col_index[col]] = lag_30_scaled
                elif col == 'Month':
                    next_row[0, col_index[col]] = pred_dt.month
                elif col == 'Day_of_Week':
                    next_row[0, col_index[col]] = pred_dt.weekday()
                elif col == 'Quarter':
                    next_row[0, col_index[col]] = (pred_dt.month - 1) // 3 + 1
                elif col == 'Sin_Month':
                    next_row[0, col_index[col]] = np.sin(pred_dt.month * (2 * np.pi / 12))
                elif col == 'Cos_Month':
                    next_row[0, col_index[col]] = np.cos(pred_dt.month * (2 * np.pi / 12))
                elif col == 'Entropy':
                    # Approximate entropy using recent predictions
                    if recent_predictions:
                        total = sum(recent_predictions)
                        if total != 0:
                            prob = pred_value / total
                            next_row[0, col_index[col]] = -prob * np.log2(prob + 1e-10)
                elif col == 'Random_Component':
                    next_row[0, col_index[col]] = np.random.normal(0, df['close'].std())
                elif col == 'OU_Simulated':
                    # Simple OU process update
                    prev_ou = next_seq[-1, col_index[col]]
                    theta = 0.1
                    mu = df['close'].mean()
                    sigma = df['close'].std()
                    dt = 1 / 252  # Assuming daily data
                    next_row[0, col_index[col]] = prev_ou + theta * (mu - prev_ou) * dt + sigma * np.sqrt(
                        dt) * np.random.normal(0, 1)
                elif col == 'Seasonal_Adjusted_Close':
                    # Use the previous seasonal adjustment factor
                    next_row[0, col_index[col]] = pred_scaled

            # Stack the sequences and reshape
            current_seq = np.vstack([next_seq, next_row]).reshape(1, seq_len, len(feature_cols))

        return results