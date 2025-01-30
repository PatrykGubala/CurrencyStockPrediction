import os
import shutil
import numpy as np
import pandas as pd
from itertools import product
import logging
import json
import uuid
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression, RFE

from tensorflow.keras.regularizers import L1L2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense, Dropout
from tensorflow.keras.callbacks import Callback

from myapp.services.stocks_data_service import StocksDataService
from myapp.repositories.stocks_data_repository import StocksDataRepository
from myapp.repositories.stocks_trained_models_repository import StocksTrainedModelsRepository
from myapp.utils.plotting_utils import (plot_training_loss_by_rnn_type, plot_validation_loss_by_rnn_type, plot_residuals_over_time,
                                        plot_scatter_actual_vs_predicted, plot_results,plot_heatmap,plot_line_graph,decompose_time_series)


class PrintMetricsCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        print(
            f"loss={logs.get('loss')}, mae={logs.get('mae')}, val_loss={logs.get('val_loss')}, val_mae={logs.get('val_mae')}"
        )

class ModelCounter:
    def __init__(self, total):
        self.count = 0
        self.total = total

    def increment(self):
        self.count += 1
        return self.count



def print_debug_data(title, data):
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

def create_rnn_model(
    rnn_type='LSTM', number_of_layers=1, units=50, activation='tanh',
    optimizer='adam', input_shape=None, dropout_rate=0.2, horizon=1,
    recurrent_dropout=0.1, l1_reg=0.01, l2_reg=0.01
):
    if input_shape is None:
        raise ValueError("input_shape must be specified")
    regularizer = None
    if l1_reg > 0 or l2_reg > 0:
        regularizer = L1L2(l1=l1_reg, l2=l2_reg)
    model = Sequential()
    for layer_index in range(number_of_layers):
        return_sequences = layer_index < number_of_layers - 1
        if rnn_type == 'LSTM':
            model.add(LSTM(
                units=units, activation=activation,
                input_shape=input_shape, kernel_regularizer=regularizer,
                dropout=dropout_rate, recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
        elif rnn_type == 'GRU':
            model.add(GRU(
                units=units, activation=activation,
                input_shape=input_shape, kernel_regularizer=regularizer,
                dropout=dropout_rate, recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
        else:
            model.add(SimpleRNN(
                units=units, activation=activation,
                input_shape=input_shape, kernel_regularizer=regularizer,
                dropout=dropout_rate, recurrent_dropout=recurrent_dropout,
                return_sequences=return_sequences
            ))
    model.add(Dense(horizon))
    model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mae'])
    return model

def create_lstm_sequences(X, y, sequence_length=30):
    X_seq = []
    y_seq = []
    for i in range(len(X) - sequence_length):
        X_seq.append(X.iloc[i:i + sequence_length].values)
        y_seq.append(y.iloc[i + sequence_length])
    return np.array(X_seq), np.array(y_seq)

def make_predictions(best_model, X_test_seq, y_test_seq, scaler_y):
    predictions_scaled = best_model.predict(X_test_seq)
    predictions = scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1)).flatten()
    y_test_plot = scaler_y.inverse_transform(y_test_seq.reshape(-1, 1)).flatten()
    return predictions, y_test_plot


def add_stochastic_features(dataframe, stock_symbol):
    close_column = f'Close_{stock_symbol}'
    if not np.issubdtype(dataframe[close_column].dtype, np.floating):
        dataframe[close_column] = dataframe[close_column].astype(float)
    dataframe['Random_Component'] = np.random.normal(0, dataframe[close_column].std(), len(dataframe))

    def ornstein_uhlenbeck_process(mu, sigma, theta, T, N):
        dt = T / N
        process = np.zeros(N)
        process[0] = mu
        for t in range(1, N):
            process[t] = (process[t - 1] + theta *
                          (mu - process[t - 1]) * dt + sigma * np.sqrt(dt) *
                          np.random.normal(0, 1))
        return process

    dataframe['OU_Simulated'] = ornstein_uhlenbeck_process(
        mu=float(dataframe[close_column].mean()),
        sigma=float(dataframe[close_column].std()),
        theta=0.1,
        T=1,
        N=len(dataframe)
    )
    return dataframe

def add_trend_feature(dataframe, stock_symbol, window=30):
    close_column = f'Close_{stock_symbol}'
    dataframe[f'Trend_{stock_symbol}'] = dataframe[close_column].rolling(window=window).apply(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else np.nan
    )
    return dataframe

def add_seasonal_trend_features(dataframe, decomposition_result, stock_symbol):
    close_column = f'Close_{stock_symbol}'
    dataframe[f'Seasonal_Component_{stock_symbol}'] = decomposition_result.seasonal
    dataframe[f'Trend_Component_{stock_symbol}'] = decomposition_result.trend
    dataframe[f'Deseasonalized_Close_{stock_symbol}'] = dataframe[close_column] - decomposition_result.seasonal
    return dataframe

def create_seasonal_features(dataframe, stock_symbol):
    dataframe['Month'] = dataframe.index.month
    dataframe['Day_of_Week'] = dataframe.index.dayofweek
    dataframe['Quarter'] = dataframe.index.quarter
    dataframe['Sin_Month'] = np.sin(dataframe['Month'] * (2 * np.pi / 12))
    dataframe['Cos_Month'] = np.cos(dataframe['Month'] * (2 * np.pi / 12))
    return dataframe

def apply_seasonal_adjustment(dataframe, decomposition_result, stock_symbol):
    close_column = f'Close_{stock_symbol}'
    adjusted_dataframe = dataframe.copy()
    adjusted_dataframe['Seasonal_Adjusted_Close'] = dataframe[close_column] / decomposition_result.seasonal
    return adjusted_dataframe

def prepare_seasonal_data(dataframe, stock_symbol, output_directory):
    for column in dataframe.columns:
        if dataframe[column].dtype.name == 'object':
            try:
                dataframe[column] = dataframe[column].astype(float)
            except (ValueError, TypeError):
                continue
    decomposition = decompose_time_series(dataframe, stock_symbol, output_directory)
    dataframe = create_seasonal_features(dataframe, stock_symbol)
    dataframe = add_stochastic_features(dataframe, stock_symbol)
    dataframe = add_seasonal_trend_features(dataframe, decomposition, stock_symbol)
    dataframe = add_trend_feature(dataframe, stock_symbol, window=30)
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

def make_future_predictions(best_model, last_seq_full, scaler_y, sequence_length):
    future_preds = []
    current_sequence = last_seq_full.values.reshape(1, sequence_length, -1)
    for _ in range(30):
        pred_scaled = best_model.predict(current_sequence, verbose=0)
        pred_inverted = scaler_y.inverse_transform(pred_scaled)
        next_pred = pred_inverted.flatten()[0]
        future_preds.append(next_pred)

        pred_scaled_reshaped = scaler_y.transform(pred_inverted.reshape(-1, 1))
        current_sequence = np.roll(current_sequence, -1, axis=1)
        current_sequence[0, -1] = pred_scaled_reshaped
    return future_preds

def train_rnn_models(
    X_train_seq, y_train_seq, X_val_seq, y_val_seq, sequence_length, param_grid,
    model_counter, total_models, horizon, scaler_y, output_directory, stock_symbol
):
    results = []
    histories = []
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    param_combinations = list(product(*values))
    best_val_mse = float('inf')
    best_val_r2 = float('inf')

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
        val_preds_inverted = scaler_y.inverse_transform(val_preds)
        y_val_inverted = scaler_y.inverse_transform(y_val_seq.reshape(-1, 1)).flatten()
        val_mse = mean_squared_error(y_val_inverted, val_preds_inverted.flatten())
        val_r2 = r2_score(y_val_inverted, val_preds_inverted.flatten())
        results.append({
            'params': param_dict,
            'val_mse': val_mse,
            'val_r2': val_r2,
            'history': history
        })
        histories.append(history)
        if val_mse < best_val_mse:
            best_val_mse = val_mse
            best_val_r2 = val_r2
            best_model = model
            best_params = param_dict
            best_model_path = os.path.join(output_directory, f'best_model_{stock_symbol}.h5')
            best_model.save(best_model_path, save_format='h5')
            print(f"Nowy najlepszy model zapisany z parametrami: {best_params} o val_mse: {val_mse}, R²: {best_val_r2}")
    return results, histories, param_combinations, best_model, best_params

def visualize_data(data, stock_symbol, output_directory):
    close_column = f'Close_{stock_symbol}'
    plot_path = os.path.join(output_directory, f'{stock_symbol}_closing_prices.png')
    plot_line_graph(
        x_data_list=[data.index], y_data_list=[data[close_column]],
        labels=[close_column], title=f'{stock_symbol} Closing Prices',
        x_label='Date', y_label='Price', legend_labels=[close_column],
        output_path=plot_path, figure_size=(14, 7)
    )
    numeric_data = data.select_dtypes(include=[np.number])
    correlation = numeric_data.corr()
    heatmap_path = os.path.join(output_directory, f'{stock_symbol}_correlation_heatmap.png')
    plot_heatmap(
        data=correlation.values,
        title=f'{stock_symbol} Correlation Heatmap',
        x_tick_labels=correlation.columns,
        y_tick_labels=correlation.index,
        output_path=heatmap_path,
        figure_size=(30, 30),
        annotate=True
    )

def load_data_from_db(stock_symbol):
    repository = StocksDataRepository()
    stock = repository.get_stock_by_symbol(stock_symbol)
    if not stock:
        return pd.DataFrame()

    service = StocksDataService()
    stock_data = service.get_stock_data(stock_symbol, frequency="daily", range_param="all_data")
    if not stock_data:
        return pd.DataFrame()

    latest_record = repository.get_latest_record(stock)
    if latest_record:
        latest_data = {
            'timestamp': latest_record.timestamp.isoformat(),
            'close_price': str(latest_record.close_price),
            'open_price': str(latest_record.open_price),
            'high_price': str(latest_record.high_price),
            'low_price': str(latest_record.low_price),
            'volume': str(latest_record.volume)
        }
        latest_date = latest_record.timestamp.date()
        existing_dates = [pd.to_datetime(d['timestamp']).date() for d in stock_data]
        if latest_date not in existing_dates:
            stock_data.append(latest_data)

    df = pd.DataFrame(stock_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)

    numeric_columns = ['close_price', 'open_price', 'high_price', 'low_price', 'volume']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(float)
        else:
            logging.warning(f"Expected column '{col}' not found in data for stock {stock_symbol}.")

    rename_map = {
        'close_price': f'Close_{stock_symbol}',
        'open_price': f'Open_{stock_symbol}',
        'high_price': f'High_{stock_symbol}',
        'low_price': f'Low_{stock_symbol}',
        'volume': f'Volume_{stock_symbol}'
    }
    df.rename(columns=rename_map, inplace=True)

    return df

class StocksTrainedModelsService:
    def __init__(self):
        self.repository = StocksTrainedModelsRepository()

    def train_and_forecast(
        self, stock_symbol, param_grid, sequence_length, dataset_time, prediction_steps,
        short_term_lag, long_term_lag, scaling_method, output_directory
    ):
        print_debug_data("train_and_forecast START for stock", stock_symbol)
        stock_instance = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock_instance:
            return {"status": "error", "message": "Stock not found"}
        horizon = 1
        self.repository.mark_all_as_not_latest(stock_instance)
        self.repository.clear_old_predictions(stock_instance)
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        os.makedirs(output_directory)
        data = load_data_from_db(stock_symbol)
        print_debug_data("Data loaded from DB", data)
        if data.empty:
            return {"status": "error", "message": f"No data available in DB for {stock_symbol}"}
        data = data.resample('D').last().ffill()
        data = data.dropna()
        data = data[data.index.notnull()]
        print_debug_data("Data after asfreq/ffill/dropna", data)
        data = prepare_seasonal_data(data, stock_symbol, output_directory)
        print_debug_data("Data after prepare_seasonal_data", data)
        filtered_data = filter_last_n_years(data, number_of_years=dataset_time)
        print_debug_data("Filtered data (last n years)", filtered_data)
        if filtered_data.empty:
            return {"status": "error", "message": f"Filtered data for {stock_symbol} is empty"}

        scaler_map = {
            'standard': StandardScaler(),
            'normalize': MinMaxScaler(),
            'robust': RobustScaler()
        }
        scaler_X = scaler_map.get(scaling_method, StandardScaler())
        scaler_y = StandardScaler()
        X, y = self.create_features_and_target(filtered_data, stock_symbol, short_term_lag, long_term_lag)
        print_debug_data("Features X", X)
        print_debug_data("Target y", y)

        if X.empty or y.empty:
            return {"status": "error", "message": f"No features/target available for {stock_symbol}"}
        string_columns = X.select_dtypes(include=['object', 'string']).columns
        if len(string_columns) > 0:
            X.drop(columns=string_columns, errors='ignore', inplace=True)

        X_fs, selected_features = feature_selection_rfe(X, y, k_best_features=5)
        print_debug_data("Selected features (X_fs)", X_fs)
        corr_matrix_after = X_fs.corr()
        heatmap_path_after = os.path.join(output_directory, f'{stock_symbol}_correlation_heatmap_after.png')
        plot_heatmap(
            data=corr_matrix_after.values,
            title=f'{stock_symbol} Correlation After Feature Selection',
            x_tick_labels=corr_matrix_after.columns,
            y_tick_labels=corr_matrix_after.index,
            output_path=heatmap_path_after,
            annotate=True
        )
        y = y.loc[X_fs.index]
        visualize_df = pd.concat([X_fs, y.rename('Close_' + stock_symbol)], axis=1)
        visualize_data(visualize_df, stock_symbol, output_directory)

        scaler_X.fit(X_fs)
        X_scaled = scaler_X.transform(X_fs)
        scaler_y.fit(y.values.reshape(-1, 1))
        y_scaled = scaler_y.transform(y.values.reshape(-1, 1)).flatten()

        X_seq, y_seq = create_lstm_sequences(
            pd.DataFrame(X_scaled, columns=selected_features, index=X_fs.index),
            pd.Series(y_scaled, index=X_fs.index),
            sequence_length
        )
        print_debug_data("X_seq", X_seq)
        print_debug_data("y_seq", y_seq)

        y_dates = y.index[sequence_length:]
        test_period_steps = prediction_steps
        train_size = len(X_seq) - test_period_steps
        if train_size <= 0:
            return {"status": "error", "message": f"Not enough data to train for {stock_symbol}"}
        X_train_seq = X_seq[:train_size]
        y_train_seq = y_seq[:train_size]
        X_val_seq = X_seq[train_size:]
        y_val_seq = y_seq[train_size:]
        y_train_dates = y_dates[:train_size]
        y_val_dates = y_dates[train_size:]
        print_debug_data("X_train_seq", X_train_seq)
        print_debug_data("y_train_seq", y_train_seq)
        print_debug_data("X_val_seq", X_val_seq)
        print_debug_data("y_val_seq", y_val_seq)
        if len(X_val_seq) == 0:
            return {"status": "error",
                    "message": f"Not enough validation sequences after adjustment for {stock_symbol}"}

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
            scaler_y=scaler_y,
            output_directory=output_directory,
            stock_symbol=stock_symbol
        )

        plot_training_loss_by_rnn_type(results, stock_symbol, output_directory)
        plot_validation_loss_by_rnn_type(results, stock_symbol, output_directory)

        predictions, y_val_plot = make_predictions(best_model, X_val_seq, y_val_seq, scaler_y)
        y_test_dates = y_dates[train_size:]
        if len(predictions) == len(y_test_dates):
            residuals = y_val_plot - predictions
            hist_path = os.path.join(output_directory, f'{stock_symbol}_residuals_hist.png')
            time_path = os.path.join(output_directory, f'{stock_symbol}_residuals_over_time.png')
            scatter_path = os.path.join(output_directory, f'{stock_symbol}_actual_vs_predicted_scatter.png')
            y_train_plot = scaler_y.inverse_transform(y_train_seq.reshape(-1, 1)).flatten()
            plot_residuals_over_time(y_test_dates, residuals, time_path)
            plot_scatter_actual_vs_predicted(y_val_plot, predictions, scatter_path)
            plot_results(
                stock_symbol, y_train_plot, y_val_plot, predictions,
                y_train_dates, y_test_dates, output_directory, dataset_time
            )

            comparison_df = pd.DataFrame({
                'Date': y_test_dates,
                'Actual': y_val_plot,
                'Predicted': predictions
            })
            comparison_df.set_index('Date', inplace=True)

            print("\n===== Rzeczywiste vs Przewidywane (10) =====")
            print(comparison_df.head(10))

            comparison_csv = os.path.join(output_directory, f'{stock_symbol}_predictions_comparison.csv')
            comparison_df.to_csv(comparison_csv)

            print("\n===== Podusmowanie =====")
            print(comparison_df.describe())

            mse = mean_squared_error(y_val_plot, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_val_plot, predictions)
            print(f'Mean Squared Error dla {stock_symbol}: {mse}')
            print(f'Root Mean Squared Error dla {stock_symbol}: {rmse}')
            print(f'R2 Score dla {stock_symbol}: {r2}')

            results_csv = os.path.join(output_directory, f'{stock_symbol}_mse_results.csv')
            sorted_results = sorted(results, key=lambda x: x['val_mse'])
            rows = []
            rank_number = 1
            for res in sorted_results:
                params_str = '; '.join([f"{k}: {v}" for k, v in res['params'].items()])
                r2_val = res.get('val_r2', None)
                mean_mse_val = res['val_mse']
                rmse_val = np.sqrt(mean_mse_val)
                rows.append([rank_number, params_str, mean_mse_val, rmse_val, r2_val ])
                rank_number += 1
            df_results = pd.DataFrame(rows, columns=["Rank", "Parameters", "Mean MSE", "RMSE", "R2SCORE"])
            df_results.to_csv(results_csv, index=False)

            model_filename = f"{stock_symbol}_{str(uuid.uuid4())}.h5"
            model_file_path = os.path.join(output_directory, model_filename)
            best_model.save(model_file_path, save_format='keras')

            metrics_dict = {
                "mse": float(mse) if np.isfinite(mse) else None,
                "rmse": float(rmse) if np.isfinite(rmse) else None,
                "r2": float(r2) if np.isfinite(r2) else None,
            }
            param_grid_json = json.dumps(best_params)
            self.repository.create_trained_model(
                stock=stock_instance,
                model_name="AdvancedRNN",
                model_file_path=model_file_path,
                metrics=metrics_dict,
                param_grid=param_grid_json,
                is_latest=True
            )

            full_scaled_df = pd.DataFrame(
                scaler_X.transform(X_fs),
                columns=selected_features,
                index=X_fs.index
            )
            last_seq_full = full_scaled_df.iloc[-sequence_length:]
            future_preds_inverted = make_future_predictions(
                best_model=best_model,
                last_seq_full=last_seq_full,
                scaler_y=scaler_y,
                sequence_length=sequence_length,
            )
            last_date = filtered_data.index.max()
            future_dates = pd.date_range(
                start=last_date + pd.Timedelta(days=1),
                periods=prediction_steps,
                freq='D'
            )
            predictions_map_future = list(zip(future_dates, future_preds_inverted))
            future_predictions_serializable = [
                (date.isoformat(), float(value))
                for date, value in predictions_map_future
            ]
            self.repository.store_predictions(stock_instance, predictions_map_future)
            return {
                "status": "success",
                "message": "Model trained and predictions saved",
                "metrics": metrics_dict,
                "future_predictions": future_predictions_serializable
            }
        return {"status": "error", "message": "Lengths do not match in final predictions"}

    def create_features_and_target(self, dataframe, stock_symbol, short_term_lag, long_term_lag):
        print_debug_data("create_features_and_target dataframe", dataframe)
        if dataframe is None or dataframe.empty:
            return pd.DataFrame(), pd.Series()
        data_copy = dataframe.copy()
        close_column = f'Close_{stock_symbol}'
        if close_column not in data_copy.columns:
            return pd.DataFrame(), pd.Series()
        data_copy[f'Close_Lag_{short_term_lag}'] = data_copy[close_column].shift(short_term_lag)
        data_copy[f'Close_Lag_{long_term_lag}'] = data_copy[close_column].shift(long_term_lag)
        expected_columns = [
            f'Close_Lag_{short_term_lag}',
            f'Close_Lag_{long_term_lag}',
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
        print_debug_data("Available columns dla X", available_columns)
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
        print_debug_data("Final X w create_features_and_target", X)
        print_debug_data("Final y w create_features_and_target", y)
        return X, y
