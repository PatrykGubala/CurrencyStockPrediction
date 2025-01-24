import os
import shutil

import numpy as np
import pandas as pd
import logging

import pytz
from django.utils import timezone
from itertools import product

from sklearn.ensemble import RandomForestRegressor

from myapp.services.currencies_data_service import CurrenciesDataService
from myapp.repositories.currencies_data_repository import CurrenciesDataRepository

from keras.src.optimizers import Adam
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from tensorflow.keras.regularizers import L1L2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense, Dropout
from tensorflow.python.keras.callbacks import Callback
from myapp.repositories.currencies_trained_models_repository import CurrenciesTrainedModelsRepository
from myapp.models import CurrenciesData, Currency
from myapp.utils.plotting_utils import (
    plot_training_loss_by_rnn_type,
    plot_validation_loss_by_rnn_type,
    plot_residuals_histogram,
    plot_residuals_over_time,
    plot_scatter_actual_vs_predicted,
    plot_results,
    plot_heatmap,
    plot_line_graph,
    decompose_time_series
)
import matplotlib.pyplot as plt
import json
import uuid

class ModelCounter:
    def __init__(self, total):
        self.count = 0
        self.total = total
    def increment(self):
        self.count += 1
        return self.count

class PrintMetricsCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        print(f"loss={logs.get('loss')}, mae={logs.get('mae')}, val_loss={logs.get('val_loss')}, val_mae={logs.get('val_mae')}")

def print_debug_data(title, data):
    import logging
    logging.info(f"===== {title} =====")
    logging.info(f"Type: {type(data)}, Shape: {getattr(data, 'shape', None)}")
    try:
        if hasattr(data, "describe"):
            desc = data.describe(include="all") if len(data) > 0 else None
            logging.info(f"Describe:\n{desc}")
        if hasattr(data, "min") and hasattr(data, "max") and hasattr(data, "mean"):
            logging.info(f"Min: {data.min()} Max: {data.max()} Mean: {data.mean()}")
    except:
        pass
    if isinstance(data, (list, tuple, dict)):
        try:
            logging.info(f"First items: {str(list(data)[:3])}")
        except:
            logging.info(f"Value: {data}")
    elif hasattr(data, "head"):
        logging.info(f"Head:\n{data.head(3)}\nTail:\n{data.tail(3)}")
    else:
        try:
            if len(data) > 5:
                logging.info(f"First items: {data[:3]}\nLast items: {data[-3:]}")
            else:
                logging.info(f"All data: {data}")
        except:
            logging.info(f"Value: {data}")

def create_rnn_model(rnn_type='LSTM', number_of_layers=1, units=50, activation='tanh',
                     optimizer='adam', input_shape=None, dropout_rate=0.2, horizon=30,
                     recurrent_dropout=0.1, l1_reg=0.01, l2_reg=0.01):
    if input_shape is None:
        raise ValueError("input_shape must be specified")


    regularizer = None
    if l1_reg > 0 or l2_reg > 0:
        regularizer = L1L2(l1=l1_reg, l2=l2_reg)

    model = Sequential()
    for layer_index in range(number_of_layers):
        return_sequences = layer_index < number_of_layers - 1
        if rnn_type == 'LSTM':
            model.add(LSTM(units=units,activation=activation,
                input_shape=input_shape,kernel_regularizer=regularizer,
                dropout=dropout_rate,recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
        elif rnn_type == 'GRU':
            model.add(GRU(units=units,activation=activation,
                input_shape=input_shape,kernel_regularizer=regularizer,
                dropout=dropout_rate,recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
        else:
            model.add(SimpleRNN(units=units,activation=activation,
                input_shape=input_shape,kernel_regularizer=regularizer,
                dropout=dropout_rate,recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
    model.add(Dense(horizon))
    model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mae'])
    return model

def create_lstm_sequences_multistep(X, y, sequence_length=30, horizon=30):
    if len(X) < sequence_length + horizon:
        raise ValueError("Not enough data points for sequence creation")
    X_seq = []
    y_seq = []
    for i in range(len(X) - sequence_length - horizon + 1):
        seq_X = X.iloc[i: i + sequence_length].values
        seq_y = y.iloc[i + sequence_length: i + sequence_length + horizon].values
        if np.any(np.isnan(seq_X)) or np.any(np.isnan(seq_y)):
            continue
        X_seq.append(seq_X)
        y_seq.append(seq_y)
    return np.array(X_seq), np.array(y_seq)

def add_stochastic_features(dataframe, currency_code):
    close_column = f'Close_{currency_code}'

    if not np.issubdtype(dataframe[close_column].dtype, np.floating):
        dataframe[close_column] = dataframe[close_column].astype(float)
    dataframe['Random_Component'] = np.random.normal(0, dataframe[close_column].std(), len(dataframe))
    def ornstein_uhlenbeck_process(mu, sigma, theta, T, N):
        dt = T / N
        process = np.zeros(N)
        process[0] = mu
        for t in range(1, N):
            process[t] = process[t - 1] + theta * (mu - process[t - 1]) * dt + sigma * np.sqrt(dt) * np.random.normal(0, 1)
        return process
    dataframe['OU_Simulated'] = ornstein_uhlenbeck_process(
        mu=float(dataframe[close_column].mean()),
        sigma=float(dataframe[close_column].std()),
        theta=0.1,
        T=1,
        N=len(dataframe)
    )
    return dataframe

def add_trend_feature(dataframe, currency_code, window=30):
    close_column = f'Close_{currency_code}'
    dataframe[f'Trend_{currency_code}'] = dataframe[close_column].rolling(window=window).apply(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x)==window else np.nan
    )
    return dataframe

def add_seasonal_trend_features(dataframe, decomposition_result, currency_code):
    close_column = f'Close_{currency_code}'
    dataframe[f'Seasonal_Component_{currency_code}'] = decomposition_result.seasonal
    dataframe[f'Trend_Component_{currency_code}'] = decomposition_result.trend
    dataframe[f'Deseasonalized_Close_{currency_code}'] = dataframe[close_column] - decomposition_result.seasonal
    return dataframe

def create_seasonal_features(dataframe, currency_code):
    dataframe['Month'] = dataframe.index.month
    dataframe['Day_of_Week'] = dataframe.index.dayofweek
    dataframe['Quarter'] = dataframe.index.quarter
    dataframe['Sin_Month'] = np.sin(dataframe['Month'] * (2 * np.pi / 12))
    dataframe['Cos_Month'] = np.cos(dataframe['Month'] * (2 * np.pi / 12))
    return dataframe

def apply_seasonal_adjustment(dataframe, decomposition_result, currency_code):
    close_column = f'Close_{currency_code}'
    adjusted_dataframe = dataframe.copy()
    adjusted_dataframe['Seasonal_Adjusted_Close'] = dataframe[close_column] / decomposition_result.seasonal
    return adjusted_dataframe

def prepare_seasonal_data(dataframe, currency_code, output_directory):
    for column in dataframe.columns:
        if dataframe[column].dtype.name == 'object':
            try:
                dataframe[column] = dataframe[column].astype(float)
            except (ValueError, TypeError):
                continue
    decomposition = decompose_time_series(dataframe, currency_code, output_directory)
    dataframe = create_seasonal_features(dataframe, currency_code)
    dataframe = add_stochastic_features(dataframe, currency_code)
    dataframe = add_seasonal_trend_features(dataframe, decomposition, currency_code)
    dataframe = add_trend_feature(dataframe, currency_code, window=30)
    return dataframe

def filter_last_n_years(dataframe, number_of_years=6):
    if not isinstance(dataframe.index, pd.DatetimeIndex):
        return dataframe
    end_date = dataframe.index.max()
    start_date = end_date - pd.DateOffset(years=number_of_years)
    return dataframe.loc[(dataframe.index >= start_date) & (dataframe.index <= end_date)]

def feature_selection_k_best(X, y, k_best_features=5):
    selector = SelectKBest(f_regression, k=k_best_features)
    X_new = selector.fit_transform(X, y)
    selected_features = X.columns[selector.get_support(indices=True)]
    return pd.DataFrame(X_new, columns=selected_features, index=X.index), selected_features

def feature_selection_rfe(X, y, k_best_features=5):
    model = RandomForestRegressor(n_estimators=100, random_state=1)
    model.fit(X, y)
    importances = model.feature_importances_
    feature_importances = pd.Series(importances, index=X.columns)
    selected_features = feature_importances.sort_values(ascending=False).head(k_best_features).index
    X_new = X[selected_features]
    return pd.DataFrame(X_new, columns=selected_features, index=X.index), selected_features

def make_predictions(best_model, X_test_seq, y_test_seq, scaler_y):
    predictions = []
    actuals = y_test_seq.reshape(-1)
    print_debug_data("X_test_seq Shape", X_test_seq)
    print_debug_data("y_test_seq Shape", y_test_seq)
    for i in range(len(X_test_seq)):
        curr_pred = best_model.predict(X_test_seq[i:i + 1], verbose=0)
        predictions.extend(curr_pred.flatten())
    predictions = np.array(predictions)
    if len(predictions) != len(actuals):
        raise ValueError("Mismatch between the number of predictions and actual values")
    predictions_final = scaler_y.inverse_transform(predictions.reshape(-1, 1)).flatten()
    y_test_plot = scaler_y.inverse_transform(actuals.reshape(-1, 1)).flatten()

    if predictions_final.shape != y_test_plot.shape:
        raise ValueError(f"Shape mismatch: predictions {predictions_final.shape} vs actuals {y_test_plot.shape}")
    return predictions_final, y_test_plot

def create_future_sequence(last_known_data, sequence_length, n_features):
    future_sequence = last_known_data[-sequence_length:].reshape(1, sequence_length, n_features)
    return future_sequence

def generate_future_predictions(model, initial_sequence, scaler_y, horizon):
    logging.info("===== generate_future_predictions (Direct Multi-Step) =====")
    next_pred = model.predict(initial_sequence, verbose=0)
    future_predictions = next_pred.flatten()
    future_predictions_transformed = scaler_y.inverse_transform(
        future_predictions.reshape(-1, 1)
    ).flatten()
    logging.info(f"Future raw preds: {future_predictions[:5]}")
    logging.info(f"Future inverted preds: {future_predictions_transformed[:5]}")
    return future_predictions_transformed

def make_future_predictions(best_model, last_seq_full, scaler_y, scaler_X, selected_features,  prediction_time, sequence_length):
    inverted_array = scaler_X.inverse_transform(last_seq_full)
    inverted_df = pd.DataFrame(inverted_array, columns=selected_features, index=last_seq_full.index)
    print_debug_data("Last sequence for future predictions (last_seq_full) [inverted]", inverted_df)

    n_features = last_seq_full.shape[1]
    initial_sequence = last_seq_full.values.reshape(1, sequence_length, n_features)

    print_debug_data("Initial sequence for future predictions (reshaped last_seq_full)", initial_sequence)
    next_pred = best_model.predict(initial_sequence, verbose=0)

    future_predictions = next_pred.flatten()
    future_predictions_transformed = scaler_y.inverse_transform(
        future_predictions.reshape(-1, 1)
    ).flatten()

    return future_predictions_transformed

def train_rnn_models(X_train_seq, y_train_seq, X_val_seq, y_val_seq, sequence_length, param_grid, model_counter, total_models, horizon, scaler_y, output_directory, currency_code):
    results = []
    histories = []
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    param_combinations = list(product(*values))

    best_val_loss = float('inf')
    best_model = None
    best_params = None

    for parameters in param_combinations:
        param_dict = dict(zip(keys, parameters))
        current_model_number = model_counter.increment()
        print(f"Model {current_model_number} / {model_counter.total} param_grid: {param_dict}")
        model = create_rnn_model(
            rnn_type=param_dict['rnn_type'],
            number_of_layers=param_dict['n_layers'],
            units=param_dict['units'],
            activation=param_dict['activation'],
            input_shape=(sequence_length, X_train_seq.shape[2]),
            dropout_rate=param_dict.get('dropout_rate', 0.2),
            horizon=horizon
        )
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0)
        history = model.fit(
            X_train_seq,
            y_train_seq,
            validation_data=(X_val_seq, y_val_seq),
            epochs=param_dict['epochs'],
            batch_size=param_dict['batch_size'],
            callbacks=[early_stopping, PrintMetricsCallback()],
            verbose=1
        )
        val_preds = model.predict(X_val_seq)
        val_preds = val_preds.flatten()
        val_preds_inverted = scaler_y.inverse_transform(val_preds.reshape(-1, 1)).flatten()
        actual_inverted = scaler_y.inverse_transform(y_val_seq.reshape(-1, 1)).flatten()
        plot_path = os.path.join(output_directory,
                                 f'{currency_code}_model_{current_model_number}_val_actual_vs_predicted.png')
        plot_scatter_actual_vs_predicted(actual_inverted, val_preds_inverted, plot_path)

        val_loss = min(history.history['val_loss'])
        val_preds = model.predict(X_val_seq)
        val_r2 = r2_score(y_val_seq.flatten(), val_preds.flatten())
        results.append({
            'params': param_dict,
            'val_loss': val_loss,
            'val_r2': val_r2,
            'history': history
        })
        histories.append(history)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model = model
            best_params = param_dict
            best_model_path = os.path.join(output_directory, f'best_model_{currency_code}.h5')
            best_model.save(best_model_path, save_format='h5')
            print(f"Nowy najlepszy model zapisany z parametrami: {best_params} o val_loss: {val_loss}")
    return results, histories, param_combinations, best_model, best_params

def visualize_data(data, currency_code, output_directory):
    close_column = f'Close_{currency_code}'
    plot_path = os.path.join(output_directory, f'{currency_code}_closing_prices.png')
    plot_line_graph(
        x_data_list=[data.index], y_data_list=[data[close_column]],
        labels=[close_column], title=f'{currency_code} Closing Prices',
        x_label='Date', y_label='Price', legend_labels=[close_column],
        output_path=plot_path, figure_size=(14, 7)
    )
    numeric_data = data.select_dtypes(include=[np.number])
    correlation = numeric_data.corr()
    heatmap_path = os.path.join(output_directory, f'{currency_code}_correlation_heatmap.png')


def load_data_from_db(currency_code):
    repository = CurrenciesDataRepository()
    currency = repository.get_currency_by_code(currency_code)
    if not currency:
        return pd.DataFrame()
    service = CurrenciesDataService()
    currency_data = service.get_currency_data(currency_code, frequency="daily", range_param="all_data")
    if not currency_data:
        return pd.DataFrame()
    latest_record = repository.get_latest_record(currency)
    if latest_record:
        latest_data = {
            'timestamp': int(latest_record.timestamp.timestamp() * 1000),
            'close': str(latest_record.close_price),
            'open': str(latest_record.open_price),
            'high': str(latest_record.high_price),
            'low': str(latest_record.low_price),
            'volume': str(latest_record.volume)
        }
        latest_date = latest_record.timestamp.date()
        existing_dates = [pd.to_datetime(d['timestamp'], unit='ms').date() for d in currency_data]
        if latest_date not in existing_dates:
            currency_data.append(latest_data)

    df = pd.DataFrame(currency_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'].apply(lambda x: x / 1000), unit='s', utc=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)

    numeric_columns = ['close', 'open', 'high', 'low', 'volume']
    for col in numeric_columns:
        df[col] = df[col].astype(float)

    df.rename(columns={'close': f'Close_{currency_code}'}, inplace=True)
    return df

class CurrenciesTrainedModelsService:
    def __init__(self):
        self.repository = CurrenciesTrainedModelsRepository()
    def train_and_forecast(self, currency_code, param_grid, sequence_length, dataset_time, prediction_time,
                           short_term_lag, long_term_lag, scaling_method, output_directory):
        print_debug_data("train_and_forecast START for currency", currency_code)
        currency_instance = self.repository.get_currency_by_code(currency_code)
        if not currency_instance:
            return {"status": "error", "message": "Currency not found"}
        horizon = prediction_time
        self.repository.mark_all_as_not_latest(currency_instance)
        self.repository.clear_old_predictions(currency_instance)
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        os.makedirs(output_directory)

        data = load_data_from_db(currency_code)
        print_debug_data("Data loaded from DB", data)
        if data.empty:
            return {"status": "error", "message": f"No data available in DB for {currency_code}"}
        data = data.resample('D').last().ffill()
        data = data.dropna()
        data = data[data.index.notnull()]
        print_debug_data("Data after asfreq/ffill/dropna", data)
        data = prepare_seasonal_data(data, currency_code, output_directory)
        print_debug_data("Data after prepare_seasonal_data", data)
        filtered_data = filter_last_n_years(data, number_of_years=dataset_time)
        print_debug_data("Filtered data (last n years)", filtered_data)
        if filtered_data.empty:
            return {"status": "error", "message": f"Filtered data for {currency_code} is empty"}
        scaler_map = {
            'standard': StandardScaler(),
            'normalize': MinMaxScaler(),
            'robust': RobustScaler()
        }
        scaler_X = scaler_map.get(scaling_method, StandardScaler())
        scaler_y = StandardScaler()
        X, y = self.create_features_and_target(filtered_data, currency_code, short_term_lag, long_term_lag)
        print_debug_data("Features X", X)
        print_debug_data("Target y", y)
        if X.empty or y.empty:
            return {"status": "error", "message": f"No features/target available for {currency_code}"}
        string_columns = X.select_dtypes(include=['object', 'string']).columns
        if len(string_columns) > 0:
            X.drop(columns=string_columns, errors='ignore', inplace=True)
        corr_matrix_before = X.corr()
        heatmap_path_before = os.path.join(output_directory, f'{currency_code}_correlation_heatmap_before.png')
        plot_heatmap(
            data=corr_matrix_before.values,
            title=f'{currency_code} Correlation Before Feature Selection',
            x_tick_labels=corr_matrix_before.columns,
            y_tick_labels=corr_matrix_before.index,
            output_path=heatmap_path_before,
            annotate=True
        )
        X_fs, selected_features = feature_selection_rfe(X, y, k_best_features=6)
        print_debug_data("Selected features (X_fs)", X_fs)
        corr_matrix_after = X_fs.corr()
        heatmap_path_after = os.path.join(output_directory, f'{currency_code}_correlation_heatmap_after.png')
        plot_heatmap(
            data=corr_matrix_after.values,
            title=f'{currency_code} Correlation After Feature Selection',
            x_tick_labels=corr_matrix_after.columns,
            y_tick_labels=corr_matrix_after.index,
            output_path=heatmap_path_after,
            annotate=True
        )
        y = y.loc[X_fs.index]
        visualize_df = pd.concat([X_fs, y.rename('Close_' + currency_code)], axis=1)
        plot_line_graph(
            x_data_list=[visualize_df.index],
            y_data_list=[visualize_df['Close_' + currency_code]],
            labels=['Close_' + currency_code],
            title=f'{currency_code} Closing Prices',
            x_label='Date',
            y_label='Price',
            legend_labels=['Close_' + currency_code],
            output_path=os.path.join(output_directory, f'{currency_code}_closing_prices.png'),
            figure_size=(14, 7)
        )
        test_period_days = prediction_time
        train_size = len(X_fs) - test_period_days - sequence_length
        if train_size <= 0:
            return {"status": "error", "message": f"Not enough data to train for {currency_code}"}

        X_train_df = X_fs.iloc[:train_size + sequence_length]
        X_val_df = X_fs.iloc[train_size:]
        y_train_series = y.iloc[:train_size + sequence_length]
        y_val_series = y.iloc[train_size:]

        full_data_scaler_X = scaler_X
        full_data_scaler_X.fit(X_fs)

        train_scaled = full_data_scaler_X.transform(X_train_df)
        val_scaled = full_data_scaler_X.transform(X_val_df)
        full_data_scaler_y = scaler_y
        full_data_scaler_y.fit(y.values.reshape(-1, 1))
        y_train_scaled = full_data_scaler_y.transform(y_train_series.values.reshape(-1, 1)).flatten()
        y_val_scaled = full_data_scaler_y.transform(y_val_series.values.reshape(-1, 1)).flatten()
        train_scaled_df = pd.DataFrame(train_scaled, columns=selected_features, index=X_train_df.index)
        val_scaled_df = pd.DataFrame(val_scaled, columns=selected_features, index=X_val_df.index)
        y_train_series = pd.Series(y_train_scaled, index=y_train_series.index)
        y_val_series = pd.Series(y_val_scaled, index=y_val_series.index)
        print_debug_data("train_scaled_df", train_scaled_df)
        print_debug_data("val_scaled_df", val_scaled_df)
        print_debug_data("y_train_series scaled", y_train_series)
        print_debug_data("y_val_series scaled", y_val_series)
        X_train_seq, y_train_seq = create_lstm_sequences_multistep(train_scaled_df, y_train_series, sequence_length, horizon)
        X_val_seq, y_val_seq = create_lstm_sequences_multistep(val_scaled_df, y_val_series, sequence_length, horizon)
        print_debug_data("X_train_seq", X_train_seq)
        print_debug_data("y_train_seq", y_train_seq)
        print_debug_data("X_val_seq", X_val_seq)
        print_debug_data("y_val_seq", y_val_seq)
        if len(X_val_seq) == 0:
            return {"status": "error", "message": f"Not enough validation sequences after adjustment for {currency_code}"}
        total_models_count = 1
        for v in param_grid.values():
            total_models_count *= len(v)
        model_counter = ModelCounter(total_models_count)
        results, histories, param_combinations, best_model, best_params = train_rnn_models(
            X_train_seq=X_train_seq,
            y_train_seq=y_train_seq,
            X_val_seq=X_val_seq,
            y_val_seq=y_val_seq,
            sequence_length=sequence_length,
            param_grid=param_grid,
            model_counter=model_counter,
            total_models=total_models_count,
            horizon=horizon,
            scaler_y=full_data_scaler_y,
            output_directory=output_directory,
            currency_code=currency_code
        )
        plot_training_loss_by_rnn_type(results, currency_code, output_directory)
        plot_validation_loss_by_rnn_type(results, currency_code, output_directory)

        predictions, y_val_plot = make_predictions(best_model, X_val_seq, y_val_seq, full_data_scaler_y)
        y_test_dates = y_val_series.index[sequence_length:]
        if len(predictions) == len(y_test_dates):
            residuals = y_val_plot - predictions
            hist_path = os.path.join(output_directory, f'{currency_code}_residuals_hist.png')
            time_path = os.path.join(output_directory, f'{currency_code}_residuals_over_time.png')
            scatter_path = os.path.join(output_directory, f'{currency_code}_actual_vs_predicted_scatter.png')
            y_train_plot = full_data_scaler_y.inverse_transform(y_train_series.values.reshape(-1, 1)).flatten()
            y_test_dates = y_val_series.index[sequence_length:]
            plot_residuals_histogram(residuals, hist_path)
            plot_residuals_over_time(y_test_dates, residuals, time_path)
            plot_scatter_actual_vs_predicted(y_val_plot, predictions, scatter_path)
            plot_results(currency_code, y_train_plot, y_val_plot, predictions,
                         y_train_series.index, y_test_dates, output_directory, dataset_time)
            mse = mean_squared_error(y_val_plot, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_val_plot, predictions)
            results_csv = os.path.join(output_directory, f'{currency_code}_mse_results.csv')
            sorted_results = sorted(results, key=lambda x: x['val_loss'])
            rows = []
            rank_number = 1
            for res in sorted_results:
                params_str = '; '.join([f"{k}: {v}" for k, v in res['params'].items()])
                mean_mse_val = res['val_loss']
                rmse_val = np.sqrt(mean_mse_val)
                val_r2_val = res['val_r2']
                rows.append([rank_number, params_str, mean_mse_val, rmse_val, val_r2_val])
                rank_number += 1
            df_results = pd.DataFrame(rows, columns=["Rank", "Parameters", "Mean MSE", "RMSE", "R2"])
            df_results.to_csv(results_csv, index=False)
            model_filename = f"{currency_code}_{str(uuid.uuid4())}.h5"
            model_file_path = os.path.join(output_directory, model_filename)
            best_model.save(model_file_path, save_format='keras')
            metrics_dict = {
                "mse": float(mse) if np.isfinite(mse) else None,
                "rmse": float(rmse) if np.isfinite(rmse) else None,
                "r2": float(r2) if np.isfinite(r2) else None,
                "val_loss": float(mean_mse_val) if np.isfinite(mean_mse_val) else None,
                "val_r2": float(r2) if np.isfinite(r2) else None
            }
            param_grid_json = json.dumps(best_params)
            self.repository.create_trained_model(
                currency=currency_instance,
                model_name="AdvancedRNN",
                model_file_path=model_file_path,
                metrics=metrics_dict,
                param_grid=param_grid_json,
                is_latest=True
            )
            predictions_map = list(zip(y_test_dates, predictions))
            full_scaled_df = pd.DataFrame(
                full_data_scaler_X.transform(X_fs),
                columns=selected_features,
                index=X_fs.index
            )
            last_seq_full = full_scaled_df.iloc[-sequence_length:]
            future_preds_inverted = make_future_predictions(
                best_model=best_model,
                last_seq_full=last_seq_full,
                scaler_y=full_data_scaler_y,
                scaler_X=full_data_scaler_X,
                selected_features=selected_features,
                prediction_time=prediction_time,
                sequence_length=sequence_length
            )
            last_date = filtered_data.index.max()
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=prediction_time,
                freq='D'
            )
            predictions_map_future = list(zip(future_dates, future_preds_inverted))
            future_predictions_serializable = [
                (date.isoformat(), float(value))
                for date, value in predictions_map_future
            ]
            self.repository.store_predictions(currency_instance, predictions_map_future)
            return {
                "status": "success",
                "message": "Model trained and predictions saved",
                "metrics": metrics_dict,
                "future_predictions": future_predictions_serializable
            }
        return {"status": "error", "message": "Lengths do not match in final predictions"}



    def create_features_and_target(self, dataframe, currency_code, short_term_lag, long_term_lag):
        print_debug_data("create_features_and_target input dataframe", dataframe)
        if dataframe is None or dataframe.empty:
            return pd.DataFrame(), pd.Series()
        data_copy = dataframe.copy()
        close_column = f'Close_{currency_code}'
        if close_column not in data_copy.columns:
            return pd.DataFrame(), pd.Series()
        data_copy[f'Close_Lag_{short_term_lag}'] = data_copy[close_column].shift(short_term_lag)
        data_copy[f'Close_Lag_{long_term_lag}'] = data_copy[close_column].shift(long_term_lag)
        data_copy['MA_5'] = data_copy[close_column].rolling(window=5).mean()
        expected_columns = [
            f'Close_Lag_{short_term_lag}',
            f'Close_Lag_{long_term_lag}',
            'MA_5',
            'Month',
            'Day_of_Week',
            'Quarter',
            'Sin_Month',
            'Cos_Month',
            'Random_Component',
            'OU_Simulated',
            'Seasonal_Adjusted_Close'
        ]
        available_columns = [col for col in expected_columns if col in data_copy.columns]
        print_debug_data("Available columns for X", available_columns)
        if not available_columns:
            return pd.DataFrame(), pd.Series()
        data_copy.dropna(subset=available_columns, inplace=True)
        X = data_copy[available_columns].copy()
        y = data_copy[close_column].copy()
        X.ffill(inplace=True)
        y.ffill(inplace=True)
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        print_debug_data("Final X shape in create_features_and_target", X)
        print_debug_data("Final y shape in create_features_and_target", y)
        return X, y