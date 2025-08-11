"""
Building model that manages multiple elevators and floors.
"""

from typing import List, Dict, Optional
import logging
from .elevator import Elevator, Direction
from .floor import Floor

class Building:
    """
    Represents a building with multiple elevators and floors.
    
    This class follows the Single Responsibility Principle by managing
    the overall building structure and coordinating between elevators.
    """
    
    def __init__(self, building_id: str, num_floors: int, 
                 elevators_config: List[dict]):
        """
        Initialize a building instance.
        
        Args:
            building_id: Unique identifier for this building
            num_floors: Total number of floors
            elevators_config: List of elevator configuration dictionaries
        """
        self._id = building_id
        self._num_floors = num_floors
        self._floors = {}
        self._elevators = {}
        
        self._initialize_floors()
        self._initialize_elevators(elevators_config)
        
        logging.info(f"Building {self._id} initialized with "
                    f"{len(self._elevators)} elevators and "
                    f"{num_floors} floors")
    
    def _initialize_floors(self) -> None:
        """Initialize all floors in the building."""
        for floor_num in range(1, self._num_floors + 1):
            self._floors[floor_num] = Floor(floor_num)
    
    def _initialize_elevators(self, elevators_config: List[dict]) -> None:
        """Initialize elevators from configuration."""
        for config in elevators_config:
            elevator_id = config.get('id', f'elevator_{len(self._elevators)}')
            capacity = config.get('capacity', 8)
            floors_range = (1, self._num_floors)
            speed = config.get('speed', 2.0)
            
            elevator = Elevator(elevator_id, capacity, floors_range, speed)
            self._elevators[elevator_id] = elevator
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def num_floors(self) -> int:
        return self._num_floors
    
    @property
    def elevators(self) -> Dict[str, Elevator]:
        return self._elevators.copy()
    
    @property
    def floors(self) -> Dict[int, Floor]:
        return self._floors.copy()
    
    def get_elevator(self, elevator_id: str) -> Optional[Elevator]:
        """Get elevator by ID."""
        return self._elevators.get(elevator_id)
    
    def get_floor(self, floor_num: int) -> Optional[Floor]:
        """Get floor by number."""
        return self._floors.get(floor_num)
    
    def request_elevator(self, floor: int, direction: Direction) -> bool:
        """
        Request an elevator to a specific floor.
        
        Args:
            floor: Floor number where elevator is requested
            direction: Desired direction of travel
            
        Returns:
            bool: True if request was successfully assigned to an elevator
        """
        if not self._is_valid_floor(floor):
            logging.warning(f"Invalid floor request: {floor}")
            return False
        
        # Simple dispatching: assign to nearest idle elevator
        # or elevator already going in the right direction
        best_elevator = self._find_best_elevator(floor, direction)
        
        if best_elevator:
            success = best_elevator.add_hall_call(floor, direction)
            if success:
                logging.info(f"Hall call assigned to elevator {best_elevator.id}: "
                           f"floor {floor}, direction {direction.name}")
            return success
        
        logging.warning(f"No available elevator for floor {floor}, "
                       f"direction {direction.name}")
        return False
    
    def _find_best_elevator(self, floor: int, direction: Direction) -> Optional[Elevator]:
        """Find the best elevator to handle a hall call."""
        available_elevators = []
        
        for elevator in self._elevators.values():
            if elevator.state.value != "maintenance" and elevator.state.value != "emergency":
                distance = abs(elevator.current_floor - floor)
                # Prefer elevators that are idle or moving in the same direction
                priority = 0
                if elevator.state.value == "idle":
                    priority = 2
                elif ((direction == Direction.UP and elevator.direction == Direction.UP) or
                      (direction == Direction.DOWN and elevator.direction == Direction.DOWN)):
                    priority = 1
                
                available_elevators.append((elevator, distance, priority))
        
        if not available_elevators:
            return None
        
        # Sort by priority (desc) then by distance (asc)
        available_elevators.sort(key=lambda x: (-x[2], x[1]))
        return available_elevators[0][0]
    
    def update(self, delta_time: float) -> None:
        """Update all elevators in the building."""
        for elevator in self._elevators.values():
            elevator.update(delta_time)
    
    def _is_valid_floor(self, floor: int) -> bool:
        """Check if floor number is valid."""
        return 1 <= floor <= self._num_floors
    
    def get_building_status(self) -> dict:
        """Get comprehensive building status."""
        return {
            'id': self._id,
            'num_floors': self._num_floors,
            'elevators': {eid: elevator.get_status_dict() 
                         for eid, elevator in self._elevators.items()},
            'total_elevators': len(self._elevators)
        }