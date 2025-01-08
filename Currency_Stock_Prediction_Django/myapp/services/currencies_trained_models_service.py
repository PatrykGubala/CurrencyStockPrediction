import os
import time
import numpy as np
import pandas as pd
from math import sqrt
from datetime import timedelta
from django.utils import timezone
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense, Input
from tensorflow.keras.callbacks import EarlyStopping, Callback
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from itertools import product
from myapp.models import Currency
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository
from myapp.services.currencies_data_service import CurrenciesDataService, logger
from myapp.utils.plotting_utils import decompose_time_series, visualize_data, plot_results, plot_heatmap
from statsmodels.tsa.seasonal import seasonal_decompose





def ornstein_uhlenbeck_process(mu, sigma, theta, T, N):
    dt = T / N
    process = np.zeros(N)
    process[0] = mu
    for t in range(1, N):
        process[t] = process[t - 1] + theta * (mu - process[t - 1]) * dt + sigma * np.sqrt(dt) * np.random.normal(0, 1)
    return process





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

    def _create_sequences_multistep(self, features_data, target_data, seq_len, forecast_horizon):
        X, y = [], []
        for i in range(seq_len, len(features_data) - forecast_horizon + 1):
            X.append(features_data[i - seq_len:i])
            y.append(target_data[i:i + forecast_horizon])
        return np.array(X), np.array(y)

    def _train_simple_model(self, df: pd.DataFrame, params: dict):
        if len(df) < params['sequence_length'] * 2:
            return None, None, None, None, None, None, None, None, None

        seq_len = params.get('sequence_length', 14)
        forecast_horizon = 30
        feature_cols = [c for c in df.columns if c not in ['close']]

        if 'close' not in df.columns or len(feature_cols) == 0:
            return None, None, None, None, None, None, None, None, None

        scaler_features = StandardScaler()
        scaler_target = StandardScaler()
        features_scaled = scaler_features.fit_transform(df[feature_cols].astype(float).values)
        close_scaled = scaler_target.fit_transform(df['close'].astype(float).values.reshape(-1, 1))

        train_size = int(len(features_scaled) * 0.8)
        train_features = features_scaled[:train_size]
        test_features = features_scaled[train_size:]
        train_target = close_scaled[:train_size]
        test_target = close_scaled[train_size:]

        X_train_seq, y_train_seq = self._create_sequences_multistep(
            train_features, train_target, seq_len, forecast_horizon
        )
        X_test_seq, y_test_seq = self._create_sequences_multistep(
            test_features, test_target, seq_len, forecast_horizon
        )

        y_train_dates = df.index[seq_len:train_size - forecast_horizon + 1]
        y_test_dates = df.index[train_size + seq_len:len(df) - forecast_horizon + 1]

        model = Sequential()
        for layer_idx in range(params['n_layers']):
            return_sequences = (layer_idx < params['n_layers'] - 1)
            if layer_idx == 0:
                model.add(Input(shape=(seq_len, len(feature_cols))))
            if params['rnn_type'] == 'LSTM':
                model.add(LSTM(params['units'], activation=params['activation'], return_sequences=return_sequences))
            elif params['rnn_type'] == 'GRU':
                model.add(GRU(params['units'], activation=params['activation'], return_sequences=return_sequences))
            else:
                model.add(
                    SimpleRNN(params['units'], activation=params['activation'], return_sequences=return_sequences))
        model.add(Dense(forecast_horizon))  # Changed to output forecast_horizon values
        model.compile(loss='mean_squared_error', optimizer=params['optimizer'])

        es = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)
        iteration_logger = IterationLogger()
        history = model.fit(
            X_train_seq, y_train_seq,
            epochs=params['epochs'],
            batch_size=params['batch_size'],
            verbose=1,
            callbacks=[es, iteration_logger]
        )

        train_predictions = model.predict(X_train_seq)
        mse_train = mean_squared_error(y_train_seq.flatten(), train_predictions.flatten())
        rmse_train = sqrt(mse_train)

        test_predictions = model.predict(X_test_seq)
        mse_test = mean_squared_error(y_test_seq.flatten(), test_predictions.flatten())
        rmse_test = sqrt(mse_test)

        metrics = {
            "mse_train": float(mse_train),
            "rmse_train": float(rmse_train),
            "mse_test": float(mse_test),
            "rmse_test": float(rmse_test),
            "total_iterations": iteration_logger.batch_count
        }

        scaler_params = {
            'features_scaler_mean': scaler_features.mean_.tolist(),
            'features_scaler_scale': scaler_features.scale_.tolist(),
            'target_scaler_mean': scaler_target.mean_.tolist(),
            'target_scaler_scale': scaler_target.scale_.tolist()
        }
        params.update(scaler_params)

        return model, metrics, X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_target, y_train_dates, y_test_dates

    def train_model_for_currency(self, currency_code: str, model_name: str = "SeasonalRNN", param_grid=None) -> dict:
        if param_grid is None:
            param_grid = {}
        defaults = {
            'rnn_type': 'LSTM',
            'n_layers': 1,
            'units': 50,
            'activation': 'relu',
            'optimizer': 'adam',
            'batch_size': 32,
            'epochs': 5,
            'sequence_length': 14
        }
        param_grid = {**defaults, **param_grid}

        currency = Currency.objects.filter(code=currency_code).first()
        if not currency:
            return {"error": "Currency not found."}

        df = self._load_and_prepare_data(currency_code=currency_code, dataset_time=3)
        if df.empty:
            return {"error": "No data for currency."}

        model, metrics, X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_target, y_train_dates, y_test_dates = self._train_simple_model(
            df, param_grid)

        if model is None:
            return {"error": "Failed to train model."}

        # Save the model
        model_filename = f"{currency_code.lower()}_{model_name}_{int(time.time())}.keras"
        model_path = os.path.join("saved_models", model_filename)
        os.makedirs("saved_models", exist_ok=True)
        model.save(model_path)

        # Create and save the trained model record
        trained_model = self.trained_models_repo.create_trained_model(
            currency=currency,
            model_name=model_name,
            model_file_path=model_path,
            metrics=metrics,
            param_grid=param_grid,
            is_latest=True  # This will be the latest model since we're only keeping one
        )

        # Generate and save predictions
        predictions_30 = self._predict_30_days(model, df, param_grid)
        self.trained_models_repo.add_predictions_bulk(
            trained_model=trained_model,
            currency=currency,
            predictions=predictions_30
        )

        return {
            "model_id": trained_model.id,
            "model_path": model_path,
            "metrics": metrics,
            "future_predictions_saved": len(predictions_30)
        }

    def _predict_30_days(self, model, df: pd.DataFrame, params: dict):
        try:
            seq_len = params.get('sequence_length', 14)
            feature_cols = [c for c in df.columns if c not in ['close']]

            scaler_features = StandardScaler()
            scaler_target = StandardScaler()

            scaler_features.mean_ = np.array(params.get('features_scaler_mean'))
            scaler_features.scale_ = np.array(params.get('features_scaler_scale'))
            scaler_target.mean_ = np.array(params.get('target_scaler_mean'))
            scaler_target.scale_ = np.array(params.get('target_scaler_scale'))

            all_data = df[feature_cols].astype(float).values
            features_scaled = scaler_features.transform(all_data)
            last_seq = features_scaled[-seq_len:]
            current_seq = last_seq.reshape(1, seq_len, len(feature_cols))

            future_predictions_scaled = model.predict(current_seq, verbose=0)[0]
            future_predictions = scaler_target.inverse_transform(
                future_predictions_scaled.reshape(-1, 1)
            ).flatten()

            last_dt = df.index[-1]
            return [
                {
                    "prediction_date": last_dt + timedelta(days=i + 1),
                    "predicted_value": float(pred_value)
                }
                for i, pred_value in enumerate(future_predictions)
            ]
        except Exception as e:
            logger.exception(f"Error during prediction: {e}")
            return []

    def _load_and_prepare_data(self, currency_code: str, dataset_time: int = 3) -> pd.DataFrame:
        df = self.data_service.get_currency_data(currency_code=currency_code, frequency='daily', range_param='all_data')
        if not df:
            logger.error("No data for currency.")
            return pd.DataFrame()

        df = pd.DataFrame(df)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df = df.set_index('timestamp').sort_index()
        cutoff_date = timezone.now() - timedelta(days=365 * dataset_time)
        df = df[df.index >= cutoff_date]
        local_timezone = timezone.get_default_timezone()
        df = df.tz_convert(local_timezone)
        df.index = df.index.normalize()
        df['day_of_week'] = df.index.dayofweek
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])

        all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        missing_dates = all_dates.difference(df.index)
        if not missing_dates.empty:
            logger.warning(f"Missing dates for currency {currency_code}: {missing_dates.tolist()}")
            df = df.reindex(all_dates)
            df['close'].fillna(method='ffill', inplace=True)
            df['day_of_week'].fillna(method='ffill', inplace=True)

        df = df.dropna(subset=['close'])

        logger.debug(f"DataFrame after handling missing dates for {currency_code}:")
        logger.debug(df.head())
        logger.debug(df.tail())

        df = self._create_additional_features(df, currency_code)

        logger.debug(f"DataFrame after feature engineering for {currency_code}:")
        logger.debug(df.head())
        logger.debug(df.tail())

        return df

    def _create_additional_features(self, df: pd.DataFrame, currency_code: str) -> pd.DataFrame:
        close_col = 'close'
        feature_cols = []

        df[f'Close_Lag_7'] = df[close_col].shift(7)
        df[f'Close_Lag_30'] = df[close_col].shift(30)
        feature_cols += [f'Close_Lag_7', f'Close_Lag_30']

        df['MA_5'] = df[close_col].rolling(window=5).mean()
        feature_cols += ['MA_5']

        df['Month'] = df.index.month
        df['Quarter'] = df.index.quarter
        df['Sin_Month'] = np.sin(df['Month'] * (2 * np.pi / 12))
        df['Cos_Month'] = np.cos(df['Month'] * (2 * np.pi / 12))
        feature_cols += ['Month', 'Quarter', 'Sin_Month', 'Cos_Month']

        if len(df) > 0 and df['close'].sum() != 0:
            probabilities = df['close'] / df['close'].sum()
            df['Entropy'] = - (probabilities * np.log2(probabilities + 1e-10))
            feature_cols += ['Entropy']
        else:
            df['Entropy'] = 0
            feature_cols += ['Entropy']

        df['Random_Component'] = np.random.normal(0, df['close'].std(), len(df))
        feature_cols += ['Random_Component']

        df['OU_Simulated'] = ornstein_uhlenbeck_process(
            mu=df['close'].mean(),
            sigma=df['close'].std(),
            theta=0.1,
            T=1,
            N=len(df)
        )
        feature_cols += ['OU_Simulated']

        gdp_features = [col for col in df.columns if col.startswith('GDP_Growth_Percentage')]
        if gdp_features:
            feature_cols += gdp_features

        df = df.dropna()

        feature_cols = [col for col in feature_cols if col in df.columns]

        logger.debug(f"DataFrame with additional features for {currency_code}:")
        logger.debug(df.head())
        logger.debug(df.tail())

        return df

    def _enhance_data(self, df: pd.DataFrame, param_grid: dict) -> pd.DataFrame:
        if param_grid.get('use_short_term_lag'):
            lag = param_grid.get('short_term_lag', 7)
            df[f'Close_Lag_{lag}'] = df['close'].shift(lag)
        if param_grid.get('use_long_term_lag'):
            lag = param_grid.get('long_term_lag', 30)
            df[f'Close_Lag_{lag}'] = df['close'].shift(lag)
        df.dropna(inplace=True)
        return df

    def predict_with_existing_model(self, model_id: int, days_ahead: int = 30) -> dict:

        try:
            trained_model = self.trained_models_repo.get_trained_model_by_id(model_id)
            if not trained_model or not trained_model.model_file_path:
                return {"error": "Model not found or no file path available"}

            if not os.path.exists(trained_model.model_file_path):
                return {"error": "Model file not found on disk"}

            model = load_model(trained_model.model_file_path)

            currency = trained_model.currency
            df = self._load_and_prepare_data(currency.code)
            if df.empty:
                return {"error": "No data available for currency"}

            params = trained_model.param_grid or {}
            predictions = self._predict_30_days(model, df, params)

            return {
                "model_id": trained_model.id,
                "currency_code": currency.code,
                "predictions": predictions
            }

        except Exception as e:
            logger.exception(f"Error predicting with existing model: {e}")
            return {"error": f"Prediction failed: {str(e)}"}