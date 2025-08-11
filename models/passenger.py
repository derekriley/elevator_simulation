"""
Passenger model representing individuals using the elevator system.
"""

from enum import Enum
from typing import Optional
import time
import logging

class PassengerState(Enum):
    """Enumeration of possible passenger states."""
    WAITING = "waiting"
    IN_ELEVATOR = "in_elevator"
    ARRIVED = "arrived"

class Passenger:
    """
    Represents a passenger in the elevator system.
    
    This class tracks passenger journey and statistics.
    """
    
    def __init__(self, passenger_id: str, origin_floor: int, 
                 destination_floor: int, arrival_time: float = None):
        """
        Initialize a passenger instance.
        
        Args:
            passenger_id: Unique identifier for this passenger
            origin_floor: Floor where passenger starts
            destination_floor: Floor where passenger wants to go
            arrival_time: When passenger arrived (defaults to current time)
        """
        self._id = passenger_id
        self._origin_floor = origin_floor
        self._destination_floor = destination_floor
        self._state = PassengerState.WAITING
        self._elevator_id: Optional[str] = None
        
        # Timing information
        self._arrival_time = arrival_time or time.time()
        self._board_time: Optional[float] = None
        self._arrival_at_destination_time: Optional[float] = None
        
        logging.debug(f"Passenger {self._id} created: "
                     f"{self._origin_floor} -> {self._destination_floor}")
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def origin_floor(self) -> int:
        return self._origin_floor
    
    @property
    def destination_floor(self) -> int:
        return self._destination_floor
    
    @property
    def state(self) -> PassengerState:
        return self._state
    
    @property
    def elevator_id(self) -> Optional[str]:
        return self._elevator_id
    
    @property
    def wants_to_go_up(self) -> bool:
        return self._destination_floor > self._origin_floor
    
    def board_elevator(self, elevator_id: str, board_time: float = None) -> None:
        """
        Mark passenger as having boarded an elevator.
        
        Args:
            elevator_id: ID of the elevator being boarded
            board_time: Time of boarding (defaults to current time)
        """
        self._state = PassengerState.IN_ELEVATOR
        self._elevator_id = elevator_id
        self._board_time = board_time or time.time()
        
        logging.debug(f"Passenger {self._id} boarded elevator {elevator_id}")
    
    def arrive_at_destination(self, arrival_time: float = None) -> None:
        """
        Mark passenger as having arrived at destination.
        
        Args:
            arrival_time: Time of arrival (defaults to current time)
        """
        self._state = PassengerState.ARRIVED
        self._arrival_at_destination_time = arrival_time or time.time()
        
        logging.debug(f"Passenger {self._id} arrived at destination")
    
    def get_wait_time(self) -> Optional[float]:
        """Get time spent waiting for elevator."""
        if self._board_time:
            return self._board_time - self._arrival_time
        return None
    
    def get_travel_time(self) -> Optional[float]:
        """Get time spent in elevator."""
        if self._board_time and self._arrival_at_destination_time:
            return self._arrival_at_destination_time - self._board_time
        return None
    
    def get_total_time(self) -> Optional[float]:
        """Get total time from arrival to destination."""
        if self._arrival_at_destination_time:
            return self._arrival_at_destination_time - self._arrival_time
        return None
    
    def get_status_dict(self) -> dict:
        """Get passenger status as a dictionary."""
        return {
            'id': self._id,
            'origin_floor': self._origin_floor,
            'destination_floor': self._destination_floor,
            'state': self._state.value,
            'elevator_id': self._elevator_id,
            'arrival_time': self._arrival_time,
            'board_time': self._board_time,
            'destination_arrival_time': self._arrival_at_destination_time,
            'wait_time': self.get_wait_time(),
            'travel_time': self.get_travel_time(),
            'total_time': self.get_total_time()
        }