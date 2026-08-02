# Metrics for evaluating model performance
import numpy as np
from sklearn.metrics import mean_squared_error

def print_metrics(y_true, y_pred, label):
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    rmse = np.sqrt(mean_squared_error(y_true[mask], y_pred[mask]))
    print(f"{label} - MAPE: {mape:.2f}%, RMSE: {rmse:.2f} tonnes")