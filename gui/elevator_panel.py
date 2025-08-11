"""
Elevator visualization panel showing elevator state and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from models.elevator import Elevator, ElevatorState
from models.building import Building

class ElevatorPanel(ttk.Frame):
    """
    Visual representation of a single elevator with interactive controls.
    
    This class provides a graphical display of elevator state and allows
    users to interact with elevator buttons.
    """
    
    def __init__(self, parent, elevator: Elevator, num_floors: int, 
                 command_callback: Optional[Callable[[str, int], None]] = None,
                 building: Optional['Building'] = None):
        """
        Initialize the elevator panel.
        
        Args:
            parent: Parent Tkinter widget
            elevator: Elevator model to display
            num_floors: Total number of floors in building
            command_callback: Callback for button presses
            building: Building model for accessing floor information
        """
        super().__init__(parent)
        
        self._elevator = elevator
        self._num_floors = num_floors
        self._command_callback = command_callback
        self._building = building
        
        # Visual elements
        self._floor_labels = {}
        self._button_widgets = {}
        self._elevator_indicator = None
        
        self._setup_panel()
        
    def _setup_panel(self) -> None:
        """Set up the elevator panel layout."""
        # Title
        title_label = ttk.Label(self, text=f"Elevator {self._elevator.id}", 
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Create elevator shaft visualization
        self._setup_elevator_shaft()
        
        # Create floor buttons panel
        self._setup_floor_buttons()
        
        # Create status display
        self._setup_status_display()
    
    def _setup_elevator_shaft(self) -> None:
        """Create the elevator shaft visualization."""
        shaft_frame = ttk.LabelFrame(self, text="Elevator Shaft", padding="5")
        shaft_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Title for elevator shaft
        title_frame = ttk.Frame(shaft_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=2)
        
        ttk.Label(title_frame, text="Floor", font=("Arial", 8, "bold")).grid(row=0, column=0, padx=2)
        ttk.Label(title_frame, text="Elevator", font=("Arial", 8, "bold")).grid(row=0, column=1, padx=2)
        
        # Create floor indicators (top to bottom)
        for floor in range(self._num_floors, 0, -1):
            floor_frame = ttk.Frame(shaft_frame)
            floor_frame.grid(row=self._num_floors - floor + 1, column=0, 
                           sticky="ew", pady=1, padx=5)
            
            # Floor number label
            floor_label = ttk.Label(floor_frame, text=str(floor), width=3)
            floor_label.grid(row=0, column=0, padx=2)
            
            # Elevator position indicator
            indicator = tk.Label(floor_frame, text="", width=8, height=2,
                               bg="lightgray", relief="solid", borderwidth=1)
            indicator.grid(row=0, column=1, padx=2)
            
            self._floor_labels[floor] = indicator
            

        
        
        
        # Set initial elevator position
        self._update_elevator_position()
    
    def _setup_floor_buttons(self) -> None:
        """Create floor selection buttons."""
        buttons_frame = ttk.LabelFrame(self, text="Floor Buttons", padding="5")
        buttons_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Create buttons in a grid layout
        buttons_per_row = 5
        row = 0
        col = 0
        
        for floor in range(1, self._num_floors + 1):
            btn = tk.Button(buttons_frame, text=str(floor), width=4, height=2,
                           command=lambda f=floor: self._on_button_press(f))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            self._button_widgets[floor] = btn
            
            col += 1
            if col >= buttons_per_row:
                col = 0
                row += 1
    
    def _setup_status_display(self) -> None:
        """Create status information display."""
        status_frame = ttk.LabelFrame(self, text="Status", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Status labels
        self._state_label = ttk.Label(status_frame, text="State: Idle")
        self._state_label.grid(row=0, column=0, sticky="w", pady=2)
        
        self._direction_label = ttk.Label(status_frame, text="Direction: None")
        self._direction_label.grid(row=1, column=0, sticky="w", pady=2)
        
        self._requests_label = ttk.Label(status_frame, text="Requests: None")
        self._requests_label.grid(row=2, column=0, sticky="w", pady=2)
        

        
        # Door status indicator
        self._door_indicator = tk.Label(status_frame, text="DOORS CLOSED",
                                      bg="red", fg="white", font=("Arial", 10, "bold"))
        self._door_indicator.grid(row=6, column=0, pady=5, sticky="ew")
    
    def _on_button_press(self, floor: int) -> None:
        """Handle floor button press."""
        if self._command_callback:
            self._command_callback(self._elevator.id, floor)
        
        # Visual feedback
        btn = self._button_widgets[floor]
        original_bg = btn.cget("bg")
        btn.config(bg="cyan")
        self.after(500, lambda: btn.config(bg=original_bg))
    
    def _update_elevator_position(self) -> None:
        """Update the visual elevator position indicator."""
        # Clear all position indicators
        for floor, indicator in self._floor_labels.items():
            indicator.config(bg="lightgray", text="")
        
        # Set current floor indicator
        current_floor = self._elevator.current_floor
        if current_floor in self._floor_labels:
            indicator = self._floor_labels[current_floor]
            
            # Color based on elevator state
            state = self._elevator.state
            if state == ElevatorState.IDLE:
                bg_color = "green"
                text = "IDLE"
            elif state in [ElevatorState.MOVING_UP, ElevatorState.MOVING_DOWN]:
                bg_color = "blue"
                text = "MOVING"
            elif state == ElevatorState.DOORS_OPEN:
                bg_color = "orange"
                text = "OPEN"
            else:
                bg_color = "magenta"
                text = state.value.upper()
            

            
            indicator.config(bg=bg_color, text=text, fg="white")
    
    def _update_status_labels(self) -> None:
        """Update status information labels."""
        # State
        state_text = self._elevator.state.value.replace('_', ' ').title()
        self._state_label.config(text=f"State: {state_text}")
        
        # Direction
        direction_text = self._elevator.direction.name.title()
        self._direction_label.config(text=f"Direction: {direction_text}")
        

        
        # Requests
        requests = sorted(list(self._elevator.floor_requests))
        if requests:
            requests_text = f"Requests: {', '.join(map(str, requests))}"
        else:
            requests_text = "Requests: None"
        self._requests_label.config(text=requests_text)
        

        

        
        # Door status
        if self._elevator.is_door_open:
            self._door_indicator.config(text="DOORS OPEN", bg="green")
        else:
            self._door_indicator.config(text="DOORS CLOSED", bg="red")
    
    def _update_button_highlights(self) -> None:
        """Update button highlighting for active requests."""
        # Reset all buttons
        for btn in self._button_widgets.values():
            btn.config(bg="SystemButtonFace")  # Default button color
        
        # Highlight active requests
        for floor in self._elevator.floor_requests:
            if floor in self._button_widgets:
                self._button_widgets[floor].config(bg="lightblue")
    

    

    
    def update_display(self, elevator: Elevator, passengers_info: dict = None) -> None:
        """
        Update the panel display with current elevator state.
        
        Args:
            elevator: Updated elevator model
            passengers_info: Dictionary mapping passenger IDs to destination floors
        """
        self._elevator = elevator
        self._passengers_info = passengers_info or {}
        
        self._update_elevator_position()
        self._update_status_labels()
        self._update_button_highlights()
    
    def destroy(self) -> None:
        """Clean up the panel."""
        super().destroy()