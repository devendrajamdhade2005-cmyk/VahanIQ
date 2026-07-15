"""
Train XGBoost failure prediction model with SHAP explainability

Predicts vehicle failure types based on sensor data:
- Brake failures
- Engine failures
- Fuel system issues
- Electrical problems
"""

import asyncio
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
from pathlib import Path

# ML libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb
import shap

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.core.database import async_session_maker
from backend.app.models.sensor import SensorReading
from backend.app.models.vehicle import Vehicle
from sqlalchemy import select


class FailurePredictionModel:
    """
    XGBoost-based failure prediction model
    """
    
    # Sensor features to use for prediction
    SENSOR_FEATURES = [
        'rpm', 'speed', 'engine_load', 'coolant_temp', 'intake_temp',
        'throttle_position', 'maf', 'fuel_pressure', 'fuel_level',
        'fuel_trim_short', 'fuel_trim_long', 'o2_voltage',
        'brake_fluid_pressure', 'brake_pad_thickness_fl', 'brake_pad_thickness_fr',
        'brake_pad_thickness_rl', 'brake_pad_thickness_rr',
        'transmission_temp', 'battery_voltage', 'mileage'
    ]
    
    # Failure type labels
    FAILURE_TYPES = {
        0: 'normal',
        1: 'brake',
        2: 'engine',
        3: 'fuel',
        4: 'electrical'
    }
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.explainer = None
        self.feature_names = self.SENSOR_FEATURES
        
    async def load_data_from_db(self):
        """Load sensor data from database"""
        print("📊 Loading sensor data from database...")
        
        async with async_session_maker() as db:
            # Get all sensor readings
            result = await db.execute(
                select(SensorReading).order_by(SensorReading.timestamp.desc())
            )
            readings = result.scalars().all()
            
            if not readings:
                raise ValueError("No sensor data found. Run generate_synthetic_data.py first!")
            
            print(f"✅ Loaded {len(readings)} sensor readings")
            
            # Convert to DataFrame
            data = []
            for reading in readings:
                row = {feature: getattr(reading, feature, None) for feature in self.SENSOR_FEATURES}
                row['vehicle_id'] = reading.vehicle_id
                row['timestamp'] = reading.timestamp
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Handle missing values
            df = df.fillna(df.mean())
            
            return df
    
    def label_failures(self, df):
        """
        Label sensor readings with failure types based on thresholds
        """
        print("🏷️  Labeling failures based on sensor thresholds...")
        
        labels = []
        
        for idx, row in df.iterrows():
            # Check for brake failures (critical brake pad thickness)
            if (row['brake_pad_thickness_fl'] < 2.5 or 
                row['brake_pad_thickness_fr'] < 2.5):
                labels.append(1)  # brake
            
            # Check for engine failures (overheating)
            elif row['coolant_temp'] > 100:
                labels.append(2)  # engine
            
            # Check for fuel system issues
            elif (abs(row['fuel_trim_short']) > 10 or 
                  abs(row['fuel_trim_long']) > 10):
                labels.append(3)  # fuel
            
            # Check for electrical issues
            elif row['battery_voltage'] < 12.5:
                labels.append(4)  # electrical
            
            # Normal operation
            else:
                labels.append(0)  # normal
        
        df['failure_type'] = labels
        
        # Print distribution
        print("\n📈 Failure distribution:")
        for failure_id, failure_name in self.FAILURE_TYPES.items():
            count = (df['failure_type'] == failure_id).sum()
            percentage = count / len(df) * 100
            print(f"   {failure_name:12s}: {count:5d} ({percentage:5.1f}%)")
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        print("\n🔧 Preparing features...")
        
        # Features
        X = df[self.SENSOR_FEATURES].values
        
        # Labels
        y = df['failure_type'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"✅ Feature matrix shape: {X_scaled.shape}")
        print(f"✅ Labels shape: {y.shape}")
        
        return X_scaled, y
    
    def train(self, X, y):
        """Train XGBoost model"""
        print("\n🤖 Training XGBoost model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # XGBoost parameters
        params = {
            'objective': 'multi:softprob',
            'num_class': len(self.FAILURE_TYPES),
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'mlogloss'
        }
        
        # Train model
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Model trained! Accuracy: {accuracy:.2%}")
        
        # Detailed metrics
        print("\n📊 Classification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=list(self.FAILURE_TYPES.values())
        ))
        
        return X_test, y_test
    
    def create_explainer(self, X_sample):
        """Create SHAP explainer"""
        print("\n🔍 Creating SHAP explainer...")
        
        # Use a sample for SHAP (it's computationally expensive)
        sample_size = min(100, len(X_sample))
        X_sample_small = X_sample[:sample_size]
        
        # Create TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)
        
        # Calculate SHAP values for sample
        shap_values = self.explainer.shap_values(X_sample_small)
        
        print("✅ SHAP explainer created")
        
        return shap_values
    
    def save_model(self, output_dir='ml/models'):
        """Save trained model and scaler"""
        print(f"\n💾 Saving model to {output_dir}/...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = f"{output_dir}/failure_prediction_model.pkl"
        joblib.dump(self.model, model_path)
        print(f"   ✅ Model saved: {model_path}")
        
        # Save scaler
        scaler_path = f"{output_dir}/scaler.pkl"
        joblib.dump(self.scaler, scaler_path)
        print(f"   ✅ Scaler saved: {scaler_path}")
        
        # Save explainer
        explainer_path = f"{output_dir}/shap_explainer.pkl"
        joblib.dump(self.explainer, explainer_path)
        print(f"   ✅ SHAP explainer saved: {explainer_path}")
        
        # Save feature names
        features_path = f"{output_dir}/feature_names.pkl"
        joblib.dump(self.feature_names, features_path)
        print(f"   ✅ Feature names saved: {features_path}")
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'features': self.feature_names,
            'failure_types': self.FAILURE_TYPES,
            'model_type': 'XGBoost',
            'accuracy': None  # Can be added after evaluation
        }
        metadata_path = f"{output_dir}/model_metadata.pkl"
        joblib.dump(metadata, metadata_path)
        print(f"   ✅ Metadata saved: {metadata_path}")
    
    def load_model(self, model_dir='ml/models'):
        """Load trained model"""
        print(f"📂 Loading model from {model_dir}/...")
        
        self.model = joblib.load(f"{model_dir}/failure_prediction_model.pkl")
        self.scaler = joblib.load(f"{model_dir}/scaler.pkl")
        self.explainer = joblib.load(f"{model_dir}/shap_explainer.pkl")
        self.feature_names = joblib.load(f"{model_dir}/feature_names.pkl")
        
        print("✅ Model loaded successfully")
    
    def predict(self, sensor_data):
        """
        Make prediction for new sensor data
        
        Args:
            sensor_data: dict with sensor readings
        
        Returns:
            prediction, probability, shap_values
        """
        # Prepare features
        features = np.array([[sensor_data.get(f, 0) for f in self.SENSOR_FEATURES]])
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(features_scaled)
        
        return {
            'failure_type': self.FAILURE_TYPES[prediction],
            'failure_type_id': int(prediction),
            'probability': float(probabilities[prediction]),
            'all_probabilities': {
                self.FAILURE_TYPES[i]: float(prob) 
                for i, prob in enumerate(probabilities)
            },
            'shap_values': shap_values
        }


async def main():
    """Main training pipeline"""
    print("=" * 60)
    print("🚀 AutoSense AI - Failure Prediction Model Training")
    print("=" * 60)
    
    # Initialize model
    model = FailurePredictionModel()
    
    # Load data
    df = await model.load_data_from_db()
    
    # Label failures
    df = model.label_failures(df)
    
    # Prepare features
    X, y = model.prepare_features(df)
    
    # Train model
    X_test, y_test = model.train(X, y)
    
    # Create explainer
    shap_values = model.create_explainer(X_test)
    
    # Save model
    model.save_model()
    
    print("\n" + "=" * 60)
    print("✨ Training complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Test predictions: python ml/scripts/test_predictions.py")
    print("   2. Integrate with backend: Implement diagnosis API")
    print("   3. Build frontend: Display predictions in dashboards")


if __name__ == "__main__":
    asyncio.run(main())
