"""
Simple test runner for the elevator simulation system.
"""

import unittest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_basic_tests():
    """Run basic functionality tests."""
    print("Running Elevator Simulation Tests...")
    
    # Test 1: Configuration loading
    try:
        from config.building_config import BuildingConfig
        from config.simulation_config import SimulationConfig
        
        # Create sample config
        BuildingConfig.create_sample_config("test_building.csv")
        config = BuildingConfig("test_building.csv")
        
        errors = config.validate_configuration()
        if errors:
            print(f"❌ Configuration validation failed: {errors}")
        else:
            print("✅ Configuration loading and validation passed")
        
        # Cleanup
        os.remove("test_building.csv")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    # Test 2: Building creation
    try:
        from models.building import Building
        from models.elevator import Elevator, Direction
        
        elevators_config = [
            {'id': 'test_elevator', 'capacity': 8, 'speed': 2.0}
        ]
        
        building = Building("test_building", 5, elevators_config)
        
        if len(building.elevators) == 1:
            print("✅ Building creation passed")
        else:
            print("❌ Building creation failed")
            
        # Test elevator request
        success = building.request_elevator(3, Direction.UP)
        if success:
            print("✅ Elevator request handling passed")
        else:
            print("❌ Elevator request handling failed")
            
    except Exception as e:
        print(f"❌ Building test failed: {e}")
    
    # Test 3: Simulation components
    try:
        from simulation.simulator import ElevatorSimulator
        from simulation.logger import SimulationLogger
        
        # Create simulator
        simulator = ElevatorSimulator(building)
        
        # Test passenger addition
        passenger_id = simulator.add_manual_passenger(1, 4)
        if passenger_id:
            print("✅ Passenger management passed")
        else:
            print("❌ Passenger management failed")
            
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
    
    # Test 4: Logging system
    try:
        from simulation.logger import SimulationLogger
        import tempfile
        import shutil
        
        # Create temporary directory for test
        temp_dir = tempfile.mkdtemp()
        logger = SimulationLogger(temp_dir)
        
        logger.start_logging()
        logger.log_button_press("hall_call", "floor_3", "up")
        logger.stop_logging()
        
        # Check if files were created
        files_created = len(os.listdir(temp_dir)) > 0
        if files_created:
            print("✅ Logging system passed")
        else:
            print("❌ Logging system failed")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
    
    print("\nTest Summary Complete!")
    print("Run 'python main.py' to start the GUI application.")

if __name__ == "__main__":
    run_basic_tests()