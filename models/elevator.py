"""
Elevator model representing the physical elevator car and its state.
"""

from enum import Enum
from typing import Set, Optional
import time
import logging

class ElevatorState(Enum):
    """Enumeration of possible elevator states."""
    IDLE = "idle"
    MOVING_UP = "moving_up"
    MOVING_DOWN = "moving_down"
    DOORS_OPENING = "doors_opening"
    DOORS_OPEN = "doors_open"
    DOORS_CLOSING = "doors_closing"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"

class Direction(Enum):
    """Enumeration of elevator movement directions."""
    UP = 1
    DOWN = -1
    NONE = 0

class Elevator:
    """
    Represents a single elevator car with its state and capabilities.
    
    This class encapsulates all the physical properties and state management
    of an elevator car following the Single Responsibility Principle.
    """
    
    def __init__(self, elevator_id: str, capacity: int = 8, 
                 floors_range: tuple = (1, 10), speed: float = 2.0):
        """
        Initialize an elevator instance.
        
        Args:
            elevator_id: Unique identifier for this elevator
            capacity: Maximum number of passengers
            floors_range: Tuple of (min_floor, max_floor)
            speed: Speed in floors per second
        """
        self._id = elevator_id
        self._capacity = capacity
        self._min_floor = floors_range[0]
        self._max_floor = floors_range[1]
        self._speed = speed
        
        # Current state
        self._current_floor = 1
        self._state = ElevatorState.IDLE
        self._direction = Direction.NONE
        self._passengers = set()
        self._door_open = False
        
        # Requests
        self._floor_requests = set()  # Internal button presses
        self._up_requests = set()     # Up hall calls
        self._down_requests = set()   # Down hall calls
        
        # Timing
        self._door_timer = 0.0
        self._move_timer = 0.0
        self._last_update = time.time()
        
        # Configuration
        self._door_open_time = 3.0    # Seconds doors stay open
        self._door_operation_time = 2.0  # Seconds to open/close doors
        
        logging.info(f"Elevator {self._id} initialized: "
                    f"floors {self._min_floor}-{self._max_floor}, "
                    f"capacity {self._capacity}")
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def current_floor(self) -> int:
        return self._current_floor
    
    @property
    def state(self) -> ElevatorState:
        return self._state
    
    @property
    def direction(self) -> Direction:
        return self._direction
    
    @property
    def passenger_count(self) -> int:
        return len(self._passengers)
    
    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def is_door_open(self) -> bool:
        return self._door_open
    
    @property
    def floor_requests(self) -> Set[int]:
        return self._floor_requests.copy()
    
    def add_floor_request(self, floor: int) -> bool:
        """
        Add an internal floor request (button pressed inside elevator).
        
        Args:
            floor: Target floor number
            
        Returns:
            bool: True if request was added successfully
        """
        if not self._is_valid_floor(floor):
            return False
        
        if floor != self._current_floor:
            self._floor_requests.add(floor)
            logging.debug(f"Elevator {self._id}: Floor {floor} requested")
        
        return True
    
    def add_hall_call(self, floor: int, direction: Direction) -> bool:
        """
        Add a hall call request (button pressed outside elevator).
        
        Args:
            floor: Floor where call was made
            direction: Desired direction of travel
            
        Returns:
            bool: True if request was added successfully
        """
        if not self._is_valid_floor(floor):
            return False
        
        # Ensure direction is a Direction enum
        if isinstance(direction, bool):
            direction = Direction.UP if direction else Direction.DOWN
        elif not isinstance(direction, Direction):
            return False
        
        if direction == Direction.UP:
            self._up_requests.add(floor)
        elif direction == Direction.DOWN:
            self._down_requests.add(floor)
        
        logging.debug(f"Elevator {self._id}: Hall call floor {floor} {direction.name}")
        return True
    
    def update(self, delta_time: float) -> None:
        """
        Update elevator state based on elapsed time.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self._state == ElevatorState.IDLE:
            self._handle_idle_state()
        elif self._state == ElevatorState.MOVING_UP:
            self._handle_moving_state(Direction.UP, delta_time)
        elif self._state == ElevatorState.MOVING_DOWN:
            self._handle_moving_state(Direction.DOWN, delta_time)
        elif self._state == ElevatorState.DOORS_OPENING:
            self._handle_door_opening(delta_time)
        elif self._state == ElevatorState.DOORS_OPEN:
            self._handle_doors_open(delta_time)
        elif self._state == ElevatorState.DOORS_CLOSING:
            self._handle_door_closing(delta_time)
    
    def _handle_idle_state(self) -> None:
        """Handle elevator behavior when idle."""
        next_floor = self._get_next_destination()
        
        if next_floor is not None:
            if next_floor > self._current_floor:
                self._direction = Direction.UP
                self._state = ElevatorState.MOVING_UP
                self._move_timer = 0.0
            elif next_floor < self._current_floor:
                self._direction = Direction.DOWN
                self._state = ElevatorState.MOVING_DOWN
                self._move_timer = 0.0
            else:
                # Same floor - open doors
                self._state = ElevatorState.DOORS_OPENING
                self._door_timer = 0.0
    
    def _handle_moving_state(self, direction: Direction, delta_time: float) -> None:
        """Handle elevator movement between floors."""
        self._move_timer += delta_time
        time_per_floor = 1.0 / self._speed
        
        if self._move_timer >= time_per_floor:
            # Arrived at next floor
            self._current_floor += direction.value
            self._move_timer = 0.0
            
            if self._should_stop_at_current_floor():
                self._state = ElevatorState.DOORS_OPENING
                self._door_timer = 0.0
                self._direction = Direction.NONE
            elif not self._has_requests_in_direction(direction):
                # No more requests in this direction
                self._state = ElevatorState.IDLE
                self._direction = Direction.NONE
    
    def _handle_door_opening(self, delta_time: float) -> None:
        """Handle door opening sequence."""
        self._door_timer += delta_time
        
        if self._door_timer >= self._door_operation_time:
            self._door_open = True
            self._state = ElevatorState.DOORS_OPEN
            self._door_timer = 0.0
            self._clear_requests_at_current_floor()
    
    def _handle_doors_open(self, delta_time: float) -> None:
        """Handle doors open state."""
        self._door_timer += delta_time
        
        if self._door_timer >= self._door_open_time:
            self._state = ElevatorState.DOORS_CLOSING
            self._door_timer = 0.0
    
    def _handle_door_closing(self, delta_time: float) -> None:
        """Handle door closing sequence."""
        self._door_timer += delta_time
        
        if self._door_timer >= self._door_operation_time:
            self._door_open = False
            self._state = ElevatorState.IDLE
            self._door_timer = 0.0
    
    def _should_stop_at_current_floor(self) -> bool:
        """Check if elevator should stop at current floor."""
        return (self._current_floor in self._floor_requests or
                self._current_floor in self._up_requests or
                self._current_floor in self._down_requests)
    
    def _clear_requests_at_current_floor(self) -> None:
        """Clear all requests for the current floor."""
        self._floor_requests.discard(self._current_floor)
        self._up_requests.discard(self._current_floor)
        self._down_requests.discard(self._current_floor)
    
    def _get_next_destination(self) -> Optional[int]:
        """Get the next floor the elevator should visit."""
        all_requests = (self._floor_requests | 
                       self._up_requests | 
                       self._down_requests)
        
        if not all_requests:
            return None
        
        # Simple strategy: go to nearest floor
        return min(all_requests, key=lambda f: abs(f - self._current_floor))
    
    def _has_requests_in_direction(self, direction: Direction) -> bool:
        """Check if there are any requests in the given direction."""
        all_requests = (self._floor_requests | 
                       self._up_requests | 
                       self._down_requests)
        
        if direction == Direction.UP:
            return any(f > self._current_floor for f in all_requests)
        elif direction == Direction.DOWN:
            return any(f < self._current_floor for f in all_requests)
        
        return False
    
    def _is_valid_floor(self, floor: int) -> bool:
        """Check if floor number is valid for this elevator."""
        return self._min_floor <= floor <= self._max_floor
    
    def add_passenger(self, passenger_id: str, destination_floor: int) -> bool:
        """
        Add a passenger to the elevator.
        
        Args:
            passenger_id: Unique identifier for the passenger
            destination_floor: Floor where passenger wants to go
            
        Returns:
            bool: True if passenger was added successfully
        """
        if len(self._passengers) >= self._capacity:
            logging.warning(f"Elevator {self._id} is at capacity")
            return False
        
        if not self._is_valid_floor(destination_floor):
            logging.warning(f"Invalid destination floor {destination_floor}")
            return False
        
        # Add passenger and their destination
        self._passengers.add(passenger_id)
        self._floor_requests.add(destination_floor)
        
        logging.info(f"Passenger {passenger_id} boarded elevator {self._id}, "
                    f"destination: floor {destination_floor}")
        return True
    
    def remove_passenger(self, passenger_id: str) -> bool:
        """
        Remove a passenger from the elevator.
        
        Args:
            passenger_id: Unique identifier for the passenger
            
        Returns:
            bool: True if passenger was found and removed
        """
        if passenger_id in self._passengers:
            self._passengers.remove(passenger_id)
            logging.info(f"Passenger {passenger_id} exited elevator {self._id}")
            return True
        return False
    
    def get_passengers(self) -> Set[str]:
        """Get set of passenger IDs currently in the elevator."""
        return self._passengers.copy()
    
    def get_status_dict(self) -> dict:
        """Get current elevator status as a dictionary."""
        return {
            'id': self._id,
            'current_floor': self._current_floor,
            'state': self._state.value,
            'direction': self._direction.name,
            'passenger_count': len(self._passengers),
            'capacity': self._capacity,
            'door_open': self._door_open,
            'passengers': sorted(list(self._passengers)),
            'floor_requests': sorted(list(self._floor_requests)),
            'up_requests': sorted(list(self._up_requests)),
            'down_requests': sorted(list(self._down_requests))
        }