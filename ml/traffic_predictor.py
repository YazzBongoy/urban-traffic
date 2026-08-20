#!/usr/bin/env python3
"""
Traffic Prediction Model using LSTM
Predicts traffic congestion levels based on historical data.
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrafficPredictor:
    def __init__(self, sequence_length: int = 24):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
    
    def build_model(self, input_shape: Tuple[int, int]):
        """Build LSTM model for traffic prediction."""
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Predict congestion level
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Model built successfully")
        return self.model
    
    def prepare_data(
        self,
        data: pd.DataFrame,
        target_col: str = 'congestion_level'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM training."""
        # Scale features
        scaled_data = self.scaler.fit_transform(data.values)
        
        X, y = [], []
        
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:i + self.sequence_length])
            y.append(scaled_data[i + self.sequence_length, 0])  # Target column
        
        return np.array(X), np.array(y)
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32
    ):
        """Train the model."""
        if self.model is None:
            self.build_model((X_train.shape[1], X_train.shape[2]))
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        logger.info(f"Training completed. Final loss: {history.history['loss'][-1]:.4f}")
        return history
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        predictions = self.model.predict(data)
        return predictions
    
    def save_model(self, path: str):
        """Save model to disk."""
        if self.model:
            self.model.save(path)
            logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from disk."""
        from tensorflow.keras.models import load_model
        self.model = load_model(path)
        logger.info(f"Model loaded from {path}")


def generate_sample_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate sample traffic data for testing."""
    np.random.seed(42)
    
    hours = np.arange(n_samples)
    
    # Simulate daily pattern
    base_congestion = 0.3 + 0.4 * np.sin(2 * np.pi * hours / 24 - np.pi / 2)
    
    # Add noise
    noise = np.random.normal(0, 0.1, n_samples)
    congestion = base_congestion + noise
    
    # Clip to [0, 1]
    congestion = np.clip(congestion, 0, 1)
    
    # Create DataFrame
    data = pd.DataFrame({
        'hour': hours % 24,
        'day_of_week': (hours // 24) % 7,
        'congestion_level': congestion,
        'vehicle_count': (congestion * 1000).astype(int),
        'average_speed': 60 - congestion * 40
    })
    
    return data


def main():
    # Generate sample data
    data = generate_sample_data(1000)
    
    # Initialize predictor
    predictor = TrafficPredictor(sequence_length=24)
    
    # Prepare data
    X, y = predictor.prepare_data(data)
    
    # Split data
    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    
    # Train model
    predictor.train(X_train, y_train, X_val, y_val, epochs=50)
    
    # Make predictions
    predictions = predictor.predict(X_val[:10])
    print(f"Sample predictions: {predictions.flatten()}")
    
    # Save model
    predictor.save_model("traffic_predictor.h5")


if __name__ == "__main__":
    main()
