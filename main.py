import sys
import tkinter as tk
from pathlib import Path
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from simulation.logger import setup_logging

def main():
    """Main entry point for the elevator simulation tool."""
    setup_logging()
    logging.info("Starting Elevator Simulation Tool")
    
    root = tk.Tk()
    app = MainWindow(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Elevator Simulation Tool shutting down")

if __name__ == "__main__":
    main()
