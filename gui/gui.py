import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, List
import threading
import os

from config_manager import ConfigManager
from simulation import ElevatorSimulation, SimulationState
from logger import SimulationLogger

class ElevatorVisualization:
    def __init__(self, parent, max_floors: int = 20, max_elevators: int = 6):
        self.parent = parent
        self.max_floors = max_floors
        self.max_elevators = max_elevators
        
        # Create visualization frame
        self.frame = ttk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, width=600, height=500, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Drawing parameters
        self.elevator_width = 60
        self.elevator_spacing = 80
        self.floor_height = 20
        self.margin = 50
        
        # Colors
        self.colors = {
            'idle': '#90EE90',
            'moving_up': '#87CEEB',
            'moving_down': '#FFA07A',
            'loading': '#FFD700',
            'unloading': '#DDA0DD',
            'maintenance': '#FF6B6B'
        }
    
    def update_visualization(self, elevator_states: List[Dict]):
        """Update the elevator visualization"""
        self.canvas.delete("all")
        
        if not elevator_states:
            return
        
        # Calculate dimensions
        num_elevators = min(len(elevator_states), self.max_elevators)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Draw floor lines
        floor_spacing = (canvas_height - 2 * self.margin) / self.max_floors
        
        for floor in range(self.max_floors + 1):
            y = canvas_height - self.margin - floor * floor_spacing
            self.canvas.create_line(self.margin, y, canvas_width - self.margin, y, fill='gray', width=1)
            
            # Floor labels
            if floor % 5 == 0 or floor == 1:
                floor_num = floor - 2 if floor >= 2 else floor - 2  # Adjust for basement floors
                self.canvas.create_text(self.margin - 20, y, text=str(floor_num), anchor='e')
        
        # Draw elevators
        elevator_spacing = (canvas_width - 2 * self.margin) / max(1, num_elevators - 1) if num_elevators > 1 else 0
        
        for i, state in enumerate(elevator_states[:self.max_elevators]):
            x = self.margin + i * elevator_spacing
            floor_pos = max(0, min(self.max_floors, state['floor'] + 2))  # Adjust for basement
            y = canvas_height - self.margin - floor_pos * floor_spacing
            
            # Elevator rectangle
            color = self.colors.get(state['state'], '#CCCCCC')
            self.canvas.create_rectangle(
                x - self.elevator_width//2, y - 15,
                x + self.elevator_width//2, y + 15,
                fill=color, outline='black', width=2
            )
            
            # Elevator ID and info
            self.canvas.create_text(x, y - 5, text=f"E{state['id']}", font=('Arial', 8, 'bold'))
            self.canvas.create_text(x, y + 5, text=f"{state['passenger_count']}/{state['capacity']}", font=('Arial', 7))
            
            # Direction arrow
            if state['direction'] == 1:  # UP
                self.canvas.create_polygon(x, y-25, x-5, y-20, x+5, y-20, fill='green', outline='darkgreen')
            elif state['direction'] == -1:  # DOWN
                self.canvas.create_polygon(x, y+25, x-5, y+20, x+5, y+20, fill='red', outline='darkred')
            
            # Maintenance indicator
            if state['maintenance']:
                self.canvas.create_text(x, y+35, text="MAINT", fill='red', font=('Arial', 8, 'bold'))

class StatisticsPanel:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        
        # Create statistics display
        self.stats_vars = {
            'current_time': tk.StringVar(value="0.0"),
            'simulation_progress': tk.StringVar(value="0%"),
            'passengers_generated': tk.StringVar(value="0"),
            'passengers_completed': tk.StringVar(value="0"),
            'pending_requests': tk.StringVar(value="0"),
            'avg_wait_time': tk.StringVar(value="0.0"),
            'total_energy': tk.StringVar(value="0.0"),
            'active_elevators': tk.StringVar(value="0")
        }
        
        row = 0
        for key, var in self.stats_vars.items():
            label_text = key.replace('_', ' ').title()
            ttk.Label(self.frame, text=f"{label_text}:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(self.frame, textvariable=var).grid(row=row, column=1, sticky='w', padx=5, pady=2)
            row += 1
    
    def update_statistics(self, stats: Dict):
        """Update statistics display"""
        for key, var in self.stats_vars.items():
            if key in stats:
                value = stats[key]
                if isinstance(value, float):
                    if key == 'simulation_progress':
                        var.set(f"{value*100:.1f}%")
                    else:
                        var.set(f"{value:.2f}")
                else:
                    var.set(str(value))

class ElevatorSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Elevator System Simulation")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.simulation = ElevatorSimulation(self.config_manager)
        
        # Create GUI
        self._create_menu()
        self._create_main_layout()
        self._create_control_panel()
        self._create_configuration_panel()
        self._create_visualization()
        self._create_statistics_panel()
        self._create_charts()
        
        # Initialize sample configs
        self.config_manager.create_sample_configs()
        
        # Update timer
        self._start_update_timer()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Building Config...", command=self.load_building_config)
        file_menu.add_command(label="Load Elevator Config...", command=self.load_elevator_config)
        file_menu.add_command(label="Load Simulation Config...", command=self.load_simulation_config)
        file_menu.add_separator()
        file_menu.add_command(label="Save Logs...", command=self.save_logs)
        file_menu.add_command(label="Export Analysis...", command=self.export_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Initialize", command=self.initialize_simulation)
        sim_menu.add_command(label="Start", command=self.start_simulation)
        sim_menu.add_command(label="Pause", command=self.pause_simulation)
        sim_menu.add_command(label="Stop", command=self.stop_simulation)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset Charts", command=self.reset_charts)
    
    def _create_main_layout(self):
        """Create main layout"""
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls and config
        self.left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_panel, weight=1)
        
        # Right panel for visualization and charts
        self.right_panel = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_panel, weight=2)
    
    def _create_control_panel(self):
        """Create simulation control panel"""
        control_frame = ttk.LabelFrame(self.left_panel, text="Simulation Control", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Simulation state
        self.state_var = tk.StringVar(value="Stopped")
        ttk.Label(control_frame, text="State:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(control_frame, textvariable=self.state_var, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.init_btn = ttk.Button(button_frame, text="Initialize", command=self.initialize_simulation)
        self.init_btn.grid(row=0, column=0, padx=2)
        
        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_simulation, state='disabled')
        self.start_btn.grid(row=0, column=1, padx=2)
        
        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause_simulation, state='disabled')
        self.pause_btn.grid(row=0, column=2, padx=2)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.grid(row=0, column=3, padx=2)
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, command=self.update_speed)
        speed_scale.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        
        # Passenger pattern selection
        ttk.Label(control_frame, text="Pattern:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.pattern_var = tk.StringVar(value="normal")
        pattern_combo = ttk.Combobox(control_frame, textvariable=self.pattern_var,
                                   values=["normal", "morning_rush", "evening_rush", "lunch_time"],
                                   state="readonly")
        pattern_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        pattern_combo.bind('<<ComboboxSelected>>', self.update_pattern)
    
    def _create_configuration_panel(self):
        """Create configuration panel"""
        config_frame = ttk.LabelFrame(self.left_panel, text="Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configuration status
        self.config_status = {
            'building': tk.StringVar(value="Not Loaded"),
            'elevators': tk.StringVar(value="Not Loaded"),
            'simulation': tk.StringVar(value="Not Loaded")
        }
        
        ttk.Label(config_frame, text="Building:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(config_frame, textvariable=self.config_status['building']).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(config_frame, text="Elevators:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(config_frame, textvariable=self.config_status['elevators']).grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(config_frame, text="Simulation:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(config_frame, textvariable=self.config_status['simulation']).grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Load buttons
        ttk.Button(config_frame, text="Load Building", command=self.load_building_config).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(config_frame, text="Load Elevators", command=self.load_elevator_config).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(config_frame, text="Load Simulation", command=self.load_simulation_config).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Emergency controls
        emergency_frame = ttk.LabelFrame(config_frame, text="Emergency Controls", padding=5)
        emergency_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(emergency_frame, text="Elevator ID:").grid(row=0, column=0, padx=2)
        self.emergency_elevator_var = tk.StringVar(value="1")
        emergency_entry = ttk.Entry(emergency_frame, textvariable=self.emergency_elevator_var, width=5)
        emergency_entry.grid(row=0, column=1, padx=2)
        
        ttk.Button(emergency_frame, text="Emergency Stop", command=self.emergency_stop).grid(row=0, column=2, padx=2)
        ttk.Button(emergency_frame, text="Release", command=self.release_emergency).grid(row=0, column=3, padx=2)
    
    def _create_visualization(self):
        """Create elevator visualization"""
        viz_frame = ttk.LabelFrame(self.right_panel, text="Elevator Status", padding=5)
        self.right_panel.add(viz_frame, weight=1)
        
        self.visualization = ElevatorVisualization(viz_frame)
        self.visualization.frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_statistics_panel(self):
        """Create statistics panel"""
        self.statistics_panel = StatisticsPanel(self.right_panel)
        self.right_panel.add(self.statistics_panel.frame, weight=0)
    
    def _create_charts(self):
        """Create performance charts"""
        chart_frame = ttk.LabelFrame(self.right_panel, text="Performance Charts", padding=5)
        self.right_panel.add(chart_frame, weight=1)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        
        # Create subplots
        self.ax1 = self.fig.add_subplot(221)  # Passenger count over time
        self.ax2 = self.fig.add_subplot(222)  # Wait times
        self.ax3 = self.fig.add_subplot(223)  # Energy consumption
        self.ax4 = self.fig.add_subplot(224)  # Elevator utilization
        
        self.fig.tight_layout()
        
        # Create canvas
        self.chart_canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize data storage for charts
        self.chart_data = {
            'times': [],
            'passenger_counts': [],
            'wait_times': [],
            'energy_consumption': [],
            'elevator_utilization': []
        }
    
    def _start_update_timer(self):
        """Start the GUI update timer"""
        self.update_gui()
        self.root.after(100, self._start_update_timer)  # Update every 100ms
    
    def update_gui(self):
        """Update GUI elements"""
        # Update simulation state
        if hasattr(self.simulation, 'state'):
            self.state_var.set(self.simulation.state.value.title())
            
            # Update button states
            if self.simulation.state == SimulationState.STOPPED:
                self.start_btn.config(state='normal' if self.simulation.controller else 'disabled')
                self.pause_btn.config(state='disabled')
                self.stop_btn.config(state='disabled')
            elif self.simulation.state == SimulationState.RUNNING:
                self.start_btn.config(state='disabled')
                self.pause_btn.config(state='normal')
                self.stop_btn.config(state='normal')
            elif self.simulation.state == SimulationState.PAUSED:
                self.start_btn.config(text='Resume', state='normal')
                self.pause_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
            elif self.simulation.state == SimulationState.COMPLETED:
                self.start_btn.config(text='Start', state='disabled')
                self.pause_btn.config(state='disabled')
                self.stop_btn.config(state='disabled')
        
        # Update visualization and statistics if simulation is running
        if self.simulation.state in [SimulationState.RUNNING, SimulationState.PAUSED, SimulationState.COMPLETED]:
            elevator_states = self.simulation.get_elevator_states()
            self.visualization.update_visualization(elevator_states)
            
            stats = self.simulation.get_current_statistics()
            self.statistics_panel.update_statistics(stats)
            
            # Update charts
            self._update_charts(stats)
    
    def _update_charts(self, stats: Dict):
        """Update performance charts"""
        if 'current_time' not in stats:
            return
        
        # Add data points
        self.chart_data['times'].append(stats['current_time'])
        self.chart_data['passenger_counts'].append(stats.get('passengers_generated', 0))
        self.chart_data['wait_times'].append(stats.get('avg_wait_time', 0))
        self.chart_data['energy_consumption'].append(stats.get('total_energy', 0))
        
        # Calculate elevator utilization
        elevator_states = self.simulation.get_elevator_states()
        active_elevators = sum(1 for e in elevator_states if e['passenger_count'] > 0)
        total_elevators = len(elevator_states)
        utilization = active_elevators / max(1, total_elevators) * 100
        self.chart_data['elevator_utilization'].append(utilization)
        
        # Keep only recent data (last 1000 points)
        max_points = 1000
        for key in self.chart_data:
            if len(self.chart_data[key]) > max_points:
                self.chart_data[key] = self.chart_data[key][-max_points:]
        
        # Update plots
        self.ax1.clear()
        self.ax1.plot(self.chart_data['times'], self.chart_data['passenger_counts'])
        self.ax1.set_title('Passengers Generated')
        self.ax1.set_ylabel('Count')
        
        self.ax2.clear()
        self.ax2.plot(self.chart_data['times'], self.chart_data['wait_times'])
        self.ax2.set_title('Average Wait Time')
        self.ax2.set_ylabel('Seconds')
        
        self.ax3.clear()
        self.ax3.plot(self.chart_data['times'], self.chart_data['energy_consumption'])
        self.ax3.set_title('Energy Consumption')
        self.ax3.set_ylabel('Units')
        self.ax3.set_xlabel('Time (s)')
        
        self.ax4.clear()
        self.ax4.plot(self.chart_data['times'], self.chart_data['elevator_utilization'])
        self.ax4.set_title('Elevator Utilization')
        self.ax4.set_ylabel('Percentage')
        self.ax4.set_xlabel('Time (s)')
        
        self.fig.tight_layout()
        self.chart_canvas.draw()
    
    # Event handlers
    def load_building_config(self):
        """Load building configuration"""
        filename = filedialog.askopenfilename(
            title="Load Building Configuration",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.load_building_config(filename)
                self.config_status['building'].set("Loaded")
                messagebox.showinfo("Success", "Building configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load building config: {e}")
    
    def load_elevator_config(self):
        """Load elevator configuration"""
        filename = filedialog.askopenfilename(
            title="Load Elevator Configuration",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.load_elevator_configs(filename)
                self.config_status['elevators'].set("Loaded")
                messagebox.showinfo("Success", "Elevator configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load elevator config: {e}")
    
    def load_simulation_config(self):
        """Load simulation configuration"""
        filename = filedialog.askopenfilename(
            title="Load Simulation Configuration",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.load_simulation_config(filename)
                self.config_status['simulation'].set("Loaded")
                messagebox.showinfo("Success", "Simulation configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load simulation config: {e}")
    
    def initialize_simulation(self):
        """Initialize simulation"""
        if self.simulation.initialize():
            messagebox.showinfo("Success", "Simulation initialized successfully")
            self.start_btn.config(state='normal')
        else:
            messagebox.showerror("Error", "Failed to initialize simulation. Please check configurations.")
    
    def start_simulation(self):
        """Start simulation"""
        if self.simulation.state == SimulationState.PAUSED:
            self.simulation.resume()
            self.start_btn.config(text='Start')
        else:
            self.simulation.start()
    
    def pause_simulation(self):
        """Pause simulation"""
        self.simulation.pause()
    
    def stop_simulation(self):
        """Stop simulation"""
        self.simulation.stop()
        
        # Reset charts
        for key in self.chart_data:
            self.chart_data[key] = []
    
    def update_speed(self, value):
        """Update simulation speed"""
        speed = float(value)
        self.simulation.set_speed_multiplier(speed)
    
    def update_pattern(self, event=None):
        """Update passenger generation pattern"""
        pattern = self.pattern_var.get()
        self.simulation.set_passenger_pattern(pattern)
    
    def emergency_stop(self):
        """Trigger emergency stop"""
        try:
            elevator_id = int(self.emergency_elevator_var.get())
            self.simulation.trigger_emergency_stop(elevator_id)
            messagebox.showinfo("Emergency", f"Emergency stop triggered for elevator {elevator_id}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid elevator ID")
    
    def release_emergency(self):
        """Release emergency stop"""
        try:
            elevator_id = int(self.emergency_elevator_var.get())
            self.simulation.release_emergency_stop(elevator_id)
            messagebox.showinfo("Emergency", f"Emergency released for elevator {elevator_id}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid elevator ID")
    
    def save_logs(self):
        """Save simulation logs"""
        if self.simulation.logger:
            self.simulation.logger.save_to_csv()
            messagebox.showinfo("Success", f"Logs saved to logs directory")
        else:
            messagebox.showwarning("Warning", "No simulation data to save")
    
    def export_analysis(self):
        """Export analysis data"""
        if self.simulation.logger:
            filename = filedialog.asksaveasfilename(
                title="Export Analysis Data",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self.simulation.logger.export_analysis_data(filename)
                messagebox.showinfo("Success", "Analysis data exported successfully")
        else:
            messagebox.showwarning("Warning", "No simulation data to export")
    
    def reset_charts(self):
        """Reset performance charts"""
        for key in self.chart_data:
            self.chart_data[key] = []
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        self.chart_canvas.draw()

def main():
    root = tk.Tk()
    app = ElevatorSimulationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()