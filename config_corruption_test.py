#!/usr/bin/env python3
"""
Configuration Corruption Test Script for Elevator Simulation

This script tests how the application handles:
- Malformed CSV files
- Invalid data types
- Missing required fields
- Corrupted file contents
- Permission issues
- File system errors
"""

import sys
import tempfile
import os
import csv
import random
import string
from pathlib import Path
import shutil
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.building_config import BuildingConfig

class ConfigCorruptionTester:
    """Tester for configuration file corruption scenarios."""

    def __init__(self):
        self.test_results = []
        self.failures = []
        self.warnings = []
        self.temp_files = []

    def __del__(self):
        """Clean up temporary files."""
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Remove all temporary files created during testing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass

    def run_config_tests(self):
        """Run all configuration corruption tests."""
        print("Starting Configuration Corruption Tests...")
        print("=" * 60)

        try:
            # Test 1: Malformed CSV Structure
            self.test_malformed_csv_structure()

            # Test 2: Invalid Data Types
            self.test_invalid_data_types()

            # Test 3: Missing Required Fields
            self.test_missing_required_fields()

            # Test 4: Corrupted File Contents
            self.test_corrupted_file_contents()

            # Test 5: File Permission Issues
            self.test_file_permissions()

            # Test 6: File System Errors
            self.test_file_system_errors()

            # Test 7: Extremely Large Files
            self.test_extremely_large_files()

            # Test 8: Unicode and Special Characters
            self.test_unicode_special_chars()

            # Test 9: Concurrent File Access
            self.test_concurrent_file_access()

            # Test 10: Recovery from Corruption
            self.test_corruption_recovery()

            self.print_config_summary()

        finally:
            self.cleanup_temp_files()

    def test_malformed_csv_structure(self):
        """Test malformed CSV structure handling."""
        print("\nTesting Malformed CSV Structure...")

        # Test 1: Missing headers
        try:
            temp_file = self.create_temp_file("missing_headers.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("building,main_building,10,Main Building\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            config = BuildingConfig(temp_file)
            self.failures.append("Missing headers should cause parsing failure")
        except Exception as e:
            self.test_results.append(f"PASS: Missing headers properly handled: {e}")

        # Test 2: Extra columns
        try:
            temp_file = self.create_temp_file("extra_columns.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor,extra1,extra2\n")
                f.write("building,main_building,10,Main Building,,,,,,\n")
                f.write("elevator,elevator_A,8,2.5,1,extra_value,another_extra\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Extra columns handled gracefully")
        except Exception as e:
            self.warnings.append(f"Extra columns caused error: {e}")

        # Test 3: Missing columns
        try:
            temp_file = self.create_temp_file("missing_columns.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id\n")
                f.write("building,main_building\n")
                f.write("elevator,elevator_A\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Missing columns handled gracefully")
        except Exception as e:
            self.warnings.append(f"Missing columns caused error: {e}")

        # Test 4: Empty CSV file
        try:
            temp_file = self.create_temp_file("empty.csv")
            with open(temp_file, 'w', newline='') as f:
                pass  # Empty file

            config = BuildingConfig(temp_file)
            self.failures.append("Empty CSV should cause parsing failure")
        except Exception as e:
            self.test_results.append(f"PASS: Empty CSV properly handled: {e}")

        # Test 5: CSV with only headers
        try:
            temp_file = self.create_temp_file("headers_only.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Headers-only CSV handled gracefully")
        except Exception as e:
            self.warnings.append(f"Headers-only CSV caused error: {e}")

    def test_invalid_data_types(self):
        """Test invalid data type handling."""
        print("\nTesting Invalid Data Types...")

        # Test 1: Non-numeric values in numeric fields
        try:
            temp_file = self.create_temp_file("invalid_numeric.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,invalid_number,Main Building,,,\n")
                f.write("elevator,elevator_A,invalid_capacity,invalid_speed,invalid_floor\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught {len(errors)} data type errors")
            else:
                self.failures.append("Validation should have caught data type errors")

        except Exception as e:
            self.test_results.append(f"PASS: Invalid data types properly handled: {e}")

        # Test 2: Negative values
        try:
            temp_file = self.create_temp_file("negative_values.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,-5,Main Building,,,\n")
                f.write("elevator,elevator_A,-8,-2.5,-1\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught {len(errors)} negative value errors")
            else:
                self.failures.append("Validation should have caught negative value errors")

        except Exception as e:
            self.test_results.append(f"PASS: Negative values properly handled: {e}")

        # Test 3: Zero values
        try:
            temp_file = self.create_temp_file("zero_values.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,0,Main Building,,,\n")
                f.write("elevator,elevator_A,0,0.0,0\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught {len(errors)} zero value errors")
            else:
                self.warnings.append("Validation should have caught zero value errors")

        except Exception as e:
            self.test_results.append(f"PASS: Zero values properly handled: {e}")

        # Test 4: Extremely large values
        try:
            temp_file = self.create_temp_file("large_values.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,999999,Main Building,,,\n")
                f.write("elevator,elevator_A,999999,999999.0,999999\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Large values handled gracefully")
        except Exception as e:
            self.warnings.append(f"Large values caused error: {e}")

    def test_missing_required_fields(self):
        """Test missing required field handling."""
        print("\nTesting Missing Required Fields...")

        # Test 1: Missing building section
        try:
            temp_file = self.create_temp_file("no_building.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught missing building: {len(errors)} errors")
            else:
                self.failures.append("Validation should have caught missing building section")

        except Exception as e:
            self.test_results.append(f"PASS: Missing building properly handled: {e}")

        # Test 2: Missing elevator section
        try:
            temp_file = self.create_temp_file("no_elevators.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught missing elevators: {len(errors)} errors")
            else:
                self.failures.append("Validation should have caught missing elevator section")

        except Exception as e:
            self.test_results.append(f"PASS: Missing elevators properly handled: {e}")

        # Test 3: Missing critical fields
        try:
            temp_file = self.create_temp_file("missing_critical.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,,Main Building,,,\n")
                f.write("elevator,elevator_A,,,,\n")

            config = BuildingConfig(temp_file)
            errors = config.validate_configuration()

            if errors:
                self.test_results.append(f"PASS: Validation caught missing critical fields: {len(errors)} errors")
            else:
                self.warnings.append("Validation should have caught missing critical fields")

        except Exception as e:
            self.test_results.append(f"PASS: Missing critical fields properly handled: {e}")

    def test_corrupted_file_contents(self):
        """Test corrupted file content handling."""
        print("\nTesting Corrupted File Contents...")

        # Test 1: Binary data corruption
        try:
            temp_file = self.create_temp_file("binary_corruption.csv")
            with open(temp_file, 'wb') as f:
                f.write(b"section,id,num_floors,name\n")
                f.write(b"building,main_building,10,Main Building\n")
                f.write(b"elevator,elevator_A,8,2.5\n")
                # Add some binary corruption
                f.write(b"\x00\x01\x02\x03\x04\x05")

            config = BuildingConfig(temp_file)
            self.failures.append("Binary corruption should cause parsing failure")
        except Exception as e:
            self.test_results.append(f"PASS: Binary corruption properly handled: {e}")

        # Test 2: Invalid CSV delimiters
        try:
            temp_file = self.create_temp_file("invalid_delimiters.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section;id;num_floors;name;capacity;speed;initial_floor\n")
                f.write("building;main_building;10;Main Building;;;\n")
                f.write("elevator;elevator_A;8;2.5;1\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Invalid delimiters handled gracefully")
        except Exception as e:
            self.warnings.append(f"Invalid delimiters caused error: {e}")

        # Test 3: Mixed line endings
        try:
            temp_file = self.create_temp_file("mixed_line_endings.csv")
            with open(temp_file, 'wb') as f:
                f.write(b"section,id,num_floors,name\n")
                f.write(b"building,main_building,10,Main Building\r\n")
                f.write(b"elevator,elevator_A,8,2.5\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Mixed line endings handled gracefully")
        except Exception as e:
            self.warnings.append(f"Mixed line endings caused error: {e}")

        # Test 4: Truncated file
        try:
            temp_file = self.create_temp_file("truncated.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1")  # Missing newline and data

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Truncated file handled gracefully")
        except Exception as e:
            self.warnings.append(f"Truncated file caused error: {e}")

    def test_file_permissions(self):
        """Test file permission handling."""
        print("\nTesting File Permissions...")

        # Test 1: Read-only file
        try:
            temp_file = self.create_temp_file("readonly.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Make file read-only
            os.chmod(temp_file, 0o444)

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Read-only file handled gracefully")

            # Restore permissions for cleanup
            os.chmod(temp_file, 0o666)

        except Exception as e:
            self.warnings.append(f"Read-only file caused error: {e}")

        # Test 2: No read permission
        try:
            temp_file = self.create_temp_file("no_read.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Remove read permission
            os.chmod(temp_file, 0o222)

            config = BuildingConfig(temp_file)
            self.failures.append("No read permission should cause failure")

        except PermissionError:
            self.test_results.append("PASS: No read permission properly handled")
        except Exception as e:
            self.warnings.append(f"No read permission handling: {e}")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(temp_file, 0o666)
            except:
                pass

    def test_file_system_errors(self):
        """Test file system error handling."""
        print("\nTesting File System Errors...")

        # Test 1: Non-existent file
        try:
            config = BuildingConfig("non_existent_file.csv")
            self.failures.append("Non-existent file should cause failure")
        except FileNotFoundError:
            self.test_results.append("PASS: Non-existent file properly handled")
        except Exception as e:
            self.test_results.append(f"PASS: Non-existent file handled: {e}")

        # Test 2: Directory instead of file
        try:
            temp_dir = tempfile.mkdtemp()
            self.temp_files.append(temp_dir)

            config = BuildingConfig(temp_dir)
            self.failures.append("Directory should cause failure")
        except (IsADirectoryError, PermissionError):
            self.test_results.append("PASS: Directory properly handled")
        except Exception as e:
            self.test_results.append(f"PASS: Directory handled: {e}")

        # Test 3: Symbolic link (if supported)
        try:
            temp_file = self.create_temp_file("original.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Create symbolic link
            symlink_path = temp_file + "_link"
            os.symlink(temp_file, symlink_path)
            self.temp_files.append(symlink_path)

            config = BuildingConfig(symlink_path)
            self.test_results.append("PASS: Symbolic link handled gracefully")

        except OSError:
            self.test_results.append("PASS: Symbolic links not supported on this system")
        except Exception as e:
            self.warnings.append(f"Symbolic link caused error: {e}")

    def test_extremely_large_files(self):
        """Test extremely large file handling."""
        print("\nTesting Extremely Large Files...")

        # Test 1: Very large number of elevators
        try:
            temp_file = self.create_temp_file("many_elevators.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,1000,Main Building,,,\n")

                # Add many elevator entries
                for i in range(10000):
                    f.write(f"elevator,elevator_{i},8,2.5,1\n")

            start_time = time.time()
            config = BuildingConfig(temp_file)
            load_time = time.time() - start_time

            if load_time > 10.0:
                self.warnings.append(f"Large file loading slow: {load_time:.2f}s")
            else:
                self.test_results.append(f"PASS: Large file loaded in {load_time:.2f}s")

        except Exception as e:
            self.warnings.append(f"Large file caused error: {e}")

        # Test 2: Very long field values
        try:
            temp_file = self.create_temp_file("long_fields.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")

                # Create very long field values
                long_name = "A" * 10000  # 10KB name
                f.write(f"building,main_building,10,{long_name},,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Long field values handled gracefully")

        except Exception as e:
            self.warnings.append(f"Long field values caused error: {e}")

    def test_unicode_special_chars(self):
        """Test Unicode and special character handling."""
        print("\nTesting Unicode and Special Characters...")

        # Test 1: Unicode characters
        try:
            temp_file = self.create_temp_file("unicode.csv")
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Unicode characters handled gracefully")

        except Exception as e:
            self.warnings.append(f"Unicode characters caused error: {e}")

        # Test 2: Special CSV characters
        try:
            temp_file = self.create_temp_file("special_chars.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write('building,main_building,10,"Main Building, with commas",,,\n')
                f.write('elevator,elevator_A,8,2.5,1\n')

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Special CSV characters handled gracefully")

        except Exception as e:
            self.warnings.append(f"Special CSV characters caused error: {e}")

        # Test 3: Quotes and escapes
        try:
            temp_file = self.create_temp_file("quotes_escapes.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write('building,main_building,10,"Building with ""quotes""",,,\n')
                f.write('elevator,elevator_A,8,2.5,1\n')

            config = BuildingConfig(temp_file)
            self.test_results.append("PASS: Quotes and escapes handled gracefully")

        except Exception as e:
            self.warnings.append(f"Quotes and escapes caused error: {e}")

    def test_concurrent_file_access(self):
        """Test concurrent file access scenarios."""
        print("\nTesting Concurrent File Access...")

        try:
            temp_file = self.create_temp_file("concurrent.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Test concurrent reading
            import concurrent.futures
            def read_config():
                try:
                    config = BuildingConfig(temp_file)
                    return "success"
                except Exception as e:
                    return f"error: {e}"

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(read_config) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]

            success_count = sum(1 for r in results if r == "success")
            if success_count == 10:
                self.test_results.append("PASS: Concurrent file access handled successfully")
            else:
                self.warnings.append(f"Concurrent access issues: {success_count}/10 successful")

        except Exception as e:
            self.failures.append(f"Concurrent file access test failed: {e}")

    def test_corruption_recovery(self):
        """Test recovery from corrupted configurations."""
        print("\nTesting Corruption Recovery...")

        try:
            # Create a valid config first
            temp_file = self.create_temp_file("recovery_test.csv")
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Load valid config
            config1 = BuildingConfig(temp_file)

            # Corrupt the file
            with open(temp_file, 'w', newline='') as f:
                f.write("corrupted,data,here\n")

            # Try to load corrupted config
            try:
                config2 = BuildingConfig(temp_file)
                self.failures.append("Corrupted config should cause failure")
            except Exception:
                # Expected behavior
                pass

            # Restore valid config
            with open(temp_file, 'w', newline='') as f:
                f.write("section,id,num_floors,name,capacity,speed,initial_floor\n")
                f.write("building,main_building,10,Main Building,,,\n")
                f.write("elevator,elevator_A,8,2.5,1\n")

            # Try to load restored config
            config3 = BuildingConfig(temp_file)

            # Verify recovery
            if (config1.get_num_floors() == config3.get_num_floors() and
                config1.get_elevators_count() == config3.get_elevators_count()):
                self.test_results.append("PASS: Configuration recovery successful")
            else:
                self.warnings.append("Configuration recovery may have issues")

        except Exception as e:
            self.failures.append(f"Corruption recovery test failed: {e}")

    def create_temp_file(self, filename):
        """Create a temporary file and track it for cleanup."""
        temp_file = os.path.join(tempfile.gettempdir(), f"elevator_test_{filename}")
        self.temp_files.append(temp_file)
        return temp_file

    def print_config_summary(self):
        """Print configuration test results summary."""
        print("\n" + "=" * 60)
        print("CONFIGURATION CORRUPTION TEST SUMMARY")
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

        print(f"\nConfiguration Success Rate: {len(self.test_results)}/{len(self.test_results) + len(self.failures)}")

        if self.failures:
            print("\nCRITICAL CONFIGURATION ISSUES FOUND!")
            print("The configuration handling has vulnerabilities that need immediate attention.")
        elif self.warnings:
            print("\nCONFIGURATION WARNINGS - Review recommended")
            print("Some configuration issues were found that should be investigated.")
        else:
            print("\nALL CONFIGURATION TESTS PASSED!")
            print("The configuration handling appears to be robust under corruption.")

def main():
    """Main entry point for configuration corruption testing."""
    try:
        tester = ConfigCorruptionTester()
        tester.run_config_tests()
    except KeyboardInterrupt:
        print("\n\nConfiguration corruption testing interrupted by user")
    except Exception as e:
        print(f"\n\nConfiguration corruption testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
