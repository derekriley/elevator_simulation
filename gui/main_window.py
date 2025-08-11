"""
Main GUI window for the elevator simulation application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from pathlib import Path
from config.building_config import BuildingConfig
from config.simulation_config import SimulationConfig
from models.building import Building
from simulation.simulator import ElevatorSimulator
from .elevator_panel import ElevatorPanel
from .control_panel import ControlPanel

class MainWindow:
    """
    Main application window providing the primary user interface.
    
    This class follows the Model-View-Controller pattern and serves
    as the main view coordinating all GUI components.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: Root Tkinter window
        """
        self.root = root
        self.root.title("Elevator Simulation Tool")
        self.root.geometry("1200x800")
        
        # Application state
        self.building_config: BuildingConfig = None
        self.simulation_config: SimulationConfig = None
        self.building: Building = None
        self.simulator: ElevatorSimulator = None
        
        # GUI components
        self.elevator_panels = {}
        self.control_panel = None
        
        self._setup_menu()
        self._setup_main_layout()
        self._setup_status_bar()
        
        # Start with sample configuration
        self._load_sample_configuration()
        
        logging.info("Main window initialized")
    
    def _setup_menu(self) -> None:
        """Set up the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Building Config", command=self._load_building_config)
        file_menu.add_command(label="Load Simulation Config", command=self._load_simulation_config)
        file_menu.add_separator()
        file_menu.add_command(label="Create Sample Configs", command=self._create_sample_configs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self._start_simulation)
        sim_menu.add_command(label="Pause", command=self._pause_simulation)
        sim_menu.add_command(label="Resume", command=self._resume_simulation)
        sim_menu.add_command(label="Stop", command=self._stop_simulation)
        sim_menu.add_separator()
        sim_menu.add_command(label="Add Random Passenger", command=self._add_random_passenger)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Logs", command=self._show_logs)
        view_menu.add_command(label="Performance Metrics", command=self._show_metrics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_main_layout(self) -> None:
        """Set up the main window layout."""
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for elevators
        self.elevator_frame = ttk.LabelFrame(self.main_paned, text="Elevators", padding="5")
        self.main_paned.add(self.elevator_frame, weight=3)
        
        # Right panel for controls
        self.control_frame = ttk.LabelFrame(self.main_paned, text="Controls", padding="5")
        self.main_paned.add(self.control_frame, weight=1)
        
        # Create scrollable elevator area
        self.elevator_canvas = tk.Canvas(self.elevator_frame)
        self.elevator_scrollbar = ttk.Scrollbar(self.elevator_frame, orient="vertical", 
                                               command=self.elevator_canvas.yview)
        self.elevator_scrollable_frame = ttk.Frame(self.elevator_canvas)
        
        self.elevator_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.elevator_canvas.configure(scrollregion=self.elevator_canvas.bbox("all"))
        )
        
        self.elevator_canvas.create_window((0, 0), window=self.elevator_scrollable_frame, anchor="nw")
        self.elevator_canvas.configure(yscrollcommand=self.elevator_scrollbar.set)
        
        self.elevator_canvas.pack(side="left", fill="both", expand=True)
        self.elevator_scrollbar.pack(side="right", fill="y")
    
    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.simulation_status_label = ttk.Label(self.status_frame, text="Simulation: Stopped")
        self.simulation_status_label.pack(side=tk.RIGHT)
    
    def _load_building_config(self) -> None:
        """Load building configuration from file."""
        file_path = filedialog.askopenfilename(
            title="Select Building Configuration",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.building_config = BuildingConfig(file_path)
                errors = self.building_config.validate_configuration()
                
                if errors:
                    error_msg = "\n".join(errors)
                    messagebox.showerror("Configuration Error", 
                                       f"Configuration validation failed:\n\n{error_msg}")
                    return
                
                self._create_building_from_config()
                self.status_label.config(text=f"Loaded: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration:\n{e}")
                logging.error(f"Error loading building config: {e}")
    
    def _load_simulation_config(self) -> None:
        """Load simulation configuration from file."""
        file_path = filedialog.askopenfilename(
            title="Select Simulation Configuration",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.simulation_config = SimulationConfig(file_path)
                self.status_label.config(text=f"Sim config loaded: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load simulation configuration:\n{e}")
                logging.error(f"Error loading simulation config: {e}")
    
    def _create_sample_configs(self) -> None:
        """Create sample configuration files."""
        try:
            # Create data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Create sample building config
            building_config_path = data_dir / "sample_building.csv"
            BuildingConfig.create_sample_config(str(building_config_path))
            
            # Create sample simulation config
            sim_config_path = data_dir / "sample_simulation.csv"
            SimulationConfig.create_sample_config(str(sim_config_path))
            
            messagebox.showinfo("Success", 
                              f"Sample configurations created:\n"
                              f"- {building_config_path}\n"
                              f"- {sim_config_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sample configs:\n{e}")
    
    def _load_sample_configuration(self) -> None:
        """Load sample configuration for demonstration."""
        try:
            # Create sample configs if they don't exist
            data_dir = Path("data")
            building_config_path = data_dir / "sample_building.csv"
            
            if not building_config_path.exists():
                data_dir.mkdir(exist_ok=True)
                BuildingConfig.create_sample_config(str(building_config_path))
            
            # Load the sample configuration
            self.building_config = BuildingConfig(str(building_config_path))
            self._create_building_from_config()
            
            self.status_label.config(text="Sample configuration loaded")
            
        except Exception as e:
            logging.error(f"Error loading sample configuration: {e}")
            self.status_label.config(text="Error loading sample configuration")
    
    def _create_building_from_config(self) -> None:
        """Create building and GUI components from loaded configuration."""
        if not self.building_config:
            return
        
        # Create building model
        building_data = self.building_config.building_data
        elevators_data = self.building_config.elevators_data
        
        self.building = Building(
            building_data['id'],
            building_data['num_floors'],
            elevators_data
        )
        
        # Create simulator
        self.simulator = ElevatorSimulator(self.building, self.simulation_config)
        self.simulator.controller.add_update_callback(self._update_gui)
        
        # Clear existing GUI components
        self._clear_elevator_panels()
        
        # Create elevator panels
        self._create_elevator_panels()
        
        # Create control panel
        self._create_control_panel()
        
        logging.info("Building and GUI created from configuration")
    
    def _create_elevator_panels(self) -> None:
        """Create elevator visualization panels."""
        elevators = self.building.elevators
        
        # Calculate layout
        elevators_per_row = min(4, len(elevators))
        
        row = 0
        col = 0
        
        for elevator_id, elevator in elevators.items():
            panel = ElevatorPanel(
                self.elevator_scrollable_frame,
                elevator,
                self.building.num_floors,
                command_callback=self._elevator_button_pressed,
                building=self.building
            )
            
            panel.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
            self.elevator_panels[elevator_id] = panel
            
            col += 1
            if col >= elevators_per_row:
                col = 0
                row += 1
    
    def _create_control_panel(self) -> None:
        """Create the simulation control panel."""
        if self.control_panel:
            self.control_panel.destroy()
        
        self.control_panel = ControlPanel(
            self.control_frame,
            self.building.num_floors,
            hall_call_callback=self._hall_button_pressed,
            passenger_callback=self._add_passenger,
            simulation_callback=self._handle_simulation_control
        )
        
        self.control_panel.pack(fill=tk.BOTH, expand=True)
    
    def _clear_elevator_panels(self) -> None:
        """Clear all existing elevator panels."""
        for panel in self.elevator_panels.values():
            panel.destroy()
        self.elevator_panels.clear()
    
    def _elevator_button_pressed(self, elevator_id: str, floor: int) -> None:
        """Handle elevator button press."""
        if self.simulator:
            success = self.simulator.press_elevator_button(elevator_id, floor)
            if success:
                self.status_label.config(text=f"Elevator {elevator_id} button {floor} pressed")
            else:
                self.status_label.config(text=f"Failed to press elevator button")
    
    def _hall_button_pressed(self, floor: int, direction: str) -> None:
        """Handle hall call button press."""
        if self.simulator:
            success = self.simulator.press_hall_button(floor, direction)
            if success:
                self.status_label.config(text=f"Hall button floor {floor} {direction} pressed")
            else:
                self.status_label.config(text=f"Failed to press hall button")
    
    def _add_passenger(self, origin: int, destination: int) -> None:
        """Add a passenger to the simulation."""
        if self.simulator:
            passenger_id = self.simulator.add_manual_passenger(origin, destination)
            self.status_label.config(text=f"Added passenger {passenger_id}: {origin} -> {destination}")
    
    def _add_random_passenger(self) -> None:
        """Add a random passenger."""
        if self.building:
            import random
            floors = list(range(1, self.building.num_floors + 1))
            origin = random.choice(floors)
            destination = random.choice([f for f in floors if f != origin])
            self._add_passenger(origin, destination)
    
    def _handle_simulation_control(self, action: str, value=None) -> None:
        """Handle simulation control actions."""
        if action == "speed" and value is not None:
            if self.simulator:
                self.simulator.controller.set_simulation_speed(value)
        elif action == "passenger_generation":
            if self.simulator:
                self.simulator.set_passenger_generation(value)
    
    def _start_simulation(self) -> None:
        """Start the simulation."""
        if not self.simulator:
            messagebox.showwarning("Warning", "No building configuration loaded")
            return
        
        if self.simulator.controller.start_simulation():
            self.simulation_status_label.config(text="Simulation: Running")
            self.status_label.config(text="Simulation started")
        else:
            messagebox.showerror("Error", "Failed to start simulation")
    
    def _pause_simulation(self) -> None:
        """Pause the simulation."""
        if self.simulator:
            self.simulator.pause_simulation()
            self.simulation_status_label.config(text="Simulation: Paused")
            self.status_label.config(text="Simulation paused")
    
    def _resume_simulation(self) -> None:
        """Resume the simulation."""
        if self.simulator:
            self.simulator.resume_simulation()
            self.simulation_status_label.config(text="Simulation: Running")
            self.status_label.config(text="Simulation resumed")
    
    def _stop_simulation(self) -> None:
        """Stop the simulation."""
        if self.simulator:
            self.simulator.stop_simulation()
            self.simulation_status_label.config(text="Simulation: Stopped")
            self.status_label.config(text="Simulation stopped")
    
    def _update_gui(self) -> None:
        """Update GUI components with current simulation state."""
        if not self.simulator:
            return
        
        # Get simulation status for passenger information
        status = self.simulator.get_simulation_status()
        
        # Update elevator panels
        for elevator_id, panel in self.elevator_panels.items():
            elevator = self.building.get_elevator(elevator_id)
            if elevator:
                # Get passenger information for this elevator
                elevator_status = status.get('building_status', {}).get('elevators', {}).get(elevator_id, {})
                passengers_info = {}
                
                # Create passenger info mapping
                for passenger_id in elevator_status.get('passengers', []):
                    if passenger_id in self.simulator.passengers:
                        passenger = self.simulator.passengers[passenger_id]
                        passengers_info[passenger_id] = passenger.destination_floor
                
                panel.update_display(elevator, passengers_info)
        
        # Update control panel
        if self.control_panel:
            self.control_panel.update_metrics(status)
    
    def _show_logs(self) -> None:
        """Show simulation logs window."""
        log_window = tk.Toplevel(self.root)
        log_window.title("Simulation Logs")
        log_window.geometry("800x600")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(log_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_text = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load and display log file
        try:
            with open("elevator_simulation.log", "r") as f:
                log_content = f.read()
                log_text.insert("1.0", log_content)
        except FileNotFoundError:
            log_text.insert("1.0", "No log file found.")
        
        log_text.config(state="disabled")
    
    def _show_metrics(self) -> None:
        """Show performance metrics window."""
        if not self.simulator:
            messagebox.showwarning("Warning", "No active simulation")
            return
        
        metrics_window = tk.Toplevel(self.root)
        metrics_window.title("Performance Metrics")
        metrics_window.geometry("600x400")
        
        # Get current metrics
        status = self.simulator.get_simulation_status()
        
        # Create treeview for metrics display
        tree = ttk.Treeview(metrics_window, columns=("Value",), show="tree headings")
        tree.heading("#0", text="Metric")
        tree.heading("Value", text="Value")
        
        # Populate metrics
        self._populate_metrics_tree(tree, "", status)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _populate_metrics_tree(self, tree: ttk.Treeview, parent: str, data: dict) -> None:
        """Recursively populate metrics tree."""
        for key, value in data.items():
            if isinstance(value, dict):
                node = tree.insert(parent, "end", text=key, values=("",))
                self._populate_metrics_tree(tree, node, value)
            else:
                tree.insert(parent, "end", text=key, values=(str(value),))
    
    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """Elevator Simulation Tool

A comprehensive elevator control system simulator for testing and evaluation.

Features:
- Multiple elevator simulation
- Configurable building layouts
- Performance metrics
- Data logging and analysis
- Interactive GUI controls

Built with Python and Tkinter following SOLID principles."""
        
        messagebox.showinfo("About", about_text)