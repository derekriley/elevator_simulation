"""
Elevator controller implementing dispatch algorithms and control logic.
"""

from typing import Dict, List, Optional
import logging
from models.building import Building
from models.elevator import Elevator, Direction

class ElevatorController:
    """
    Controls elevator dispatching and optimization.
    
    This class implements the Dependency Inversion Principle by depending
    on abstractions rather than concrete implementations.
    """
    
    def __init__(self, building: Building, algorithm: str = "nearest_car"):
        """
        Initialize the elevator controller.
        
        Args:
            building: The building to control
            algorithm: Dispatch algorithm to use
        """
        self._building = building
        self._algorithm = algorithm
        self._request_queue = []
        
        logging.info(f"Elevator controller initialized with {algorithm} algorithm")
    
    def request_elevator(self, floor: int, direction: Direction) -> bool:
        """
        Handle an elevator request.
        
        Args:
            floor: Floor where elevator is requested
            direction: Desired direction
            
        Returns:
            bool: True if request was handled successfully
        """
        if self._algorithm == "nearest_car":
            return self._dispatch_nearest_car(floor, direction)
        elif self._algorithm == "scan":
            return self._dispatch_scan(floor, direction)
        else:
            return self._dispatch_fcfs(floor, direction)
    
    def _dispatch_nearest_car(self, floor: int, direction: Direction) -> bool:
        """Dispatch using nearest available car algorithm."""
        return self._building.request_elevator(floor, direction)
    
    def _dispatch_scan(self, floor: int, direction: Direction) -> bool:
        """Dispatch using SCAN (elevator) algorithm."""
        # Find elevator moving in same direction or idle elevator closest to floor
        elevators = self._building.elevators
        best_elevator = None
        best_score = float('inf')
        
        for elevator in elevators.values():
            if elevator.state.value in ["maintenance", "emergency"]:
                continue
            
            distance = abs(elevator.current_floor - floor)
            
            # Prefer elevators already moving in the same direction
            if elevator.direction == direction and elevator.current_floor < floor:
                score = distance - 100  # Bonus for same direction
            elif elevator.state.value == "idle":
                score = distance
            else:
                score = distance + 50  # Penalty for opposite direction
            
            if score < best_score:
                best_score = score
                best_elevator = elevator
        
        if best_elevator:
            return best_elevator.add_hall_call(floor, direction)
        
        return False
    
    def _dispatch_fcfs(self, floor: int, direction: Direction) -> bool:
        """Dispatch using First Come First Served algorithm."""
        # Simple FCFS: assign to first available elevator
        elevators = self._building.elevators
        
        for elevator in elevators.values():
            if elevator.state.value not in ["maintenance", "emergency"]:
                return elevator.add_hall_call(floor, direction)
        
        return False
    
    def get_performance_metrics(self) -> dict:
        """Calculate and return performance metrics."""
        elevators = self._building.elevators
        total_requests = 0
        total_energy = 0
        
        active_elevators = 0
        idle_elevators = 0
        
        for elevator in elevators.values():
            if elevator.state.value == "idle":
                idle_elevators += 1
            elif elevator.state.value in ["moving_up", "moving_down"]:
                active_elevators += 1
                total_energy += 1  # Simplified energy calculation
            
            total_requests += len(elevator.floor_requests)
        
        return {
            'total_elevators': len(elevators),
            'active_elevators': active_elevators,
            'idle_elevators': idle_elevators,
            'pending_requests': total_requests,
            'estimated_energy': total_energy
        }