
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any

class ControlPanel(ttk.Frame):
    """
    Control panel providing simulation controls and hall call buttons.
    
    This class provides the user interface for controlling the simulation
    and making hall calls from different floors.
    """
    
    def __init__(self, parent, num_floors: int,
                 hall_call_callback: Optional[Callable[[int, str], None]] = None,
                 passenger_callback: Optional[Callable[[int, int], None]] = None,
                 simulation_callback: Optional[Callable[[str, Any], None]] = None):
        """
        Initialize the control panel.
        
        Args:
            parent: Parent Tkinter widget
            num_floors: Number of floors in the building
            hall_call_callback: Callback for hall call button presses
            passenger_callback: Callback for adding passengers
            simulation_callback: Callback for simulation control
        """
        super().__init__(parent)
        
        self._num_floors = num_floors
        self._hall_call_callback = hall_call_callback
        self._passenger_callback = passenger_callback
        self._simulation_callback = simulation_callback
        
        # Control variables
        self._speed_var = tk.DoubleVar(value=1.0)
        self._passenger_gen_var = tk.BooleanVar(value=False)
        
        # Passenger form variables
        self._origin_var = tk.IntVar(value=1)
        self._destination_var = tk.IntVar(value=2)
        
        # Metrics display
        self._metrics_labels = {}
        
        self._setup_panel()
    
    def _setup_panel(self) -> None:
        """Set up the control panel layout."""
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Hall calls tab
        hall_frame = ttk.Frame(notebook)
        notebook.add(hall_frame, text="Hall Calls")
        self._setup_hall_calls_tab(hall_frame)
        
        # Passengers tab
        passenger_frame = ttk.Frame(notebook)
        notebook.add(passenger_frame, text="Passengers")

        self._setup_passengers_tab(passenger_frame)
        # Simulation control tab
        sim_frame = ttk.Frame(notebook)
        notebook.add(sim_frame, text="Simulation")
        self._setup_simulation_tab(sim_frame)
        

        
        # Metrics tab
        metrics_frame = ttk.Frame(notebook)
        notebook.add(metrics_frame, text="Metrics")
        self._setup_metrics_tab(metrics_frame)
    
    def _setup_hall_calls_tab(self, parent) -> None:
        """Set up the hall calls interface."""
        # Instructions
        instructions = ttk.Label(parent, text="Press hall call buttons to request elevators:",
                                font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Create hall call buttons for each floor
        for floor in range(self._num_floors, 0, -1):
            floor_frame = ttk.Frame(parent)
            floor_frame.pack(fill=tk.X, padx=10, pady=2)
            
            # Floor label
            floor_label = ttk.Label(floor_frame, text=f"Floor {floor}:", width=10)
            floor_label.pack(side=tk.LEFT, padx=5)
            
            # Up button (not for top floor)
            if floor < self._num_floors:
                up_btn = tk.Button(floor_frame, text="↑ UP", width=8,
                                 command=lambda f=floor: self._call_hall_button(f, "up"))
                up_btn.pack(side=tk.LEFT, padx=2)
            
            # Down button (not for ground floor)
            if floor > 1:
                down_btn = tk.Button(floor_frame, text="↓ DOWN", width=8,
                                   command=lambda f=floor: self._call_hall_button(f, "down"))
                down_btn.pack(side=tk.LEFT, padx=2)
    
    def _setup_passengers_tab(self, parent) -> None:
        """Set up the passenger management interface."""
        # Manual passenger addition
        manual_frame = ttk.LabelFrame(parent, text="Add Passenger", padding="10")
        manual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Origin floor
        ttk.Label(manual_frame, text="Origin Floor:").grid(row=0, column=0, sticky="w", pady=2)
        origin_combo = ttk.Combobox(manual_frame, textvariable=self._origin_var,
                                   values=list(range(1, self._num_floors + 1)),
                                   width=10, state="readonly")
        origin_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Destination floor
        ttk.Label(manual_frame, text="Destination Floor:").grid(row=1, column=0, sticky="w", pady=2)
        dest_combo = ttk.Combobox(manual_frame, textvariable=self._destination_var,
                                 values=list(range(1, self._num_floors + 1)),
                                 width=10, state="readonly")
        dest_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Add button
        add_btn = ttk.Button(manual_frame, text="Add Passenger",
                           command=self._add_passenger)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Quick passenger buttons
        quick_frame = ttk.LabelFrame(parent, text="Quick Add", padding="10")
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(quick_frame, text="Ground → Top",
                  command=lambda: self._quick_passenger(1, self._num_floors)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Top → Ground",
                  command=lambda: self._quick_passenger(self._num_floors, 1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Random",
                  command=self._add_random_passenger).pack(side=tk.LEFT, padx=5)
        
        # Passenger generation control
        gen_frame = ttk.LabelFrame(parent, text="Automatic Generation", padding="10")
        gen_frame.pack(fill=tk.X, padx=10, pady=10)
        
        gen_check = ttk.Checkbutton(gen_frame, text="Enable automatic passenger generation",
                                   variable=self._passenger_gen_var,
                                   command=self._toggle_passenger_generation)
        gen_check.pack(pady=5)
    
    def _setup_simulation_tab(self, parent) -> None:
        """Set up simulation control interface."""
        # Simulation speed control
        speed_frame = ttk.LabelFrame(parent, text="Simulation Speed", padding="10")
        speed_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(speed_frame, text="Speed Multiplier:").grid(row=0, column=0, sticky="w")
        
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL,
                               variable=self._speed_var, command=self._on_speed_change)
        speed_scale.grid(row=0, column=1, sticky="ew", padx=5)
        
        self._speed_label = ttk.Label(speed_frame, text="1.0x")
        self._speed_label.grid(row=0, column=2, padx=5)
        
        speed_frame.columnconfigure(1, weight=1)
        
        # Quick speed buttons
        speed_buttons_frame = ttk.Frame(speed_frame)
        speed_buttons_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        for speed in [0.5, 1.0, 2.0, 5.0]:
            ttk.Button(speed_buttons_frame, text=f"{speed}x",
                      command=lambda s=speed: self._set_speed(s)).pack(side=tk.LEFT, padx=2)
        
        # Simulation info
        info_frame = ttk.LabelFrame(parent, text="Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)
        
        info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")
        
        self._info_text = info_text
        
        # Add initial information
        self._update_info_text()
    
    def _setup_metrics_tab(self, parent) -> None:
        """Set up the metrics display interface."""
        # Create scrollable frame for metrics
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._metrics_frame = scrollable_frame
        
        # Initialize metrics display
        self._create_metrics_labels()
    

    
    def _create_metrics_labels(self) -> None:
        """Create labels for displaying metrics."""
        metrics_config = [
            ("System Status", [
                ("simulation_running", "Simulation Running"),
                ("simulation_paused", "Simulation Paused"),
                ("elapsed_time", "Elapsed Time")
            ]),
            ("Building Metrics", [
                ("total_elevators", "Total Elevators"),
                ("active_elevators", "Active Elevators"),
                ("idle_elevators", "Idle Elevators")
            ]),

            ("Performance", [
                ("energy_usage", "Energy Usage"),
                ("efficiency_score", "Efficiency Score")
            ])
        ]
        
        row = 0
        for section_name, metrics in metrics_config:
            # Section header
            section_label = ttk.Label(self._metrics_frame, text=section_name,
                                    font=("Arial", 12, "bold"))
            section_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
            row += 1
            
            # Metrics in section
            for metric_key, metric_display in metrics:
                name_label = ttk.Label(self._metrics_frame, text=f"{metric_display}:")
                name_label.grid(row=row, column=0, sticky="w", padx=20, pady=2)
                
                value_label = ttk.Label(self._metrics_frame, text="--")
                value_label.grid(row=row, column=1, sticky="w", padx=10, pady=2)
                
                self._metrics_labels[metric_key] = value_label
                row += 1
    
    def _call_hall_button(self, floor: int, direction: str) -> None:
        """Handle hall call button press."""
        if self._hall_call_callback:
            self._hall_call_callback(floor, direction)
    
    def _add_passenger(self) -> None:
        """Add a passenger using the form values."""
        origin = self._origin_var.get()
        destination = self._destination_var.get()
        
        if origin == destination:
            tk.messagebox.showwarning("Invalid Input", "Origin and destination must be different")
            return
        
        if self._passenger_callback:
            self._passenger_callback(origin, destination)
    
    def _quick_passenger(self, origin: int, destination: int) -> None:
        """Add a passenger with specified origin and destination."""
        if self._passenger_callback:
            self._passenger_callback(origin, destination)
    
    def _add_random_passenger(self) -> None:
        """Add a passenger with random origin and destination."""
        import random
        floors = list(range(1, self._num_floors + 1))
        origin = random.choice(floors)
        destination = random.choice([f for f in floors if f != origin])
        self._quick_passenger(origin, destination)
    
    def _toggle_passenger_generation(self) -> None:
        """Toggle automatic passenger generation."""
        if self._simulation_callback:
            self._simulation_callback("passenger_generation", self._passenger_gen_var.get())
    
    def _on_speed_change(self, value: str) -> None:
        """Handle speed scale change."""
        speed = float(value)
        self._speed_label.config(text=f"{speed:.1f}x")
        
        if self._simulation_callback:
            self._simulation_callback("speed", speed)
    
    def _set_speed(self, speed: float) -> None:
        """Set specific simulation speed."""
        self._speed_var.set(speed)
        self._on_speed_change(str(speed))
    
    def _update_info_text(self) -> None:
        """Update the information text display."""
        info = f"""Elevator Simulation Control Panel

Building Configuration:
- Floors: {self._num_floors}
- Elevators: Various configurations

Controls:
- Hall Calls: Request elevators from floors
- Passengers: Add passengers manually or automatically
- Simulation: Control simulation speed and parameters
- Metrics: View real-time performance data

Tips:
- Use hall call buttons to simulate people waiting
- Add passengers to see elevator routing
- Adjust simulation speed for faster testing
- Monitor metrics to evaluate performance
"""
        
        self._info_text.config(state=tk.NORMAL)
        self._info_text.delete("1.0", tk.END)
        self._info_text.insert("1.0", info)
        self._info_text.config(state=tk.DISABLED)
    
    def update_metrics(self, simulation_status: Dict[str, Any]) -> None:
        """
        Update the metrics display with current simulation data.
        
        Args:
            simulation_status: Dictionary containing simulation status
        """
        # Update system status
        self._update_metric("simulation_running", 
                           "Yes" if simulation_status.get("is_running", False) else "No")
        self._update_metric("simulation_paused", 
                           "Yes" if simulation_status.get("is_paused", False) else "No")
        self._update_metric("elapsed_time", 
                           f"{simulation_status.get('elapsed_time', 0):.1f}s")
        
        # Update building metrics
        controller_metrics = simulation_status.get("controller_metrics", {})
        self._update_metric("total_elevators", controller_metrics.get("total_elevators", 0))
        self._update_metric("active_elevators", controller_metrics.get("active_elevators", 0))
        self._update_metric("idle_elevators", controller_metrics.get("idle_elevators", 0))
        

        
        # Update performance metrics (simplified)
        self._update_metric("energy_usage", controller_metrics.get("estimated_energy", 0))
        
        # Calculate simple efficiency score
        total_elevators = controller_metrics.get("total_elevators", 1)
        active_elevators = controller_metrics.get("active_elevators", 0)
        efficiency = (active_elevators / total_elevators) * 100 if total_elevators > 0 else 0
        self._update_metric("efficiency_score", f"{efficiency:.1f}%")
        

    

    
    def _update_metric(self, metric_key: str, value) -> None:
        """Update a specific metric display."""
        if metric_key in self._metrics_labels:
            self._metrics_labels[metric_key].config(text=str(value))