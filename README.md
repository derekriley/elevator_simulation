# Elevator Simulation Tool

A comprehensive elevator control system simulator for testing and evaluation of elevator dispatch algorithms and system performance.

## Features

- **Multi-Elevator Simulation**: Simulate multiple elevators with different configurations
- **Interactive GUI**: Intuitive graphical interface with elevator visualizations
- **Configurable Buildings**: Load building configurations from CSV files
- **Performance Monitoring**: Real-time metrics and performance analysis
- **Data Logging**: Comprehensive logging of all simulation events
- **Scenario Testing**: Run predefined simulation scenarios
- **Manual Control**: Interactive buttons for testing specific scenarios

## Architecture

The application is built using SOLID principles with clear separation of concerns:

- **Models**: Elevator, Building, Floor, and Passenger entities
- **Controllers**: Elevator dispatch logic and simulation control
- **GUI**: Tkinter-based user interface with modular components
- **Simulation**: Core simulation engine and logging system
- **Configuration**: CSV-based configuration management

## Quick Start

1. **Run the application**:
   ```bash
   python main.py