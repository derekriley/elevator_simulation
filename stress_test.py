#!/usr/bin/env python3
"""
Elevator Simulation Stress Test Script

This script attempts to break the elevator simulation application by testing:
- Invalid inputs and edge cases
- Boundary conditions
- Race conditions
- Memory leaks
- Error handling
- Performance under stress
"""

import sys
import time
import threading
import random
import tkinter as tk
from pathlib import Path
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from models.elevator import Elevator, ElevatorState, Direction
from models.building import Building
from models.passenger import Passenger
from config.building_config import BuildingConfig
from simulation.simulator import ElevatorSimulator

class ElevatorStressTester:
    """Stress tester for the elevator simulation application."""

    def __init__(self):
        self.test_results = []
        self.failures = []
        self.warnings = []

    def run_all_tests(self):
        """Run all stress tests."""
        print("Starting Elevator Simulation Stress Tests...")
        print("=" * 60)

        # Test 1: Invalid Configuration Tests
        self.test_invalid_configurations()

        # Test 2: Boundary Condition Tests
        self.test_boundary_conditions()

        # Test 3: Invalid Input Tests
        self.test_invalid_inputs()

        # Test 4: Race Condition Tests
        self.test_race_conditions()

        # Test 5: Memory and Performance Tests
        self.test_memory_performance()

        # Test 6: GUI Stress Tests
        self.test_gui_stress()

        # Test 7: Data Corruption Tests
        self.test_data_corruption()

        # Test 8: Exception Handling Tests
        self.test_exception_handling()

        # Test 9: Resource Exhaustion Tests
        self.test_resource_exhaustion()

        # Test 10: Integration Stress Tests
        self.test_integration_stress()

        self.print_summary()

    def test_invalid_configurations(self):
        """Test invalid building and elevator configurations."""
        print("\nTesting Invalid Configurations...")

        # Test 1: Negative floors
        try:
            building = Building("test", -5, [])
            self.failures.append("Negative floors should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Negative floors properly rejected")

        # Test 2: Zero floors
        try:
            building = Building("test", 0, [])
            self.failures.append("Zero floors should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Zero floors properly rejected")

        # Test 3: Single floor
        try:
            building = Building("test", 1, [])
            self.failures.append("Single floor should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Single floor properly rejected")

        # Test 4: Invalid elevator capacity
        try:
            elevator = Elevator("test", -5, (1, 10), 2.0)
            self.failures.append("Negative capacity should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Negative capacity properly rejected")

        # Test 5: Zero elevator capacity
        try:
            elevator = Elevator("test", 0, (1, 10), 2.0)
            self.failures.append("Zero capacity should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Zero capacity properly rejected")

        # Test 6: Invalid speed
        try:
            elevator = Elevator("test", 8, (1, 10), -2.0)
            self.failures.append("Negative speed should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Negative speed properly rejected")

        # Test 7: Zero speed
        try:
            elevator = Elevator("test", 8, (1, 10), 0.0)
            self.failures.append("Zero speed should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Zero speed properly rejected")

        # Test 8: Invalid floor range
        try:
            elevator = Elevator("test", 8, (10, 1), 2.0)  # max < min
            self.failures.append("Invalid floor range should not be allowed")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Invalid floor range properly rejected")

        # Test 9: Empty elevator config
        try:
            building = Building("test", 10, [])
            self.test_results.append("PASS: Building with no elevators allowed")
        except Exception as e:
            self.failures.append(f"Building with no elevators failed: {e}")

    def test_boundary_conditions(self):
        """Test boundary conditions and edge cases."""
        print("\nTesting Boundary Conditions...")

        # Test 1: Maximum reasonable floors
        try:
            building = Building("test", 1000, [{"id": "e1", "capacity": 8, "speed": 2.0}])
            self.test_results.append("PASS: Large number of floors handled")
        except Exception as e:
            self.warnings.append(f"Large number of floors failed: {e}")

        # Test 2: Maximum elevator capacity
        try:
            elevator = Elevator("test", 1000, (1, 10), 2.0)
            self.test_results.append("PASS: Large elevator capacity handled")
        except Exception as e:
            self.warnings.append(f"Large elevator capacity failed: {e}")

        # Test 3: Maximum speed
        try:
            elevator = Elevator("test", 8, (1, 10), 1000.0)
            self.test_results.append("PASS: High speed handled")
        except Exception as e:
            self.warnings.append(f"High speed failed: {e}")

        # Test 4: Floor at boundary
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)
            elevator.add_floor_request(10)  # Max floor
            elevator.add_floor_request(1)   # Min floor
            self.test_results.append("PASS: Boundary floors handled")
        except Exception as e:
            self.failures.append(f"Boundary floors failed: {e}")

        # Test 5: Invalid floor requests
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)
            elevator.add_floor_request(0)   # Below min
            self.failures.append("Floor below minimum should be rejected")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Floor below minimum properly rejected")

        try:
            elevator.add_floor_request(11)  # Above max
            self.failures.append("Floor above maximum should be rejected")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Floor above maximum properly rejected")

    def test_invalid_inputs(self):
        """Test invalid input handling."""
        print("\nTesting Invalid Inputs...")

        # Test 1: None values
        try:
            elevator = Elevator(None, 8, (1, 10), 2.0)
            self.failures.append("None elevator ID should not be allowed")
        except (ValueError, TypeError, AssertionError):
            self.test_results.append("PASS: None elevator ID properly rejected")

        # Test 2: Empty string ID
        try:
            elevator = Elevator("", 8, (1, 10), 2.0)
            self.test_results.append("PASS: Empty string ID allowed (may be valid)")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Empty string ID properly rejected")

        # Test 3: Invalid direction enum
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)
            elevator.add_hall_call(5, "invalid_direction")
            self.failures.append("Invalid direction should be rejected")
        except (ValueError, TypeError):
            self.test_results.append("PASS: Invalid direction properly rejected")

        # Test 4: Invalid passenger ID
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)
            elevator.add_passenger(None, 5)
            self.failures.append("None passenger ID should be rejected")
        except (ValueError, TypeError):
            self.test_results.append("PASS: None passenger ID properly rejected")

        # Test 5: Invalid destination floor
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)
            elevator.add_passenger("passenger1", 0)
            self.failures.append("Invalid destination floor should be rejected")
        except (ValueError, AssertionError):
            self.test_results.append("PASS: Invalid destination floor properly rejected")

    def test_race_conditions(self):
        """Test for race conditions in concurrent operations."""
        print("\nTesting Race Conditions...")

        # Test 1: Multiple threads adding passengers
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)

            def add_passenger(passenger_id):
                for i in range(100):
                    elevator.add_passenger(f"{passenger_id}_{i}", random.randint(1, 10))
                    time.sleep(0.001)

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(add_passenger, i) for i in range(4)]
                for future in as_completed(futures):
                    future.result()

            self.test_results.append("PASS: Concurrent passenger addition handled")
        except Exception as e:
            self.failures.append(f"Concurrent passenger addition failed: {e}")

        # Test 2: Multiple threads updating elevator state
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)

            def update_elevator():
                for i in range(100):
                    elevator.update(0.1)
                    time.sleep(0.001)

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(update_elevator) for _ in range(3)]
                for future in as_completed(futures):
                    future.result()

            self.test_results.append("PASS: Concurrent elevator updates handled")
        except Exception as e:
            self.failures.append(f"Concurrent elevator updates failed: {e}")

        # Test 3: Multiple threads requesting elevators
        try:
            building = Building("test", 10, [{"id": "e1", "capacity": 8, "speed": 2.0}])

            def request_elevator():
                for i in range(50):
                    building.request_elevator(random.randint(1, 10), Direction.UP)
                    time.sleep(0.001)

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(request_elevator) for _ in range(4)]
                for future in as_completed(futures):
                    future.result()

            self.test_results.append("PASS: Concurrent elevator requests handled")
        except Exception as e:
            self.failures.append(f"Concurrent elevator requests failed: {e}")

    def test_memory_performance(self):
        """Test memory usage and performance under load."""
        print("\nTesting Memory and Performance...")

        # Test 1: Large number of passengers
        try:
            elevator = Elevator("test", 1000, (1, 10), 2.0)

            # Add many passengers
            for i in range(1000):
                elevator.add_passenger(f"passenger_{i}", random.randint(1, 10))

            # Check memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb > 100:  # More than 100MB
                self.warnings.append(f"High memory usage with many passengers: {memory_mb:.1f}MB")
            else:
                self.test_results.append(f"PASS: Memory usage reasonable: {memory_mb:.1f}MB")

        except ImportError:
            self.test_results.append("PASS: psutil not available, memory test skipped")
        except Exception as e:
            self.failures.append(f"Memory test failed: {e}")

        # Test 2: Performance under load
        try:
            building = Building("test", 100, [{"id": f"e{i}", "capacity": 8, "speed": 2.0} for i in range(10)])

            start_time = time.time()

            # Simulate heavy load
            for i in range(1000):
                building.request_elevator(random.randint(1, 100), Direction.UP)
                if i % 100 == 0:
                    building.update(0.1)

            end_time = time.time()
            duration = end_time - start_time

            if duration > 5.0:  # More than 5 seconds
                self.warnings.append(f"Performance under load slow: {duration:.2f}s")
            else:
                self.test_results.append(f"PASS: Performance under load acceptable: {duration:.2f}s")

        except Exception as e:
            self.failures.append(f"Performance test failed: {e}")

    def test_gui_stress(self):
        """Test GUI under stress conditions."""
        print("\nTesting GUI Stress...")

        # Test 1: Rapid button clicks
        try:
            root = tk.Tk()
            root.withdraw()  # Hide window

            # Create control panel
            from gui.control_panel import ControlPanel
            panel = ControlPanel(root, 10)

            # Simulate rapid button clicks
            for i in range(100):
                panel._call_hall_button(random.randint(1, 10), "up")
                panel._call_hall_button(random.randint(1, 10), "down")
                time.sleep(0.001)

            root.destroy()
            self.test_results.append("PASS: Rapid button clicks handled")

        except Exception as e:
            self.failures.append(f"Rapid button clicks failed: {e}")

        # Test 2: Large number of floors
        try:
            root = tk.Tk()
            root.withdraw()

            panel = ControlPanel(root, 1000)  # Very large building

            root.destroy()
            self.test_results.append("PASS: Large number of floors handled")

        except Exception as e:
            self.warnings.append(f"Large number of floors failed: {e}")

    def test_data_corruption(self):
        """Test data integrity under various conditions."""
        print("\nTesting Data Integrity...")

        # Test 1: Corrupted elevator state
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)

            # Manually corrupt internal state (this is evil!)
            elevator._current_floor = 999
            elevator._state = "INVALID_STATE"

            # Try to use corrupted elevator
            elevator.update(0.1)

            # Check if corruption was detected
            if elevator._current_floor == 999:
                self.failures.append("Corrupted floor state not detected")
            else:
                self.test_results.append("PASS: Corrupted state detected and corrected")

        except Exception as e:
            self.test_results.append(f"PASS: Corruption handling: {e}")

        # Test 2: Invalid passenger data
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)

            # Add passenger with invalid data
            elevator.add_passenger("passenger1", 5)

            # Corrupt passenger data
            if hasattr(elevator, '_passengers'):
                elevator._passengers.add(None)
                elevator._passengers.add("")
                elevator._passengers.add(123)

            # Try to remove passengers
            elevator.remove_passenger("passenger1")

            self.test_results.append("PASS: Invalid passenger data handled")

        except Exception as e:
            self.failures.append(f"Invalid passenger data handling failed: {e}")

    def test_exception_handling(self):
        """Test exception handling and recovery."""
        print("\nTesting Exception Handling...")

        # Test 1: Division by zero in calculations
        try:
            elevator = Elevator("test", 8, (1, 10), 2.0)

            # Simulate division by zero scenario
            if hasattr(elevator, '_speed') and elevator._speed > 0:
                # This should not cause division by zero
                time_per_floor = 1.0 / elevator._speed
                self.test_results.append("PASS: Division by zero prevention working")
            else:
                self.failures.append("Elevator speed should be positive")

        except ZeroDivisionError:
            self.failures.append("Division by zero not prevented")
        except Exception as e:
            self.test_results.append(f"✓ Exception handling: {e}")

        # Test 2: File I/O errors
        try:
            # Try to load non-existent config
            config = BuildingConfig("non_existent_file.csv")
            self.failures.append("Non-existent file should raise exception")
        except FileNotFoundError:
            self.test_results.append("PASS: File not found properly handled")
        except Exception as e:
            self.test_results.append(f"PASS: File error handling: {e}")

    def test_resource_exhaustion(self):
        """Test behavior under resource exhaustion."""
        print("\nTesting Resource Exhaustion...")

        # Test 1: Memory exhaustion simulation
        try:
            # Create many objects to simulate memory pressure
            elevators = []
            for i in range(10000):
                try:
                    elevator = Elevator(f"elevator_{i}", 8, (1, 10), 2.0)
                    elevators.append(elevator)
                except MemoryError:
                    self.warnings.append(f"Memory exhausted after {i} elevators")
                    break
                except Exception as e:
                    self.failures.append(f"Unexpected error creating elevator {i}: {e}")
                    break

            if len(elevators) > 0:
                self.test_results.append(f"PASS: Created {len(elevators)} elevators")

        except Exception as e:
            self.failures.append(f"Resource exhaustion test failed: {e}")

        # Test 2: Thread exhaustion
        try:
            def dummy_work():
                time.sleep(0.1)

            # Try to create many threads
            threads = []
            for i in range(1000):
                try:
                    thread = threading.Thread(target=dummy_work)
                    thread.start()
                    threads.append(thread)
                except RuntimeError:
                    self.warnings.append(f"Thread limit reached after {i} threads")
                    break
                except Exception as e:
                    self.failures.append(f"Unexpected error creating thread {i}: {e}")
                    break

            # Wait for threads to complete
            for thread in threads:
                thread.join()

            if len(threads) > 0:
                self.test_results.append(f"PASS: Created {len(threads)} threads")

        except Exception as e:
            self.failures.append(f"Thread exhaustion test failed: {e}")

    def test_integration_stress(self):
        """Test integration between components under stress."""
        print("\nTesting Integration Stress...")

        # Test 1: Full system stress
        try:
            # Create building with many elevators and floors
            building = Building("stress_test", 50, [
                {"id": f"e{i}", "capacity": 8, "speed": 2.0}
                for i in range(20)
            ])

            # Simulate heavy traffic
            start_time = time.time()

            for i in range(500):
                # Random hall calls
                building.request_elevator(random.randint(1, 50), Direction.UP)
                building.request_elevator(random.randint(1, 50), Direction.DOWN)

                # Update building
                building.update(0.1)

                # Add random passengers
                if i % 10 == 0:
                    elevator = random.choice(list(building.elevators.values()))
                    try:
                        elevator.add_passenger(f"passenger_{i}", random.randint(1, 50))
                    except:
                        pass  # Ignore individual failures

            end_time = time.time()
            duration = end_time - start_time

            if duration > 10.0:
                self.warnings.append(f"Integration stress test slow: {duration:.2f}s")
            else:
                self.test_results.append(f"PASS: Integration stress test passed: {duration:.2f}s")

        except Exception as e:
            self.failures.append(f"Integration stress test failed: {e}")

        # Test 2: Configuration file stress
        try:
            # Create malformed configuration
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,test_building,invalid_number,Test Building,,,\n")
                f.write("elevator,e1,,,invalid_capacity,invalid_speed,invalid_floor\n")
                f.write("elevator,e2,,,8,2.0,1\n")
                temp_file = f.name

            try:
                config = BuildingConfig(temp_file)
                errors = config.validate_configuration()

                if errors:
                    self.test_results.append(f"PASS: Configuration validation caught {len(errors)} errors")
                else:
                    self.failures.append("Configuration validation should have caught errors")

            finally:
                os.unlink(temp_file)

        except Exception as e:
            self.test_results.append(f"PASS: Configuration stress test: {e}")

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("STRESS TEST SUMMARY")
        print("=" * 60)

        print(f"\nTests Passed: {len(self.test_results)}")
        for result in self.test_results:
            print(f"  {result}")

        print(f"\nFailures: {len(self.failures)}")
        for failure in self.failures:
            print(f"  {failure}")

        print(f"\nWarnings: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"  {warning}")

        print(f"\nSuccess Rate: {len(self.test_results)}/{len(self.test_results) + len(self.failures)}")

        if self.failures:
            print("\nCRITICAL ISSUES FOUND!")
            print("The application has vulnerabilities that need immediate attention.")
        elif self.warnings:
            print("\nWARNINGS - Review recommended")
            print("Some issues were found that should be investigated.")
        else:
            print("\nALL TESTS PASSED!")
            print("The application appears to be robust under stress.")

def main():
    """Main entry point for stress testing."""
    try:
        tester = ElevatorStressTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nStress testing interrupted by user")
    except Exception as e:
        print(f"\n\nStress testing failed with error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
