"""
Simulation configuration management.
"""

import csv
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

class SimulationConfig:
    """
    Manages simulation scenarios and configuration.
    
    This class handles loading simulation scenarios from CSV files.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize simulation configuration.
        
        Args:
            config_file: Path to simulation configuration CSV file (optional)
        """
        self._config_file = Path(config_file) if config_file else None
        self._scenarios = []
        self._passengers = []
        self._simulation_params = {}
        
        if self._config_file:
            self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load simulation configuration from CSV file."""
        if not self._config_file.exists():
            raise FileNotFoundError(f"Simulation config file not found: {self._config_file}")
        
        try:
            with open(self._config_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    section = row.get('section', '').lower()
                    
                    if section == 'simulation':
                        self._simulation_params = {
                            'duration': float(row.get('duration', 300)),  # 5 minutes default
                            'speed_multiplier': float(row.get('speed_multiplier', 1.0)),
                            'passenger_arrival_rate': float(row.get('passenger_arrival_rate', 0.5))
                        }
                    
                    elif section == 'scenario':
                        scenario = {
                            'name': row.get('name', f'Scenario_{len(self._scenarios)}'),
                            'description': row.get('description', ''),
                            'start_time': float(row.get('start_time', 0)),
                            'passenger_count': int(row.get('passenger_count', 10)),
                            'floor_distribution': row.get('floor_distribution', 'uniform')
                        }
                        self._scenarios.append(scenario)
                    
                    elif section == 'passenger':
                        passenger = {
                            'id': row.get('id', f'passenger_{len(self._passengers)}'),
                            'arrival_time': float(row.get('arrival_time', 0)),
                            'origin_floor': int(row.get('origin_floor', 1)),
                            'destination_floor': int(row.get('destination_floor', 5))
                        }
                        self._passengers.append(passenger)
            
            logging.info(f"Simulation configuration loaded from {self._config_file}")
            
        except Exception as e:
            logging.error(f"Error loading simulation configuration: {e}")
            raise
    
    @property
    def scenarios(self) -> List[Dict[str, Any]]:
        """Get all scenarios."""
        return self._scenarios.copy()
    
    @property
    def passengers(self) -> List[Dict[str, Any]]:
        """Get all predefined passengers."""
        return self._passengers.copy()
    
    @property
    def simulation_params(self) -> Dict[str, Any]:
        """Get simulation parameters."""
        return self._simulation_params.copy()
    
    def get_simulation_duration(self) -> float:
        """Get simulation duration in seconds."""
        return self._simulation_params.get('duration', 300)
    
    def get_speed_multiplier(self) -> float:
        """Get simulation speed multiplier."""
        return self._simulation_params.get('speed_multiplier', 1.0)
    
    def get_passenger_arrival_rate(self) -> float:
        """Get passenger arrival rate (passengers per second)."""
        return self._simulation_params.get('passenger_arrival_rate', 0.5)
    
    @staticmethod
    def create_sample_config(file_path: str) -> None:
        """
        Create a sample simulation configuration file.
        
        Args:
            file_path: Path where to create the sample file
        """
        sample_data = [
            ['section', 'name', 'description', 'duration', 'speed_multiplier', 
             'passenger_arrival_rate', 'start_time', 'passenger_count', 
             'floor_distribution', 'id', 'arrival_time', 'origin_floor', 'destination_floor'],
            ['simulation', '', '', '600', '1.0', '0.3', '', '', '', '', '', '', ''],
            ['scenario', 'Morning Rush', 'Typical morning rush hour', '', '', '', '0', '20', 'ground_heavy', '', '', '', ''],
            ['scenario', 'Lunch Time', 'Lunch hour traffic', '', '', '', '300', '15', 'uniform', '', '', '', ''],
            ['passenger', '', '', '', '', '', '', '', '', 'test_passenger_1', '10', '1', '8'],
            ['passenger', '', '', '', '', '', '', '', '', 'test_passenger_2', '15', '5', '2']
        ]
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sample_data)
        
        logging.info(f"Sample simulation configuration created at {file_path}")