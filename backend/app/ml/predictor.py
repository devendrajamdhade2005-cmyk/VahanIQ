"""
ML Prediction Service - Load model and make predictions
"""

try:
    import joblib
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not available. Using mock predictor.")

from pathlib import Path
from typing import Dict, List, Optional
import json
import random

class FailurePredictor:
    """
    Wrapper for trained XGBoost model
    Singleton pattern to load model once
    """
    
    _instance = None
    _model = None
    _scaler = None
    _explainer = None
    _feature_names = None
    _metadata = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize predictor (loads model on first call)"""
        if self._model is None:
            self.load_model()
    
    def load_model(self, model_dir: str = "ml/models"):
        """Load trained model and related artifacts"""
        if not ML_AVAILABLE:
            print("⚠️  Using mock ML predictor (ML libraries not installed)")
            self._model = "mock"
            self._scaler = "mock"
            self._explainer = "mock"
            self._feature_names = [
                "rpm", "speed", "engine_load", "coolant_temp", "intake_temp",
                "throttle_position", "maf", "fuel_pressure", "fuel_level",
                "fuel_trim_short", "fuel_trim_long", "o2_voltage",
                "brake_pad_thickness_fl", "brake_pad_thickness_fr",
                "brake_pad_thickness_rl", "brake_pad_thickness_rr",
                "brake_fluid_pressure", "battery_voltage", "transmission_temp", "mileage"
            ]
            self._metadata = {
                "failure_types": {
                    "0": "normal",
                    "1": "brake",
                    "2": "engine",
                    "3": "fuel",
                    "4": "electrical"
                },
                "trained_at": "mock_model"
            }
            return
            
        model_path = Path(model_dir)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model directory not found: {model_dir}. "
                f"Train model first with: python ml/scripts/train_prediction_model.py"
            )
        
        try:
            self._model = joblib.load(model_path / "failure_prediction_model.pkl")
            self._scaler = joblib.load(model_path / "scaler.pkl")
            self._explainer = joblib.load(model_path / "shap_explainer.pkl")
            self._feature_names = joblib.load(model_path / "feature_names.pkl")
            self._metadata = joblib.load(model_path / "model_metadata.pkl")
            print("✅ ML model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def predict_failure(self, sensor_data: Dict) -> Dict:
        """
        Predict failure type from sensor data
        
        Args:
            sensor_data: Dictionary with sensor readings
        
        Returns:
            Dictionary with prediction, probability, and explanation
        """
        # Mock prediction if ML not available
        if not ML_AVAILABLE or self._model == "mock":
            return self._mock_predict(sensor_data)
        
        # Prepare features (in correct order)
        features = np.array([[
            sensor_data.get(feature, 0) for feature in self._feature_names
        ]])
        
        # Scale features
        features_scaled = self._scaler.transform(features)
        
        # Get prediction
        prediction_id = self._model.predict(features_scaled)[0]
        probabilities = self._model.predict_proba(features_scaled)[0]
        
        # Get SHAP values for explainability
        shap_values = self._explainer.shap_values(features_scaled)
        
        # Get failure type mapping
        failure_types = self._metadata['failure_types']
        failure_type = failure_types[str(prediction_id)]
        
        # Get top contributing features
        top_features = self._get_top_features(shap_values, prediction_id)
        
        # Generate plain-language explanation
        explanation = self._generate_explanation(
            failure_type, 
            probabilities[prediction_id],
            top_features,
            sensor_data
        )
        
        return {
            'failure_type': failure_type,
            'failure_type_id': int(prediction_id),
            'probability': float(probabilities[prediction_id]),
            'all_probabilities': {
                failure_types[str(i)]: float(prob) 
                for i, prob in enumerate(probabilities)
            },
            'explanation': explanation,
            'top_features': top_features,
            'severity': self._calculate_severity(probabilities[prediction_id]),
            'model_version': self._metadata.get('trained_at', 'unknown')
        }
    
    def _mock_predict(self, sensor_data: Dict) -> Dict:
        """Mock prediction when ML libraries not available"""
        # Simple rule-based logic
        failure_types = self._metadata['failure_types']
        
        # Check brake pads
        brake_fl = sensor_data.get('brake_pad_thickness_fl', 5.0)
        brake_fr = sensor_data.get('brake_pad_thickness_fr', 5.0)
        if brake_fl < 2.5 or brake_fr < 2.5:
            failure_type = "brake"
            probability = 0.85
        # Check coolant temp
        elif sensor_data.get('coolant_temp', 90) > 105:
            failure_type = "engine"
            probability = 0.75
        # Check battery voltage
        elif sensor_data.get('battery_voltage', 14) < 12.0:
            failure_type = "electrical"
            probability = 0.70
        # Check fuel trim
        elif abs(sensor_data.get('fuel_trim_short', 0)) > 15:
            failure_type = "fuel"
            probability = 0.65
        else:
            failure_type = "normal"
            probability = 0.90
        
        # Generate mock top features
        top_features = []
        if failure_type == "brake":
            top_features = [
                {"feature": "brake_pad_thickness_fl", "contribution": -0.4, "impact": "negative"},
                {"feature": "brake_pad_thickness_fr", "contribution": -0.3, "impact": "negative"},
                {"feature": "mileage", "contribution": 0.2, "impact": "positive"}
            ]
        elif failure_type == "engine":
            top_features = [
                {"feature": "coolant_temp", "contribution": 0.5, "impact": "positive"},
                {"feature": "engine_load", "contribution": 0.3, "impact": "positive"}
            ]
        elif failure_type == "electrical":
            top_features = [
                {"feature": "battery_voltage", "contribution": -0.6, "impact": "negative"}
            ]
        elif failure_type == "fuel":
            top_features = [
                {"feature": "fuel_trim_short", "contribution": 0.4, "impact": "positive"},
                {"feature": "o2_voltage", "contribution": 0.3, "impact": "positive"}
            ]
        
        explanation = self._generate_explanation(
            failure_type,
            probability,
            top_features,
            sensor_data
        )
        
        # Generate all probabilities
        all_probabilities = {ft: 0.05 for ft in failure_types.values()}
        all_probabilities[failure_type] = probability
        
        # Normalize to sum to 1.0
        total = sum(all_probabilities.values())
        all_probabilities = {k: v/total for k, v in all_probabilities.items()}
        
        return {
            'failure_type': failure_type,
            'failure_type_id': list(failure_types.values()).index(failure_type),
            'probability': probability,
            'all_probabilities': all_probabilities,
            'explanation': explanation,
            'top_features': top_features,
            'severity': self._calculate_severity(probability),
            'model_version': 'mock_v1.0'
        }
    
    def _get_top_features(self, shap_values, prediction_id, top_n=5):
        """Get top contributing features from SHAP values"""
        # Get SHAP values for the predicted class
        if isinstance(shap_values, list):
            class_shap_values = shap_values[prediction_id][0]
        else:
            class_shap_values = shap_values[0]
        
        # Get absolute values and sort
        abs_shap = np.abs(class_shap_values)
        top_indices = np.argsort(abs_shap)[-top_n:][::-1]
        
        top_features = []
        for idx in top_indices:
            feature_name = self._feature_names[idx]
            contribution = float(class_shap_values[idx])
            top_features.append({
                'feature': feature_name,
                'contribution': contribution,
                'impact': 'positive' if contribution > 0 else 'negative'
            })
        
        return top_features
    
    def _generate_explanation(
        self, 
        failure_type: str, 
        probability: float,
        top_features: List[Dict],
        sensor_data: Dict
    ) -> str:
        """Generate human-readable explanation"""
        
        if failure_type == 'normal':
            return "All systems operating normally. No issues detected."
        
        # Base explanation
        risk_level = "high" if probability > 0.7 else "moderate"
        explanation = f"{failure_type.capitalize()} failure risk is {risk_level} ({probability:.0%} probability). "
        
        # Add contributing factors
        if failure_type == 'brake':
            fl = sensor_data.get('brake_pad_thickness_fl', 0)
            fr = sensor_data.get('brake_pad_thickness_fr', 0)
            if fl < 2.5 or fr < 2.5:
                explanation += f"Front brake pads are critically worn (FL: {fl:.1f}mm, FR: {fr:.1f}mm). "
                explanation += "Replace brake pads immediately. "
        
        elif failure_type == 'engine':
            temp = sensor_data.get('coolant_temp', 0)
            if temp > 100:
                explanation += f"Engine coolant temperature is high ({temp:.1f}°C). "
                explanation += "Check cooling system and coolant levels. "
        
        elif failure_type == 'fuel':
            fuel_trim = sensor_data.get('fuel_trim_short', 0)
            if abs(fuel_trim) > 10:
                explanation += f"Fuel trim is out of range ({fuel_trim:.1f}%). "
                explanation += "Check for fuel system leaks or injector issues. "
        
        elif failure_type == 'electrical':
            voltage = sensor_data.get('battery_voltage', 0)
            if voltage < 12.5:
                explanation += f"Battery voltage is low ({voltage:.1f}V). "
                explanation += "Test battery and charging system. "
        
        # Add key contributing sensors
        top_sensor = top_features[0]['feature'] if top_features else None
        if top_sensor:
            explanation += f"Key indicator: {top_sensor.replace('_', ' ')}."
        
        return explanation
    
    def _calculate_severity(self, probability: float) -> str:
        """Calculate severity level"""
        if probability >= 0.8:
            return "critical"
        elif probability >= 0.6:
            return "high"
        elif probability >= 0.4:
            return "medium"
        else:
            return "low"
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            'model_type': 'XGBoost',
            'trained_at': self._metadata.get('trained_at', 'unknown'),
            'features': self._feature_names,
            'failure_types': self._metadata['failure_types'],
            'version': '1.0.0'
        }


# Singleton instance
predictor = FailurePredictor()


def predict_failure(sensor_data: Dict) -> Dict:
    """
    Convenience function for predictions
    
    Usage:
        from app.ml.predictor import predict_failure
        result = predict_failure(sensor_data)
    """
    return predictor.predict_failure(sensor_data)
