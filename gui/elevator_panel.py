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
        self._waiting_passenger_labels = {}  # Store waiting passenger count labels
        
        self._setup_panel()
        
    def _setup_panel(self) -> None:
        """Set up the elevator panel layout."""
        # Title
        title_label = ttk.Label(self, text=f"Elevator {self._elevator.id}", 
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=5)
        
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
        
        # Title for waiting passengers
        title_frame = ttk.Frame(shaft_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=2)
        
        ttk.Label(title_frame, text="Floor", font=("Arial", 8, "bold")).grid(row=0, column=0, padx=2)
        ttk.Label(title_frame, text="Elevator", font=("Arial", 8, "bold")).grid(row=0, column=1, padx=2)
        ttk.Label(title_frame, text="Waiting", font=("Arial", 8, "bold")).grid(row=0, column=2, padx=2)
        
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
            
            # Waiting passenger count indicator (at the "doors")
            waiting_frame = ttk.Frame(floor_frame)
            waiting_frame.grid(row=0, column=2, padx=2)
            
            waiting_label = ttk.Label(waiting_frame, text="", width=4, 
                                    font=("Arial", 8), foreground="darkblue")
            waiting_label.grid(row=0, column=0)
            
            self._waiting_passenger_labels[floor] = waiting_label
        
        # Passenger count display
        passenger_frame = ttk.Frame(shaft_frame)
        passenger_frame.grid(row=self._num_floors + 1, column=0, sticky="ew", pady=5)
        
        ttk.Label(passenger_frame, text="Passengers:").grid(row=0, column=0, padx=2)
        self._passenger_count_label = ttk.Label(passenger_frame, text="0", 
                                              font=("Arial", 10, "bold"))
        self._passenger_count_label.grid(row=0, column=1, padx=2)
        
        # Add a visual passenger indicator
        self._passenger_indicator = tk.Label(passenger_frame, text="", width=6, height=1,
                                           bg="white", relief="solid", borderwidth=1)
        self._passenger_indicator.grid(row=1, column=0, columnspan=2, pady=2)
        
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
        
        self._passengers_label = ttk.Label(status_frame, text="Passengers: 0/8")
        self._passengers_label.grid(row=2, column=0, sticky="w", pady=2)
        
        self._requests_label = ttk.Label(status_frame, text="Requests: None")
        self._requests_label.grid(row=3, column=0, sticky="w", pady=2)
        
        # Passenger list
        self._passenger_list_label = ttk.Label(status_frame, text="Passengers:")
        self._passenger_list_label.grid(row=4, column=0, sticky="w", pady=2)
        
        self._passenger_list = tk.Text(status_frame, height=4, width=30, 
                                     font=("Courier", 8), state="disabled")
        self._passenger_list.grid(row=5, column=0, sticky="ew", pady=2)
        
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
            
            # Add passenger count to the text if there are passengers
            passenger_count = self._elevator.passenger_count
            if passenger_count > 0:
                text += f"\n{passenger_count} P"
                # Add a border to highlight when carrying passengers
                indicator.config(relief="solid", borderwidth=2)
            else:
                indicator.config(relief="solid", borderwidth=1)
            
            indicator.config(bg=bg_color, text=text, fg="white")
    
    def _update_status_labels(self) -> None:
        """Update status information labels."""
        # State
        state_text = self._elevator.state.value.replace('_', ' ').title()
        self._state_label.config(text=f"State: {state_text}")
        
        # Direction
        direction_text = self._elevator.direction.name.title()
        self._direction_label.config(text=f"Direction: {direction_text}")
        
        # Passengers
        passenger_text = f"Passengers: {self._elevator.passenger_count}/{self._elevator.capacity}"
        self._passengers_label.config(text=passenger_text)
        
        # Requests
        requests = sorted(list(self._elevator.floor_requests))
        if requests:
            requests_text = f"Requests: {', '.join(map(str, requests))}"
        else:
            requests_text = "Requests: None"
        self._requests_label.config(text=requests_text)
        
        # Update passenger list
        self._update_passenger_list()
        
        # Update passenger count in shaft
        passenger_count = self._elevator.passenger_count
        self._passenger_count_label.config(text=str(passenger_count))
        
        # Update visual passenger indicator
        if passenger_count > 0:
            self._passenger_indicator.config(text=f"{passenger_count}", bg="lightgreen", fg="black")
        else:
            self._passenger_indicator.config(text="Empty", bg="lightgray", fg="black")
        
        # Update waiting passenger counts on each floor
        self._update_waiting_passenger_counts()
        
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
    
    def _update_passenger_list(self) -> None:
        """Update the passenger list display."""
        self._passenger_list.config(state="normal")
        self._passenger_list.delete(1.0, tk.END)
        
        if not self._passengers_info:
            self._passenger_list.insert(tk.END, "No passengers")
        else:
            for passenger_id, destination in self._passengers_info.items():
                self._passenger_list.insert(tk.END, f"{passenger_id} → {destination}\n")
        
        self._passenger_list.config(state="disabled")
    
    def _update_waiting_passenger_counts(self) -> None:
        """Update the waiting passenger count displays for each floor."""
        if not self._building:
            return
            
        for floor_num in range(1, self._num_floors + 1):
            waiting_label = self._waiting_passenger_labels.get(floor_num)
            if waiting_label:
                floor = self._building.get_floor(floor_num)
                if floor:
                    # Get waiting passenger counts for both directions
                    waiting_up = len(floor.waiting_passengers_up)
                    waiting_down = len(floor.waiting_passengers_down)
                    total_waiting = waiting_up + waiting_down
                    
                    if total_waiting > 0:
                        # Show total count with color coding
                        waiting_label.config(
                            text=f"{total_waiting}",
                            foreground="red" if total_waiting > 5 else "darkblue",
                            font=("Arial", 8, "bold")
                        )
                    else:
                        # No waiting passengers
                        waiting_label.config(text="", foreground="darkblue")
                else:
                    waiting_label.config(text="", foreground="darkblue")
    
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