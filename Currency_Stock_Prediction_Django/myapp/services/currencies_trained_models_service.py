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
            'sequence_length': 14,
            'use_seasonal_data': True,
            'use_short_term_lag': True,
            'short_term_lag': 7,
            'use_long_term_lag': True,
            'long_term_lag': 30
        }
        for k, v in defaults.items():
            if k not in param_grid:
                param_grid[k] = v

        currency = Currency.objects.filter(code=currency_code).first()
        if not currency:
            return {"error": "Currency not found."}

        df = self._load_and_prepare_data(currency_code=currency_code, dataset_time=3)
        if df.empty:
            return {"error": "No data for currency."}

        output_dir = "forecasting_outputs"
        currency_output_dir = os.path.join(output_dir, currency_code)
        os.makedirs(currency_output_dir, exist_ok=True)
        if not df.empty:
            df_for_plot = df.copy()
            df_for_plot["close"] = df_for_plot["close"].astype(float)
            try:
                decompose_time_series(df_for_plot, currency_code, currency_output_dir)
                visualize_data(df_for_plot, currency_code, currency_output_dir)
            except ValueError as e:
                return {"error": f"Seasonal decomposition failed: {e}"}

        df = self._enhance_data(df, param_grid)

        param_combinations = list(
            product(*{k: v if isinstance(v, list) else [v] for k, v in param_grid.items()}.values()))
        results = []
        best_mse = float('inf')
        best_params = None
        best_model = None
        best_scaler_target = None
        best_scaler_features = None

        for comb in param_combinations:
            current_params = dict(zip(param_grid.keys(), comb))
            model, metrics, X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_target, y_train_dates, y_test_dates = self._train_simple_model(
                df, current_params)
            if not model:
                continue
            results.append({
                "params": current_params,
                "metrics": metrics
            })
            if metrics['mse_test'] < best_mse:
                best_mse = metrics['mse_test']
                best_params = current_params
                best_model = model
                best_scaler_target = scaler_target
                best_scaler_features = StandardScaler()
                feature_cols = [c for c in df.columns if c not in ['close']]
                best_scaler_features.mean_ = np.array(
                    current_params.get('features_scaler_mean', [0.0 for _ in feature_cols]))
                best_scaler_features.scale_ = np.array(
                    current_params.get('features_scaler_scale', [1.0 for _ in feature_cols]))

        if best_model is None:
            return {"error": "No suitable model found."}

        param1 = 'units'
        param2 = 'sequence_length'
        units_list = sorted(set([res['params'][param1] for res in results]))
        seq_length_list = sorted(set([res['params'][param2] for res in results]))

        heatmap_data = np.full((len(seq_length_list), len(units_list)), np.nan)

        for res in results:
            units = res['params'][param1]
            seq_len = res['params'][param2]
            mse = res['metrics']['mse_test']
            i = seq_length_list.index(seq_len)
            j = units_list.index(units)
            heatmap_data[i, j] = mse

        title = f'MSE Heatmap for {currency_code}'
        x_tick_labels = units_list
        y_tick_labels = seq_length_list
        output_path = os.path.join(currency_output_dir, f'{currency_code}_mse_heatmap.png')

        plot_heatmap(heatmap_data, title, x_tick_labels, y_tick_labels, output_path)

        scaler_params = {
            'target_scaler_mean': best_scaler_target.mean_.tolist(),
            'target_scaler_scale': best_scaler_target.scale_.tolist(),
            'features_scaler_mean': best_scaler_features.mean_.tolist(),
            'features_scaler_scale': best_scaler_features.scale_.tolist()
        }
        best_params.update(scaler_params)
        model_filename = f"{currency_code.lower()}_{model_name}_{int(time.time())}.keras"
        model_path = os.path.join("saved_models", model_filename)
        os.makedirs("saved_models", exist_ok=True)
        best_model.save(model_path)
        trained_model = self.trained_models_repo.create_trained_model(
            currency=currency,
            model_name=model_name,
            model_file_path=model_path,
            metrics={"best_mse_test": best_mse},
            param_grid=best_params,
            is_latest=False
        )
        self.trained_models_repo.set_latest_model(currency, trained_model)
        predictions_14 = self._predict_14_days(best_model, df, best_params)
        self.trained_models_repo.add_predictions_bulk(trained_model=trained_model, currency=currency,
                                                      predictions=predictions_14)
        if X_test_seq is not None and X_test_seq.shape[0] > 0:
            test_preds = best_model.predict(X_test_seq).flatten()
            test_preds_inverted = best_scaler_target.inverse_transform(test_preds.reshape(-1, 1)).flatten()
            y_test_inverted = best_scaler_target.inverse_transform(y_test_seq.reshape(-1, 1)).flatten()
            plot_results(currency_code, y_train_seq, y_test_inverted, test_preds_inverted, y_train_dates, y_test_dates,
                         best_scaler_target, currency_output_dir, dataset_time=3)
        return {
            "model_id": trained_model.id,
            "model_path": model_path,
            "metrics": trained_model.metrics,
            "future_predictions_saved": len(predictions_14)
        }

    def _train_simple_model(self, df: pd.DataFrame, params: dict):
        if len(df) < params['sequence_length'] * 2:
            return None, None, None, None, None, None, None, None, None
        seq_len = params.get('sequence_length', 14)
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

        X_train_seq, y_train_seq = self._create_sequences(train_features, train_target, seq_len)
        X_test_seq, y_test_seq = self._create_sequences(test_features, test_target, seq_len)
        y_train_dates = df.index[seq_len:train_size]
        y_test_dates = df.index[train_size + seq_len:]

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
                model.add(SimpleRNN(params['units'], activation=params['activation'], return_sequences=return_sequences))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer=params['optimizer'])

        es = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)
        iteration_logger = IterationLogger()
        history = model.fit(X_train_seq, y_train_seq, epochs=params['epochs'], batch_size=params['batch_size'],
                            verbose=1, callbacks=[es, iteration_logger])

        preds_train = model.predict(X_train_seq).flatten()
        mse_train = mean_squared_error(y_train_seq, preds_train)
        rmse_train = sqrt(mse_train)

        preds_test = model.predict(X_test_seq).flatten()
        mse_test = mean_squared_error(y_test_seq, preds_test)
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
            'features_scaler_scale': scaler_features.scale_.tolist()
        }
        params.update(scaler_params)

        return model, metrics, X_train_seq, y_train_seq, X_test_seq, y_test_seq, scaler_target, y_train_dates, y_test_dates

    def _create_sequences(self, features_data, target_data, seq_len):
        X, y = [], []
        for i in range(seq_len, len(features_data)):
            X.append(features_data[i - seq_len:i])
            y.append(target_data[i])
        return np.array(X), np.array(y)

    def update_existing_model(self, model_id: int, param_grid=None) -> dict:
        if param_grid is None:
            param_grid = {}
        trained_model = self.trained_models_repo.get_trained_model_by_id(model_id)
        if not trained_model:
            return {"error": "Trained model not found in DB."}
        if not trained_model.model_file_path or not os.path.exists(trained_model.model_file_path):
            return {"error": "Model file not found on disk."}
        model = load_model(trained_model.model_file_path)
        currency = trained_model.currency
        new_data = self.data_service.get_currency_data(currency_code=currency.code, frequency='daily', range_param='last_7_days')
        if not new_data:
            return {"info": "No new data to train on."}
        new_df = pd.DataFrame(new_data)
        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms', utc=True)
        new_df = new_df.set_index('timestamp').sort_index()
        new_df = new_df.tz_convert(timezone.get_default_timezone())
        new_df.index = new_df.index.normalize()
        new_df['day_of_week'] = new_df.index.dayofweek
        new_df['close'] = pd.to_numeric(new_df['close'], errors='coerce')
        new_df = new_df.dropna(subset=['close'])
        new_df = self._create_additional_features(new_df, currency.code)

        defaults = {
            'sequence_length': trained_model.param_grid.get('sequence_length', 14),
            'use_seasonal_data': trained_model.param_grid.get('use_seasonal_data', False),
            'use_short_term_lag': trained_model.param_grid.get('use_short_term_lag', False),
            'short_term_lag': trained_model.param_grid.get('short_term_lag', 7),
            'use_long_term_lag': trained_model.param_grid.get('use_long_term_lag', False),
            'long_term_lag': trained_model.param_grid.get('long_term_lag', 30)
        }
        for k, v in defaults.items():
            if k not in param_grid:
                param_grid[k] = v

        new_df = self._enhance_data(new_df, param_grid)
        if new_df.empty:
            return {"info": "No new data to train on."}

        seq_len = param_grid.get('sequence_length', 14)
        feature_cols = [c for c in new_df.columns if c not in ['close']]
        if 'close' not in new_df.columns or len(feature_cols) == 0 or len(new_df) < seq_len:
            return {"info": "Not enough new data to form sequences."}

        scaler_target = StandardScaler()
        scaler_target.mean_ = np.array(trained_model.param_grid.get('target_scaler_mean', [0.0]))
        scaler_target.scale_ = np.array(trained_model.param_grid.get('target_scaler_scale', [1.0]))

        scaler_features = StandardScaler()
        f_mean = trained_model.param_grid.get('features_scaler_mean', [0.0 for _ in feature_cols])
        f_scale = trained_model.param_grid.get('features_scaler_scale', [1.0 for _ in feature_cols])
        if len(f_mean) != len(feature_cols):
            return {"info": "Feature mismatch."}
        scaler_features.mean_ = np.array(f_mean)
        scaler_features.scale_ = np.array(f_scale)

        data = new_df[feature_cols].astype(float).values
        target_scaled = scaler_target.transform(new_df['close'].astype(float).values.reshape(-1, 1)).flatten()
        features_scaled = scaler_features.transform(data)

        X_list, y_list = [], []
        for i in range(seq_len, len(features_scaled)):
            X_list.append(features_scaled[i - seq_len:i, :])
            y_list.append(target_scaled[i])
        X_arr = np.array(X_list)
        y_arr = np.array(y_list)

        if len(X_arr) == 0:
            return {"info": "Not enough new data to form sequences."}

        es = EarlyStopping(monitor='loss', patience=1, restore_best_weights=True)
        iteration_logger = IterationLogger()
        model.fit(X_arr, y_arr, epochs=3, batch_size=trained_model.param_grid.get('batch_size', 32),
                  verbose=1, callbacks=[es, iteration_logger])
        model.save(trained_model.model_file_path)
        updated_preds = self._predict_14_days(model, new_df, trained_model.param_grid)
        self.trained_models_repo.add_predictions_bulk(trained_model=trained_model, currency=currency, predictions=updated_preds)
        return {
            "model_id": trained_model.id,
            "updated_on": str(timezone.now()),
            "new_predictions_saved": len(updated_preds),
            "additional_iterations": iteration_logger.batch_count
        }

    def _predict_14_days(self, model, df: pd.DataFrame, params: dict):
        try:
            seq_len = params.get('sequence_length', 14)
            scaler_target = StandardScaler()
            scaler_target.mean_ = np.array(params.get('target_scaler_mean', [0.0]))
            scaler_target.scale_ = np.array(params.get('target_scaler_scale', [1.0]))
            feature_cols = [c for c in df.columns if c not in ['close']]
            if len(feature_cols) == 0 or len(df) < seq_len:
                logger.error("Insufficient feature columns or data length for prediction.")
                return []
            scaler_features = StandardScaler()
            f_mean = params.get('features_scaler_mean', [0.0 for _ in feature_cols])
            f_scale = params.get('features_scaler_scale', [1.0 for _ in feature_cols])
            if len(f_mean) != len(feature_cols):
                logger.error("Feature scaler mean length mismatch.")
                return []
            scaler_features.mean_ = np.array(f_mean)
            scaler_features.scale_ = np.array(f_scale)
            all_data = df[feature_cols].astype(float).values
            features_scaled = scaler_features.transform(all_data)
            last_seq = features_scaled[-seq_len:].copy()
            predictions = []
            current_seq = last_seq.reshape(1, seq_len, len(feature_cols))
            last_dt = df.index[-1]
            if timezone.is_naive(last_dt):
                last_dt = timezone.make_aware(last_dt, timezone.get_default_timezone())
            feature_indices = {col: idx for idx, col in enumerate(feature_cols)}

            for day in range(14):
                next_pred_scaled = model.predict(current_seq, verbose=0)[0, 0]
                next_pred = scaler_target.inverse_transform([[next_pred_scaled]])[0, 0]
                predictions.append(float(next_pred))

                new_input = current_seq[:, 1:, :].copy()
                new_input[0, -1, feature_indices['close']] = next_pred_scaled

                new_day_of_week = (last_dt.dayofweek + day + 1) % 7
                if 'day_of_week' in feature_indices:
                    new_input[0, -1, feature_indices['day_of_week']] = new_day_of_week

                current_seq = new_input

            results = []
            for i, pred_value in enumerate(predictions):
                pred_dt = last_dt + timedelta(days=i + 1)
                results.append({
                    "prediction_date": pred_dt,
                    "predicted_value": pred_value
                })
            return results
        except Exception as e:
            logger.exception(f"Error during prediction: {e}")
            return []

    def predict_with_existing_model(self, model_id: int) -> dict:
        trained_model = self.trained_models_repo.get_trained_model_by_id(model_id)
        if not trained_model or not trained_model.model_file_path:
            return {"error": "Model not found or no file_path"}
        if not os.path.exists(trained_model.model_file_path):
            return {"error": "Model file not found on disk"}
        model = load_model(trained_model.model_file_path)
        tm = self.trained_models_repo.get_trained_model_by_id(model_id)
        if not tm:
            return {"error": "No model record in DB"}
        currency = tm.currency
        df = self._load_data(currency)
        if df.empty:
            return {"error": "No data for currency"}
        params = tm.param_grid or {}
        preds = self._predict_14_days(model, df, params)
        return {
            "model_id": trained_model.id,
            "predictions": preds
        }

    def _load_data(self, currency: Currency) -> pd.DataFrame:
        data = self.data_service.get_currency_data(
            currency_code=currency.code,
            frequency='daily',
            range_param='all_data'
        )
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df = df.set_index('timestamp').sort_index()
        local_timezone = timezone.get_default_timezone()
        df = df.tz_convert(local_timezone)
        df.index = df.index.normalize()
        df['day_of_week'] = df.index.dayofweek
        df['close'] = pd.to_numeric(df['close'], errors='coerce')

        all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        missing_dates = all_dates.difference(df.index)
        if not missing_dates.empty:
            logger.warning(f"Missing dates for currency {currency.code}: {missing_dates.tolist()}")
            df = df.reindex(all_dates)
            df['close'].fillna(method='ffill', inplace=True)
            df['day_of_week'].fillna(method='ffill', inplace=True)

        df = df.dropna(subset=['close'])

        df = self._create_additional_features(df, currency.code)

        return df

    def train_models_for_all_currencies(self) -> dict:
        currencies = Currency.objects.filter(data_availability=True)
        if not currencies:
            return {"error": "No currencies to train."}
        results = []
        for cur in currencies:
            res = self.train_model_for_currency(currency_code=cur.code, model_name="SeasonalRNN", param_grid={})
            results.append({cur.code: res})
        return {"train_all_results": results}
