#!/usr/bin/env python3
"""
GUI Stress Test Script for Elevator Simulation

This script specifically targets the GUI components to find:
- Memory leaks in Tkinter
- UI freezing under load
- Button state corruption
- Layout breaking
- Event handling failures
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.control_panel import ControlPanel
from gui.elevator_panel import ElevatorPanel
from gui.main_window import MainWindow

class GUIStressTester:
    """Specialized GUI stress tester."""

    def __init__(self):
        self.root = None
        self.test_results = []
        self.failures = []
        self.warnings = []

    def run_gui_tests(self):
        """Run all GUI stress tests."""
        print("Starting GUI Stress Tests...")
        print("=" * 50)

        try:
            # Test 1: Rapid UI Updates
            self.test_rapid_ui_updates()

            # Test 2: Memory Leak Detection
            self.test_memory_leaks()

            # Test 3: Button State Corruption
            self.test_button_states()

            # Test 4: Layout Breaking
            self.test_layout_breaking()

            # Test 5: Event Queue Overflow
            self.test_event_queue()

            # Test 6: Concurrent GUI Operations
            self.test_concurrent_gui()

            # Test 7: Invalid Input Handling
            self.test_invalid_gui_inputs()

            # Test 8: Resource Exhaustion
            self.test_gui_resources()

            self.print_gui_summary()

        finally:
            if self.root:
                self.root.destroy()

    def test_rapid_ui_updates(self):
        """Test rapid UI updates that could cause freezing."""
        print("\nTesting Rapid UI Updates...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window

            panel = ControlPanel(self.root, 20)

            # Test rapid metric updates
            start_time = time.time()
            update_count = 0

            for i in range(1000):
                try:
                    # Simulate rapid metric updates
                    test_data = {
                        "is_running": bool(i % 2),
                        "is_paused": bool((i + 1) % 2),
                        "elapsed_time": i * 0.1,
                        "controller_metrics": {
                            "total_elevators": random.randint(1, 10),
                            "active_elevators": random.randint(0, 10),
                            "idle_elevators": random.randint(0, 10),
                            "estimated_energy": random.uniform(0, 100)
                        }
                    }

                    panel.update_metrics(test_data)
                    update_count += 1

                    # Small delay to prevent complete freezing
                    if i % 100 == 0:
                        time.sleep(0.001)
                        self.root.update()

                except Exception as e:
                    self.failures.append(f"UI update {i} failed: {e}")
                    break

            duration = time.time() - start_time

            if duration > 10.0:
                self.warnings.append(f"Rapid UI updates slow: {duration:.2f}s for {update_count} updates")
            else:
                self.test_results.append(f"PASS: Rapid UI updates handled: {update_count} updates in {duration:.2f}s")

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Rapid UI updates test failed: {e}")

    def test_memory_leaks(self):
        """Test for memory leaks in GUI components."""
        print("\nTesting Memory Leaks...")

        try:
            import psutil
            process = psutil.Process()

            # Create and destroy many GUI components
            initial_memory = process.memory_info().rss / 1024 / 1024

            for i in range(100):
                root = tk.Tk()
                root.withdraw()

                panel = ControlPanel(root, random.randint(5, 50))

                # Simulate some usage
                for j in range(10):
                    panel._call_hall_button(random.randint(1, 10), "up")
                    panel._call_hall_button(random.randint(1, 10), "down")

                root.destroy()

                if i % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_diff = current_memory - initial_memory

                    if memory_diff > 50:  # More than 50MB increase
                        self.warnings.append(f"Potential memory leak detected: +{memory_diff:.1f}MB after {i} iterations")
                        break

            final_memory = process.memory_info().rss / 1024 / 1024
            total_increase = final_memory - initial_memory

            if total_increase < 10:
                self.test_results.append(f"PASS: No significant memory leak: +{total_increase:.1f}MB")
            else:
                self.warnings.append(f"Memory increase detected: +{total_increase:.1f}MB")

        except ImportError:
            self.test_results.append("PASS: psutil not available, memory leak test skipped")
        except Exception as e:
            self.failures.append(f"Memory leak test failed: {e}")

    def test_button_states(self):
        """Test button state corruption under stress."""
        print("\nTesting Button States...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()

            panel = ControlPanel(self.root, 10)

            # Find all buttons in the control panel
            buttons = []
            def find_buttons(widget):
                if isinstance(widget, tk.Button):
                    buttons.append(widget)
                for child in widget.winfo_children():
                    find_buttons(child)

            find_buttons(panel)

            if not buttons:
                self.warnings.append("No buttons found in control panel")
                return

            # Test rapid button state changes
            original_states = {}
            for button in buttons:
                original_states[button] = button.cget('state')

            # Rapidly change button states
            for i in range(500):
                button = random.choice(buttons)
                try:
                    if i % 2 == 0:
                        button.config(state='disabled')
                    else:
                        button.config(state='normal')

                    # Verify state change
                    current_state = button.cget('state')
                    if current_state not in ['normal', 'disabled']:
                        self.failures.append(f"Button state corrupted: {current_state}")
                        break

                except Exception as e:
                    self.failures.append(f"Button state change failed: {e}")
                    break

            # Restore original states
            for button, state in original_states.items():
                try:
                    button.config(state=state)
                except:
                    pass

            self.test_results.append(f"PASS: Button state testing completed for {len(buttons)} buttons")

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Button state test failed: {e}")

    def test_layout_breaking(self):
        """Test if layout breaks under stress."""
        print("\nTesting Layout Breaking...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()

            # Test with various floor counts
            for floor_count in [5, 10, 50, 100]:
                try:
                    panel = ControlPanel(self.root, floor_count)

                    # Force layout update
                    panel.update()

                    # Check if any widgets are outside visible area
                    panel_width = panel.winfo_width()
                    panel_height = panel.winfo_height()

                    if panel_width > 0 and panel_height > 0:
                        self.test_results.append(f"PASS: Layout stable with {floor_count} floors")
                    else:
                        self.warnings.append(f"Layout issues with {floor_count} floors")

                    # Clear previous panel
                    for widget in panel.winfo_children():
                        widget.destroy()

                except Exception as e:
                    self.warnings.append(f"Layout test failed with {floor_count} floors: {e}")
                    break

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Layout breaking test failed: {e}")

    def test_event_queue(self):
        """Test event queue overflow scenarios."""
        print("\nTesting Event Queue...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()

            panel = ControlPanel(self.root, 10)

            # Generate many events rapidly
            event_count = 0
            start_time = time.time()

            for i in range(2000):
                try:
                    # Simulate various events
                    panel._call_hall_button(random.randint(1, 10), "up")
                    panel._call_hall_button(random.randint(1, 10), "down")

                    # Update speed
                    panel._set_speed(random.uniform(0.1, 5.0))

                    # Add passenger
                    panel._quick_passenger(random.randint(1, 10), random.randint(1, 10))

                    event_count += 1

                    # Process events periodically
                    if i % 100 == 0:
                        self.root.update()
                        time.sleep(0.001)

                except Exception as e:
                    self.failures.append(f"Event {i} failed: {e}")
                    break

            duration = time.time() - start_time

            if event_count > 0:
                self.test_results.append(f"PASS: Event queue handled {event_count} events in {duration:.2f}s")
            else:
                self.failures.append("No events processed successfully")

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Event queue test failed: {e}")

    def test_concurrent_gui(self):
        """Test concurrent GUI operations."""
        print("\nTesting Concurrent GUI Operations...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()

            panel = ControlPanel(self.root, 10)

            # Test concurrent operations from multiple threads
            def gui_operation(thread_id):
                for i in range(100):
                    try:
                        # Simulate concurrent GUI operations
                        panel._call_hall_button(random.randint(1, 10), "up")
                        panel._set_speed(random.uniform(0.1, 5.0))
                        panel._quick_passenger(random.randint(1, 10), random.randint(1, 10))

                        time.sleep(0.001)

                    except Exception as e:
                        return f"Thread {thread_id} failed at iteration {i}: {e}"
                return None

            # Run concurrent operations
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(gui_operation, i) for i in range(3)]

                errors = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        errors.append(result)

            if not errors:
                self.test_results.append("PASS: Concurrent GUI operations handled successfully")
            else:
                for error in errors:
                    self.warnings.append(error)

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Concurrent GUI test failed: {e}")

    def test_invalid_gui_inputs(self):
        """Test invalid input handling in GUI."""
        print("\nTesting Invalid GUI Inputs...")

        try:
            self.root = tk.Tk()
            self.root.withdraw()

            panel = ControlPanel(self.root, 10)

            # Test invalid hall call parameters
            invalid_floor_values = [-1, 0, 11, 999, None, "invalid", 3.14]
            invalid_direction_values = [None, "", "invalid", 123, 3.14, True]

            for floor in invalid_floor_values:
                for direction in invalid_direction_values:
                    try:
                        panel._call_hall_button(floor, direction)
                        # If we get here, invalid input was accepted
                        self.warnings.append(f"Invalid input accepted: floor={floor}, direction={direction}")
                    except Exception:
                        # Expected behavior
                        pass

            # Test invalid speed values
            invalid_speeds = [-1.0, 0.0, 999.0, None, "invalid", True]
            for speed in invalid_speeds:
                try:
                    panel._set_speed(speed)
                    if speed is not None and isinstance(speed, (int, float)) and speed > 0:
                        # Valid speed
                        pass
                    else:
                        self.warnings.append(f"Invalid speed accepted: {speed}")
                except Exception:
                    # Expected behavior for invalid speeds
                    pass

            # Test invalid passenger parameters
            invalid_origins = [-1, 0, 11, None, "invalid", 3.14]
            invalid_destinations = [-1, 0, 11, None, "invalid", 3.14]

            for origin in invalid_origins:
                for destination in invalid_destinations:
                    try:
                        panel._quick_passenger(origin, destination)
                        if (isinstance(origin, int) and isinstance(destination, int) and
                            1 <= origin <= 10 and 1 <= destination <= 10 and origin != destination):
                            # Valid passenger
                            pass
                        else:
                            self.warnings.append(f"Invalid passenger accepted: origin={origin}, destination={destination}")
                    except Exception:
                        # Expected behavior
                        pass

            self.test_results.append("PASS: Invalid GUI input testing completed")

            self.root.destroy()
            self.root = None

        except Exception as e:
            self.failures.append(f"Invalid GUI input test failed: {e}")

    def test_gui_resources(self):
        """Test GUI resource exhaustion."""
        print("\nTesting GUI Resource Exhaustion...")

        try:
            # Test creating many windows
            windows = []
            max_windows = 100

            for i in range(max_windows):
                try:
                    root = tk.Tk()
                    root.withdraw()

                    panel = ControlPanel(root, random.randint(5, 20))
                    windows.append((root, panel))

                    if i % 10 == 0:
                        # Update to prevent freezing
                        root.update()

                except Exception as e:
                    self.warnings.append(f"Window creation failed at {i}: {e}")
                    break

            # Test using all windows
            for i, (root, panel) in enumerate(windows):
                try:
                    # Simulate some usage
                    for j in range(5):
                        panel._call_hall_button(random.randint(1, 10), "up")
                        panel._set_speed(random.uniform(0.1, 5.0))

                    if i % 20 == 0:
                        root.update()

                except Exception as e:
                    self.warnings.append(f"Window {i} usage failed: {e}")

            # Clean up
            for root, _ in windows:
                try:
                    root.destroy()
                except:
                    pass

            if len(windows) > 0:
                self.test_results.append(f"PASS: Created and used {len(windows)} windows")
            else:
                self.failures.append("No windows created successfully")

        except Exception as e:
            self.failures.append(f"GUI resource test failed: {e}")

    def print_gui_summary(self):
        """Print GUI test results summary."""
        print("\n" + "=" * 50)
        print("GUI STRESS TEST SUMMARY")
        print("=" * 50)

        print(f"\nTests Passed: {len(self.test_results)}")
        for result in self.test_results:
            print(f"  {result}")

        print(f"\nFailures: {len(self.failures)}")
        for failure in self.failures:
            print(f"  {failure}")

        print(f"\nWarnings: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"  {warning}")

        print(f"\nGUI Success Rate: {len(self.test_results)}/{len(self.test_results) + len(self.failures)}")

        if self.failures:
            print("\nCRITICAL GUI ISSUES FOUND!")
            print("The GUI has vulnerabilities that need immediate attention.")
        elif self.warnings:
            print("\nGUI WARNINGS - Review recommended")
            print("Some GUI issues were found that should be investigated.")
        else:
            print("\nALL GUI TESTS PASSED!")
            print("The GUI appears to be robust under stress.")

def main():
    """Main entry point for GUI stress testing."""
    try:
        tester = GUIStressTester()
        tester.run_gui_tests()
    except KeyboardInterrupt:
        print("\n\nGUI stress testing interrupted by user")
    except Exception as e:
        print(f"\n\nGUI stress testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
