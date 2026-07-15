"""
Test ML predictions on sample sensor data
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.core.database import async_session_maker
from backend.app.models.sensor import SensorReading
from backend.app.models.vehicle import Vehicle
from backend.app.ml.predictor import predict_failure
from sqlalchemy import select
import random


async def test_predictions():
    """Test predictions on real sensor data"""
    print("=" * 60)
    print("🧪 Testing ML Predictions")
    print("=" * 60)
    
    async with async_session_maker() as db:
        # Get some sensor readings
        result = await db.execute(
            select(SensorReading, Vehicle)
            .join(Vehicle, SensorReading.vehicle_id == Vehicle.id)
            .limit(10)
        )
        readings = result.all()
        
        if not readings:
            print("❌ No sensor data found. Run generate_synthetic_data.py first!")
            return
        
        print(f"\n✅ Found {len(readings)} sensor readings to test")
        
        # Test predictions
        for reading, vehicle in readings:
            print("\n" + "-" * 60)
            print(f"🚗 Vehicle: {vehicle.registration_number} - {vehicle.make} {vehicle.model}")
            print(f"   Mileage: {vehicle.current_mileage:.0f} km")
            print(f"   Health: {vehicle.health_status.value}")
            
            # Prepare sensor data
            sensor_data = {
                'rpm': reading.rpm or 0,
                'speed': reading.speed or 0,
                'engine_load': reading.engine_load or 0,
                'coolant_temp': reading.coolant_temp or 0,
                'intake_temp': reading.intake_temp or 0,
                'throttle_position': reading.throttle_position or 0,
                'maf': reading.maf or 0,
                'fuel_pressure': reading.fuel_pressure or 0,
                'fuel_level': reading.fuel_level or 0,
                'fuel_trim_short': reading.fuel_trim_short or 0,
                'fuel_trim_long': reading.fuel_trim_long or 0,
                'o2_voltage': reading.o2_voltage or 0,
                'brake_fluid_pressure': reading.brake_fluid_pressure or 0,
                'brake_pad_thickness_fl': reading.brake_pad_thickness_fl or 0,
                'brake_pad_thickness_fr': reading.brake_pad_thickness_fr or 0,
                'brake_pad_thickness_rl': reading.brake_pad_thickness_rl or 0,
                'brake_pad_thickness_rr': reading.brake_pad_thickness_rr or 0,
                'transmission_temp': reading.transmission_temp or 0,
                'battery_voltage': reading.battery_voltage or 0,
                'mileage': reading.mileage or 0
            }
            
            # Make prediction
            try:
                prediction = predict_failure(sensor_data)
                
                print(f"\n📊 Prediction:")
                print(f"   Type: {prediction['failure_type'].upper()}")
                print(f"   Probability: {prediction['probability']:.1%}")
                print(f"   Severity: {prediction['severity']}")
                print(f"\n💡 Explanation:")
                print(f"   {prediction['explanation']}")
                
                # Show top features
                print(f"\n🔍 Key Indicators:")
                for feature in prediction['top_features'][:3]:
                    feature_name = feature['feature'].replace('_', ' ').title()
                    impact = "↑" if feature['impact'] == 'positive' else "↓"
                    print(f"   {impact} {feature_name}")
                
            except Exception as e:
                print(f"❌ Prediction failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Test complete!")
        print("=" * 60)


def test_edge_cases():
    """Test predictions on edge case scenarios"""
    print("\n" + "=" * 60)
    print("🧪 Testing Edge Cases")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Critical Brake Wear',
            'data': {
                'brake_pad_thickness_fl': 1.5,
                'brake_pad_thickness_fr': 1.8,
                'brake_pad_thickness_rl': 3.0,
                'brake_pad_thickness_rr': 3.2,
                'rpm': 1500,
                'speed': 60,
                'coolant_temp': 90,
                'battery_voltage': 14.0,
                'mileage': 85000
            }
        },
        {
            'name': 'Engine Overheating',
            'data': {
                'coolant_temp': 105,
                'engine_load': 85,
                'rpm': 3500,
                'speed': 80,
                'brake_pad_thickness_fl': 8.0,
                'brake_pad_thickness_fr': 8.0,
                'battery_voltage': 14.0,
                'mileage': 45000
            }
        },
        {
            'name': 'Low Battery',
            'data': {
                'battery_voltage': 11.8,
                'rpm': 800,
                'speed': 0,
                'coolant_temp': 88,
                'brake_pad_thickness_fl': 7.0,
                'brake_pad_thickness_fr': 7.0,
                'mileage': 95000
            }
        },
        {
            'name': 'Normal Operation',
            'data': {
                'rpm': 2000,
                'speed': 70,
                'coolant_temp': 92,
                'brake_pad_thickness_fl': 9.0,
                'brake_pad_thickness_fr': 9.0,
                'brake_pad_thickness_rl': 9.5,
                'brake_pad_thickness_rr': 9.5,
                'battery_voltage': 14.2,
                'fuel_level': 65,
                'mileage': 25000
            }
        }
    ]
    
    # Fill in missing features with defaults
    default_values = {
        'rpm': 0, 'speed': 0, 'engine_load': 0, 'coolant_temp': 90,
        'intake_temp': 30, 'throttle_position': 0, 'maf': 0,
        'fuel_pressure': 300, 'fuel_level': 50, 'fuel_trim_short': 0,
        'fuel_trim_long': 0, 'o2_voltage': 0.5, 'brake_fluid_pressure': 0,
        'brake_pad_thickness_fl': 10, 'brake_pad_thickness_fr': 10,
        'brake_pad_thickness_rl': 10, 'brake_pad_thickness_rr': 10,
        'transmission_temp': 80, 'battery_voltage': 14, 'mileage': 30000
    }
    
    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print("-" * 60)
        
        # Merge with defaults
        sensor_data = {**default_values, **test_case['data']}
        
        try:
            prediction = predict_failure(sensor_data)
            
            print(f"Prediction: {prediction['failure_type'].upper()}")
            print(f"Probability: {prediction['probability']:.1%}")
            print(f"Severity: {prediction['severity']}")
            print(f"Explanation: {prediction['explanation']}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Edge case testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Test on real data
    asyncio.run(test_predictions())
    
    # Test edge cases
    test_edge_cases()
