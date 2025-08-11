"""
Main simulation engine orchestrating all simulation components.
"""

import time
import random
from typing import List, Dict, Optional
import logging
from models.building import Building
from models.elevator import Direction
from controllers.simulation_controller import SimulationController
from config.simulation_config import SimulationConfig
from .logger import SimulationLogger

class ElevatorSimulator:
    """
    Main simulation engine that orchestrates all components.
    
    This class follows the Facade pattern to provide a simple
    interface to the complex simulation subsystem.
    """
    
    def __init__(self, building: Building, config: SimulationConfig = None):
        """
        Initialize the elevator simulator.
        
        Args:
            building: The building to simulate
            config: Simulation configuration (optional)
        """
        self._building = building
        self._config = config or SimulationConfig()
        self._logger = SimulationLogger()
        self._controller = SimulationController(building, self._logger)
        
        self._simulation_start_time: Optional[float] = None
        self._passenger_generation_active = True
        self._last_passenger_generation = 0.0
        
        logging.info("Elevator simulator initialized")
    
    @property
    def controller(self) -> SimulationController:
        """Get the simulation controller."""
        return self._controller
    
    @property
    def building(self) -> Building:
        """Get the building."""
        return self._building
    
    @property
    def logger(self) -> SimulationLogger:
        """Get the simulation logger."""
        return self._logger
    
    @property
    def passengers(self) -> Dict[str, 'Passenger']:
        """Get the passengers dictionary from the controller."""
        return self._controller._passengers
    
    def start_simulation(self) -> bool:
        """
        Start the simulation with configured scenarios.
        
        Returns:
            bool: True if simulation started successfully
        """
        self._simulation_start_time = time.time()
        self._logger.start_logging()
        
        # Add predefined passengers from configuration
        self._add_predefined_passengers()
        
        # Start automatic passenger generation if enabled
        if self._passenger_generation_active:
            self._controller.add_update_callback(self._generate_passengers)
        
        return self._controller.start_simulation()
    
    def stop_simulation(self) -> None:
        """Stop the simulation and finalize logging."""
        self._controller.stop_simulation()
        self._logger.stop_logging()
        
        # Generate final report
        self._generate_simulation_report()
    
    def pause_simulation(self) -> None:
        """Pause the simulation."""
        self._controller.pause_simulation()
    
    def resume_simulation(self) -> None:
        """Resume the simulation."""
        self._controller.resume_simulation()
    
    def set_passenger_generation(self, active: bool) -> None:
        """
        Enable or disable automatic passenger generation.
        
        Args:
            active: True to enable automatic passenger generation
        """
        self._passenger_generation_active = active
        logging.info(f"Passenger generation {'enabled' if active else 'disabled'}")
    
    def add_manual_passenger(self, origin_floor: int, destination_floor: int) -> str:
        """
        Manually add a passenger to the simulation.
        
        Args:
            origin_floor: Starting floor
            destination_floor: Target floor
            
        Returns:
            str: Passenger ID
        """
        return self._controller.add_passenger(origin_floor, destination_floor)
    
    def press_elevator_button(self, elevator_id: str, floor: int) -> bool:
        """Press a button inside an elevator."""
        return self._controller.press_elevator_button(elevator_id, floor)
    
    def press_hall_button(self, floor: int, direction: str) -> bool:
        """Press a hall call button."""
        return self._controller.press_hall_button(floor, direction)
    
    def get_simulation_status(self) -> dict:
        """Get comprehensive simulation status."""
        status = self._controller.get_simulation_status()
        
        if self._simulation_start_time:
            status['elapsed_time'] = time.time() - self._simulation_start_time
        
        return status
    
    def _add_predefined_passengers(self) -> None:
        """Add passengers defined in the configuration."""
        for passenger_config in self._config.passengers:
            # Schedule passenger addition based on arrival time
            # For now, add them immediately
            origin = passenger_config['origin_floor']
            destination = passenger_config['destination_floor']
            self._controller.add_passenger(origin, destination)
    
    def _generate_passengers(self) -> None:
        """Generate passengers automatically based on arrival rate."""
        if not self._passenger_generation_active:
            return
        
        current_time = time.time()
        if not hasattr(self, '_last_passenger_check'):
            self._last_passenger_check = current_time
        
        time_since_last = current_time - self._last_passenger_check
        arrival_rate = self._config.get_passenger_arrival_rate()
        
        # Poisson arrival process
        if random.random() < (arrival_rate * time_since_last):
            self._generate_random_passenger()
            self._last_passenger_check = current_time
    
    def _generate_random_passenger(self) -> None:
        """Generate a passenger with random origin and destination."""
        num_floors = self._building.num_floors
        
        origin = random.randint(1, num_floors)
        destination = random.randint(1, num_floors)
        
        # Ensure origin != destination
        while destination == origin:
            destination = random.randint(1, num_floors)
        
        self._controller.add_passenger(origin, destination)
        logging.debug(f"Generated random passenger: {origin} -> {destination}")
    
    def _generate_simulation_report(self) -> None:
        """Generate a comprehensive simulation report."""
        status = self.get_simulation_status()
        
        report = {
            'simulation_summary': {
                'duration': status.get('elapsed_time', 0),
                'total_passengers': status.get('passenger_count', 0),
                'building_floors': self._building.num_floors,
                'elevator_count': len(self._building.elevators)
            },
            'elevator_performance': {},
            'system_metrics': status.get('controller_metrics', {})
        }
        
        # Add per-elevator metrics
        for elevator_id, elevator in self._building.elevators.items():
            report['elevator_performance'][elevator_id] = elevator.get_status_dict()
        
        self._logger.log_simulation_report(report)
        logging.info("Simulation report generated")