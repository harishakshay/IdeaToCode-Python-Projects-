	import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def create_dataset(series, window_size):
    X, y = [], []
    for i in range(len(series) - window_size):
        X.append(series[i:i+window_size])
        y.append(series[i+window_size])
    return np.array(X), np.array(y)

def build_model(input_shape):
    model = Sequential([
        LSTM(50, activation='tanh', input_shape=input_shape),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    # generate synthetic stock price data (sine wave + noise)
    np.random.seed(42)
    timesteps = 200
    t = np.arange(timesteps)
    prices = np.sin(0.02 * t) + 0.5 * np.random.randn(timesteps)
    prices = prices.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    window_size = 20
    X, y = create_dataset(scaled_prices, window_size)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = build_model((window_size, 1))
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)

    # predict next price
    last_window = scaled_prices[-window_size:].reshape((1, window_size, 1))
    pred_scaled = model.predict(last_window, verbose=0)
    pred_price = scaler.inverse_transform(pred_scaled)
    print(f'Predicted next price: {pred_price[0][0]:.4f}')

if __name__ == "__main__":
    main()
