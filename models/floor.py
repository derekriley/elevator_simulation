"""
Floor model representing a single floor in the building.
"""

from typing import Set
import logging

class Floor:
    """
    Represents a single floor in the building.
    
    This class manages floor-specific state and passenger queues.
    """
    
    def __init__(self, floor_number: int):
        """
        Initialize a floor instance.
        
        Args:
            floor_number: The floor number (1-based)
        """
        self._number = floor_number
        self._up_button_pressed = False
        self._down_button_pressed = False
        self._waiting_passengers_up: Set[str] = set()
        self._waiting_passengers_down: Set[str] = set()
        
        logging.debug(f"Floor {self._number} initialized")
    
    @property
    def number(self) -> int:
        return self._number
    
    @property
    def up_button_pressed(self) -> bool:
        return self._up_button_pressed
    
    @property
    def down_button_pressed(self) -> bool:
        return self._down_button_pressed
    
    @property
    def waiting_passengers_up(self) -> Set[str]:
        return self._waiting_passengers_up.copy()
    
    @property
    def waiting_passengers_down(self) -> Set[str]:
        return self._waiting_passengers_down.copy()
    
    def press_up_button(self) -> None:
        """Press the up button on this floor."""
        if not self._up_button_pressed:
            self._up_button_pressed = True
            logging.debug(f"Floor {self._number}: Up button pressed")
    
    def press_down_button(self) -> None:
        """Press the down button on this floor."""
        if not self._down_button_pressed:
            self._down_button_pressed = True
            logging.debug(f"Floor {self._number}: Down button pressed")
    
    def clear_up_button(self) -> None:
        """Clear the up button (elevator arrived)."""
        self._up_button_pressed = False
        logging.debug(f"Floor {self._number}: Up button cleared")
    
    def clear_down_button(self) -> None:
        """Clear the down button (elevator arrived)."""
        self._down_button_pressed = False
        logging.debug(f"Floor {self._number}: Down button cleared")
    
    def add_waiting_passenger(self, passenger_id: str, going_up: bool) -> None:
        """
        Add a passenger waiting on this floor.
        
        Args:
            passenger_id: Unique identifier for the passenger
            going_up: True if passenger wants to go up, False for down
        """
        if going_up:
            self._waiting_passengers_up.add(passenger_id)
        else:
            self._waiting_passengers_down.add(passenger_id)
        
        logging.debug(f"Floor {self._number}: Passenger {passenger_id} "
                     f"waiting to go {'up' if going_up else 'down'}")
    
    def remove_waiting_passenger(self, passenger_id: str) -> bool:
        """
        Remove a passenger from the waiting queue.
        
        Args:
            passenger_id: Unique identifier for the passenger
            
        Returns:
            bool: True if passenger was found and removed
        """
        removed = False
        if passenger_id in self._waiting_passengers_up:
            self._waiting_passengers_up.remove(passenger_id)
            removed = True
        elif passenger_id in self._waiting_passengers_down:
            self._waiting_passengers_down.remove(passenger_id)
            removed = True
        
        if removed:
            logging.debug(f"Floor {self._number}: Passenger {passenger_id} removed")
        
        return removed
    
    def get_status_dict(self) -> dict:
        """Get current floor status as a dictionary."""
        return {
            'number': self._number,
            'up_button_pressed': self._up_button_pressed,
            'down_button_pressed': self._down_button_pressed,
            'waiting_up': list(self._waiting_passengers_up),
            'waiting_down': list(self._waiting_passengers_down)
        }