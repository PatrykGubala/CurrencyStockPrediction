# myapp/utils/plotting_utils.py
from datetime import timedelta

import matplotlib.pyplot as plt
import os
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose

def plot_line_graph(x_data_list, y_data_list, labels, title, x_label, y_label, legend_labels, output_path,
                   figure_size=(14, 7)):
    plt.figure(figsize=figure_size)
    for x_data, y_data, label in zip(x_data_list, y_data_list, legend_labels):
        plt.plot(x_data, y_data, label=label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

def plot_heatmap(data, title, x_tick_labels, y_tick_labels, output_path, figure_size=(12, 10)):
    if data.shape[0] < 2 or data.shape[1] < 2:
        print("Insufficient data for heatmap.")
        return
    plt.figure(figsize=figure_size)
    plt.matshow(data, cmap='coolwarm')
    plt.xticks(range(len(x_tick_labels)), x_tick_labels, rotation=90)
    plt.yticks(range(len(y_tick_labels)), y_tick_labels)
    plt.colorbar(label='MSE Test')
    plt.title(title, pad=20)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"Heatmap saved to {output_path}")

def visualize_data(data, currency, output_dir):
    close_col = f'Close_{currency}'
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
    plot_heatmap(
        data=correlation,
        title='Correlation Heatmap',
        x_tick_labels=correlation.columns,
        y_tick_labels=correlation.columns,
        output_path=heatmap_path,
        figure_size=(12, 10),
        annotate=True

    )
def decompose_time_series(data, currency, output_dir):
    close_col = 'close'
    if close_col not in data.columns:
        raise ValueError(f"Column {close_col} not found in data for decomposition.")

    if len(data) < 504:
        raise ValueError(f"Not enough observations for seasonal decomposition. Required: 504, Provided: {len(data)}")

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
    forecast_plot_path = os.path.join(currency_output_dir, f'{currency}_forecast.png')
    plot_line_graph(
        x_data_list=[y_train_dates, y_test_dates, y_test_dates],
        y_data_list=[y_train_plot, y_test_plot, predictions],
        labels=['Training Data', 'Actual Prices', 'Predicted Prices'],
        title=f'{currency} Closing Price Prediction (Last {dataset_time} Years)',
        x_label='Date',
        y_label='Price',
        legend_labels=['Training Data', 'Actual Prices', 'Predicted Prices'],
        output_path=forecast_plot_path,
        figure_size=(20, 10)
    )
    comparison_plot_path = os.path.join(currency_output_dir, f'{currency}_actual_vs_predicted.png')
    plot_line_graph(
        x_data_list=[y_test_dates, y_test_dates],
        y_data_list=[y_test_plot, predictions],
        labels=['Actual Prices', 'Predicted Prices'],
        title=f'{currency} Actual vs Predicted Prices (Test Set)',
        x_label='Date',
        y_label='Price',
        legend_labels=['Actual Prices', 'Predicted Prices'],
        output_path=comparison_plot_path,
        figure_size=(20, 10)
    )


def plot_training_history(history, output_dir, currency):
    loss = history.history.get('loss', [])
    val_loss = history.history.get('val_loss', [])
    if not loss:
        return
    plt.figure(figsize=(14, 7))
    plt.plot(loss, label='Training Loss')
    if val_loss:
        plt.plot(val_loss, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(f'{currency} Training History')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f'{currency}_training_history.png')
    plt.savefig(plot_path)
    plt.close()

def plot_validation_losses(histories, param_combinations, currency, output_dir):
    plt.figure(figsize=(20, 10))
    for history, params in zip(histories, param_combinations):
        epochs = range(1, len(history.history['val_loss']) + 1)
        plt.plot(epochs, history.history['val_loss'], label=str(params))
    plt.title(f'Validation Loss per Epoch for Different Model Configurations - {currency}')
    plt.xlabel('Epoch')
    plt.ylabel('Validation Loss')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f'{currency}_validation_losses_per_epoch.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"Validation losses per epoch plot saved to {plot_path}")
