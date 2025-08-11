"""
Simulation controller managing the overall simulation lifecycle.
"""

import time
import threading
from typing import Optional, Callable, List
import logging
from models.building import Building
from models.passenger import Passenger
from models.elevator import Direction
from .elevator_controller import ElevatorController
from simulation.logger import SimulationLogger

class SimulationController:
    """
    Controls the overall simulation execution and coordination.
    
    This class orchestrates all simulation components following
    the Single Responsibility Principle.
    """
    
    def __init__(self, building: Building, logger: SimulationLogger):
        """
        Initialize the simulation controller.
        
        Args:
            building: The building to simulate
            logger: Logger for simulation data
        """
        self._building = building
        self._logger = logger
        self._elevator_controller = ElevatorController(building)
        
        self._is_running = False
        self._is_paused = False
        self._simulation_thread: Optional[threading.Thread] = None
        self._simulation_speed = 1.0  # Real-time multiplier
        self._last_update_time = time.time()
        
        # Callbacks for UI updates
        self._update_callbacks: List[Callable] = []
        
        # Passengers
        self._passengers = {}
        self._passenger_counter = 0
        
        logging.info("Simulation controller initialized")
    
    def add_update_callback(self, callback: Callable) -> None:
        """Add a callback function to be called on each simulation update."""
        self._update_callbacks.append(callback)
    
    def start_simulation(self) -> bool:
        """
        Start the simulation.
        
        Returns:
            bool: True if simulation started successfully
        """
        if self._is_running:
            logging.warning("Simulation already running")
            return False
        
        self._is_running = True
        self._is_paused = False
        self._last_update_time = time.time()
        
        self._simulation_thread = threading.Thread(target=self._simulation_loop)
        self._simulation_thread.daemon = True
        self._simulation_thread.start()
        
        logging.info("Simulation started")
        return True
    
    def pause_simulation(self) -> None:
        """Pause the simulation."""
        self._is_paused = True
        logging.info("Simulation paused")
    
    def resume_simulation(self) -> None:
        """Resume the simulation."""
        self._is_paused = False
        self._last_update_time = time.time()
        logging.info("Simulation resumed")
    
    def stop_simulation(self) -> None:
        """Stop the simulation."""
        self._is_running = False
        if self._simulation_thread:
            self._simulation_thread.join(timeout=2.0)
        logging.info("Simulation stopped")
    
    def set_simulation_speed(self, speed: float) -> None:
        """
        Set simulation speed multiplier.
        
        Args:
            speed: Speed multiplier (1.0 = real-time, 2.0 = 2x speed, etc.)
        """
        self._simulation_speed = max(0.1, min(10.0, speed))
        logging.info(f"Simulation speed set to {self._simulation_speed}x")
    
    def add_passenger(self, origin_floor: int, destination_floor: int) -> str:
        """
        Add a new passenger to the simulation.
        
        Args:
            origin_floor: Starting floor
            destination_floor: Target floor
            
        Returns:
            str: Passenger ID
        """
        self._passenger_counter += 1
        passenger_id = f"P{self._passenger_counter:04d}"
        
        passenger = Passenger(passenger_id, origin_floor, destination_floor)
        self._passengers[passenger_id] = passenger
        
        # Add passenger to floor waiting queue
        floor = self._building.get_floor(origin_floor)
        if floor:
            floor.add_waiting_passenger(passenger_id, passenger.wants_to_go_up)
        
        # Request elevator
        direction = Direction.UP if passenger.wants_to_go_up else Direction.DOWN
        self._elevator_controller.request_elevator(
            origin_floor, 
            direction
        )
        
        logging.info(f"Added passenger {passenger_id}: "
                    f"floor {origin_floor} -> {destination_floor}")
        
        return passenger_id
    
    def press_elevator_button(self, elevator_id: str, floor: int) -> bool:
        """
        Simulate pressing a button inside an elevator.
        
        Args:
            elevator_id: ID of the elevator
            floor: Target floor
            
        Returns:
            bool: True if button press was successful
        """
        elevator = self._building.get_elevator(elevator_id)
        if elevator:
            success = elevator.add_floor_request(floor)
            if success:
                logging.info(f"Elevator {elevator_id} button pressed: floor {floor}")
            return success
        return False
    
    def press_hall_button(self, floor: int, direction: str) -> bool:
        """
        Simulate pressing a hall call button.
        
        Args:
            floor: Floor number
            direction: 'up' or 'down'
            
        Returns:
            bool: True if button press was successful
        """
        from models.elevator import Direction
        
        dir_enum = Direction.UP if direction.lower() == 'up' else Direction.DOWN
        success = self._elevator_controller.request_elevator(floor, dir_enum)
        
        if success:
            logging.info(f"Hall button pressed: floor {floor}, direction {direction}")
        
        return success
    
    def get_simulation_status(self) -> dict:
        """Get comprehensive simulation status."""
        return {
            'is_running': self._is_running,
            'is_paused': self._is_paused,
            'simulation_speed': self._simulation_speed,
            'building_status': self._building.get_building_status(),
            'controller_metrics': self._elevator_controller.get_performance_metrics(),
            'passenger_count': len(self._passengers),
            'active_passengers': len([p for p in self._passengers.values() 
                                    if p.state.value != 'arrived'])
        }
    
    def _handle_passenger_movement(self) -> None:
        """Handle passenger boarding and exiting when elevators arrive at floors."""
        building_status = self._building.get_building_status()
        
        for elevator_id, elevator_status in building_status['elevators'].items():
            elevator = self._building.get_elevator(elevator_id)
            if not elevator:
                continue
            
            current_floor = elevator_status['current_floor']
            state = elevator_status['state']
            
            # Only handle passenger movement when doors are open
            if state == 'doors_open':
                # Handle passengers exiting (arriving at destination)
                self._handle_passengers_exiting(elevator, current_floor)
                
                # Handle passengers boarding (waiting at current floor)
                self._handle_passengers_boarding(elevator, current_floor)
    
    def _handle_passengers_exiting(self, elevator, floor_num: int) -> None:
        """Handle passengers exiting the elevator at their destination."""
        elevator_status = elevator.get_status_dict()
        passengers_to_remove = []
        
        for passenger_id in elevator_status['passengers']:
            if passenger_id in self._passengers:
                passenger = self._passengers[passenger_id]
                if passenger.destination_floor == floor_num:
                    # Passenger has reached destination
                    passenger.arrive_at_destination()
                    passengers_to_remove.append(passenger_id)
                    logging.info(f"Passenger {passenger_id} arrived at floor {floor_num}")
        
        # Remove passengers from elevator
        for passenger_id in passengers_to_remove:
            elevator.remove_passenger(passenger_id)
    
    def _handle_passengers_boarding(self, elevator, floor_num: int) -> None:
        """Handle passengers boarding the elevator from the current floor."""
        floor = self._building.get_floor(floor_num)
        if not floor:
            return
        
        floor_status = floor.get_status_dict()
        elevator_status = elevator.get_status_dict()
        
        # Check if elevator has capacity
        if elevator_status['passenger_count'] >= elevator_status['capacity']:
            return
        
        # Determine which direction passengers want to go
        direction = elevator_status['direction']
        if direction == 'UP' or direction == 'NONE':
            # Board passengers going up
            for passenger_id in list(floor_status['waiting_up']):
                if elevator_status['passenger_count'] < elevator_status['capacity']:
                    passenger = self._passengers.get(passenger_id)
                    if passenger and passenger.state.value == 'waiting':
                        if elevator.add_passenger(passenger_id, passenger.destination_floor):
                            floor.remove_waiting_passenger(passenger_id)
                            passenger.board_elevator(elevator.id)
                            logging.info(f"Passenger {passenger_id} boarded elevator {elevator.id}")
        
        if direction == 'DOWN' or direction == 'NONE':
            # Board passengers going down
            for passenger_id in list(floor_status['waiting_down']):
                if elevator_status['passenger_count'] < elevator_status['capacity']:
                    passenger = self._passengers.get(passenger_id)
                    if passenger and passenger.state.value == 'waiting':
                        if elevator.add_passenger(passenger_id, passenger.destination_floor):
                            floor.remove_waiting_passenger(passenger_id)
                            passenger.board_elevator(elevator.id)
                            logging.info(f"Passenger {passenger_id} boarded elevator {elevator.id}")
    
    def _simulation_loop(self) -> None:
        """Main simulation loop running in separate thread."""
        while self._is_running:
            if not self._is_paused:
                current_time = time.time()
                delta_time = (current_time - self._last_update_time) * self._simulation_speed
                
                # Update building (elevators)
                self._building.update(delta_time)
                
                # Handle passenger boarding and exiting
                self._handle_passenger_movement()
                
                # Log simulation state
                self._logger.log_simulation_state(self.get_simulation_status())
                
                # Notify UI callbacks
                for callback in self._update_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logging.error(f"Error in update callback: {e}")
                
                self._last_update_time = current_time
            
            # Control simulation update rate
            time.sleep(0.1)  # 10 FPS update rate