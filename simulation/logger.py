"""
Simulation logging and data collection system.
"""

import csv
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

def setup_logging() -> None:
    """Set up application logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('elevator_simulation.log'),
            logging.StreamHandler()
        ]
    )

class SimulationLogger:
    """
    Handles all simulation data logging and CSV output generation.
    
    This class follows the Single Responsibility Principle by focusing
    solely on data collection and persistence.
    """
    
    def __init__(self, output_dir: str = "simulation_output"):
        """
        Initialize the simulation logger.
        
        Args:
            output_dir: Directory for output files
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(exist_ok=True)
        
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._is_logging = False
        
        # Data buffers
        self._elevator_states = []
        self._passenger_events = []
        self._system_metrics = []
        self._button_presses = []
        
        # File handles
        self._csv_files = {}
        
        logging.info(f"Simulation logger initialized for session {self._session_id}")
    
    def start_logging(self) -> None:
        """Start logging session and open output files."""
        if self._is_logging:
            return
        
        self._is_logging = True
        self._open_csv_files()
        
        logging.info("Logging session started")
    
    def stop_logging(self) -> None:
        """Stop logging session and close output files."""
        if not self._is_logging:
            return
        
        self._is_logging = False
        self._close_csv_files()
        self._write_summary_files()
        
        logging.info("Logging session stopped")
    
    def log_elevator_state(self, elevator_id: str, state_data: Dict[str, Any]) -> None:
        """
        Log elevator state information.
        
        Args:
            elevator_id: Elevator identifier
            state_data: Dictionary containing elevator state
        """
        if not self._is_logging:
            return
        
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'elevator_id': elevator_id,
            **state_data
        }
        
        self._elevator_states.append(log_entry)
        self._write_to_csv('elevator_states', log_entry)
    
    def log_passenger_event(self, passenger_id: str, event_type: str, 
                           event_data: Dict[str, Any]) -> None:
        """
        Log passenger events (arrival, boarding, departure).
        
        Args:
            passenger_id: Passenger identifier
            event_type: Type of event (arrival, boarding, departure)
            event_data: Additional event data
        """
        if not self._is_logging:
            return
        
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'passenger_id': passenger_id,
            'event_type': event_type,
            **event_data
        }
        
        self._passenger_events.append(log_entry)
        self._write_to_csv('passenger_events', log_entry)
    
    def log_button_press(self, button_type: str, location: str, 
                        target: str, timestamp: float = None) -> None:
        """
        Log button press events.
        
        Args:
            button_type: Type of button (hall_call, elevator_floor)
            location: Location of button press
            target: Target floor or direction
            timestamp: Event timestamp (defaults to current time)
        """
        if not self._is_logging:
            return
        
        if timestamp is None:
            timestamp = time.time()
        
        log_entry = {
            'timestamp': timestamp,
            'button_type': button_type,
            'location': location,
            'target': target
        }
        
        self._button_presses.append(log_entry)
        self._write_to_csv('button_presses', log_entry)
    
    def log_system_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Log system-wide performance metrics.
        
        Args:
            metrics: Dictionary containing system metrics
        """
        if not self._is_logging:
            return
        
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            **metrics
        }
        
        self._system_metrics.append(log_entry)
        self._write_to_csv('system_metrics', log_entry)
    
    def log_simulation_state(self, simulation_state: Dict[str, Any]) -> None:
        """
        Log complete simulation state snapshot.
        
        Args:
            simulation_state: Complete simulation state dictionary
        """
        if not self._is_logging:
            return
        
        # Extract and log elevator states
        building_status = simulation_state.get('building_status', {})
        elevators = building_status.get('elevators', {})
        
        for elevator_id, elevator_data in elevators.items():
            self.log_elevator_state(elevator_id, elevator_data)
        
        # Log system metrics
        controller_metrics = simulation_state.get('controller_metrics', {})
        if controller_metrics:
            self.log_system_metrics(controller_metrics)
    
    def log_simulation_report(self, report: Dict[str, Any]) -> None:
        """
        Log final simulation report.
        
        Args:
            report: Complete simulation report
        """
        report_file = self._output_dir / f"simulation_report_{self._session_id}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logging.info(f"Simulation report saved to {report_file}")
            
        except Exception as e:
            logging.error(f"Error saving simulation report: {e}")
    
    def _open_csv_files(self) -> None:
        """Open CSV files for logging."""
        csv_configs = {
            'elevator_states': ['timestamp', 'elevator_id', 'current_floor', 'state', 
                               'direction', 'passenger_count', 'door_open'],
            'passenger_events': ['timestamp', 'passenger_id', 'event_type', 'floor', 
                                'elevator_id', 'origin_floor', 'destination_floor'],
            'button_presses': ['timestamp', 'button_type', 'location', 'target'],
            'system_metrics': ['timestamp', 'total_elevators', 'active_elevators', 
                              'idle_elevators', 'pending_requests']
        }
        
        for file_type, headers in csv_configs.items():
            file_path = self._output_dir / f"{file_type}_{self._session_id}.csv"
            
            try:
                csvfile = open(file_path, 'w', newline='')
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                self._csv_files[file_type] = {
                    'file': csvfile,
                    'writer': writer,
                    'headers': headers
                }
                
            except Exception as e:
                logging.error(f"Error opening CSV file {file_path}: {e}")
    
    def _close_csv_files(self) -> None:
        """Close all CSV files."""
        for file_type, file_info in self._csv_files.items():
            try:
                file_info['file'].close()
            except Exception as e:
                logging.error(f"Error closing CSV file for {file_type}: {e}")
        
        self._csv_files.clear()
    
    def _write_to_csv(self, file_type: str, data: Dict[str, Any]) -> None:
        """Write data to specific CSV file."""
        if file_type not in self._csv_files:
            return
        
        try:
            writer = self._csv_files[file_type]['writer']
            headers = self._csv_files[file_type]['headers']
            
            # Filter data to only include known headers
            filtered_data = {k: v for k, v in data.items() if k in headers}
            
            writer.writerow(filtered_data)
            self._csv_files[file_type]['file'].flush()
            
        except Exception as e:
            logging.error(f"Error writing to CSV file {file_type}: {e}")
    
    def _write_summary_files(self) -> None:
        """Write summary statistics files."""
        try:
            # Elevator summary
            if self._elevator_states:
                self._write_elevator_summary()
            
            # Passenger summary
            if self._passenger_events:
                self._write_passenger_summary()
            
            # System summary
            if self._system_metrics:
                self._write_system_summary()
                
        except Exception as e:
            logging.error(f"Error writing summary files: {e}")
    
    def _write_elevator_summary(self) -> None:
        """Write elevator performance summary."""
        summary_file = self._output_dir / f"elevator_summary_{self._session_id}.csv"
        
        # Calculate per-elevator statistics
        elevator_stats = {}
        
        for state in self._elevator_states:
            elevator_id = state['elevator_id']
            
            if elevator_id not in elevator_stats:
                elevator_stats[elevator_id] = {
                    'total_records': 0,
                    'floors_visited': set(),
                    'time_moving': 0,
                    'time_idle': 0,
                    'total_passengers': 0
                }
            
            stats = elevator_stats[elevator_id]
            stats['total_records'] += 1
            stats['floors_visited'].add(state.get('current_floor', 0))
            
            if state.get('state') in ['moving_up', 'moving_down']:
                stats['time_moving'] += 1
            elif state.get('state') == 'idle':
                stats['time_idle'] += 1
            
            stats['total_passengers'] = max(stats['total_passengers'], 
                                          state.get('passenger_count', 0))
        
        # Write summary CSV
        with open(summary_file, 'w', newline='') as csvfile:
            headers = ['elevator_id', 'total_records', 'unique_floors', 
                      'time_moving_pct', 'time_idle_pct', 'max_passengers']
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for elevator_id, stats in elevator_stats.items():
                total_time = stats['time_moving'] + stats['time_idle']
                
                writer.writerow({
                    'elevator_id': elevator_id,
                    'total_records': stats['total_records'],
                    'unique_floors': len(stats['floors_visited']),
                    'time_moving_pct': (stats['time_moving'] / max(total_time, 1)) * 100,
                    'time_idle_pct': (stats['time_idle'] / max(total_time, 1)) * 100,
                    'max_passengers': stats['total_passengers']
                })
    
    def _write_passenger_summary(self) -> None:
        """Write passenger statistics summary."""
        # Group events by passenger
        passenger_journeys = {}
        
        for event in self._passenger_events:
            passenger_id = event['passenger_id']
            
            if passenger_id not in passenger_journeys:
                passenger_journeys[passenger_id] = []
            
            passenger_journeys[passenger_id].append(event)
        
        # Calculate journey statistics
        summary_file = self._output_dir / f"passenger_summary_{self._session_id}.csv"
        
        with open(summary_file, 'w', newline='') as csvfile:
            headers = ['passenger_id', 'origin_floor', 'destination_floor', 
                      'wait_time', 'travel_time', 'total_time']
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for passenger_id, events in passenger_journeys.items():
                if len(events) >= 2:  # At least arrival and departure
                    arrival_event = min(events, key=lambda e: e['timestamp'])
                    departure_event = max(events, key=lambda e: e['timestamp'])
                    
                    wait_time = departure_event['timestamp'] - arrival_event['timestamp']
                    
                    writer.writerow({
                        'passenger_id': passenger_id,
                        'origin_floor': arrival_event.get('origin_floor', ''),
                        'destination_floor': arrival_event.get('destination_floor', ''),
                        'wait_time': wait_time,
                        'travel_time': 0,  # Would need boarding event to calculate
                        'total_time': wait_time
                    })
    
    def _write_system_summary(self) -> None:
        """Write system performance summary."""
        if not self._system_metrics:
            return
        
        summary_file = self._output_dir / f"system_summary_{self._session_id}.csv"
        
        # Calculate averages
        avg_metrics = {}
        metric_keys = self._system_metrics[0].keys()
        
        for key in metric_keys:
            if key != 'timestamp':
                values = [m.get(key, 0) for m in self._system_metrics if isinstance(m.get(key), (int, float))]
                if values:
                    avg_metrics[f'avg_{key}'] = sum(values) / len(values)
                    avg_metrics[f'max_{key}'] = max(values)
                    avg_metrics[f'min_{key}'] = min(values)
        
        with open(summary_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=avg_metrics.keys())
            writer.writeheader()
            writer.writerow(avg_metrics)