"""
Building configuration management from CSV files.
"""

import csv
from typing import List, Dict, Any
from pathlib import Path
import logging

class BuildingConfig:
    """
    Manages building configuration loaded from CSV files.
    
    This class handles the Open/Closed Principle by being open for
    extension to support different configuration formats.
    """
    
    def __init__(self, config_file: str):
        """
        Initialize building configuration.
        
        Args:
            config_file: Path to the building configuration CSV file
        """
        self._config_file = Path(config_file)
        self._building_data = {}
        self._elevators_data = []
        
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from CSV file."""
        if not self._config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self._config_file}")
        
        try:
            with open(self._config_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    section = row.get('section', '').lower()
                    
                    if section == 'building':
                        self._building_data = {
                            'id': row.get('id', 'building_1'),
                            'num_floors': int(row.get('num_floors', 10)),
                            'name': row.get('name', 'Default Building')
                        }
                    
                    elif section == 'elevator':
                        elevator_config = {
                            'id': row.get('id', f'elevator_{len(self._elevators_data)}'),
                            'capacity': int(row.get('capacity', 8)),
                            'speed': float(row.get('speed', 2.0)),
                            'initial_floor': int(row.get('initial_floor', 1))
                        }
                        self._elevators_data.append(elevator_config)
            
            logging.info(f"Configuration loaded from {self._config_file}")
            
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise
    
    @property
    def building_data(self) -> Dict[str, Any]:
        """Get building configuration data."""
        return self._building_data.copy()
    
    @property
    def elevators_data(self) -> List[Dict[str, Any]]:
        """Get elevators configuration data."""
        return self._elevators_data.copy()
    
    def get_building_id(self) -> str:
        """Get building ID."""
        return self._building_data.get('id', 'building_1')
    
    def get_num_floors(self) -> int:
        """Get number of floors."""
        return self._building_data.get('num_floors', 10)
    
    def get_elevators_count(self) -> int:
        """Get number of elevators."""
        return len(self._elevators_data)
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the configuration and return any error messages.
        
        Returns:
            List[str]: List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self._building_data:
            errors.append("No building configuration found")
        
        if not self._elevators_data:
            errors.append("No elevator configuration found")
        
        num_floors = self.get_num_floors()
        if num_floors < 2:
            errors.append("Building must have at least 2 floors")
        
        for i, elevator in enumerate(self._elevators_data):
            if elevator.get('capacity', 0) <= 0:
                errors.append(f"Elevator {i}: Invalid capacity")
            
            if elevator.get('speed', 0) <= 0:
                errors.append(f"Elevator {i}: Invalid speed")
            
            initial_floor = elevator.get('initial_floor', 1)
            if not (1 <= initial_floor <= num_floors):
                errors.append(f"Elevator {i}: Invalid initial floor")
        
        return errors

    @staticmethod
    def create_sample_config(file_path: str) -> None:
        """
        Create a sample configuration file.
        
        Args:
            file_path: Path where to create the sample file
        """
        sample_data = [
            ['section', 'id', 'num_floors', 'name', 'capacity', 'speed', 'initial_floor'],
            ['building', 'main_building', '10', 'Main Office Building', '', '', ''],
            ['elevator', 'elevator_A', '', '', '8', '2.5', '1'],
            ['elevator', 'elevator_B', '', '', '12', '2.0', '1']
        ]
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sample_data)
        
        logging.info(f"Sample configuration created at {file_path}")