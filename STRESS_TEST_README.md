# Elevator Simulation Stress Testing Guide

This directory contains comprehensive stress testing scripts designed to break the elevator simulation application and identify potential vulnerabilities, bugs, and edge cases.

## 🚨 Warning

**These tests are designed to be destructive and may cause:**
- Application crashes
- Memory leaks
- System resource exhaustion
- Data corruption
- Unstable behavior

**Only run these tests in a development/testing environment, never in production!**

## 📋 Available Test Scripts

### 1. `stress_test.py` - Main Comprehensive Stress Tester
The primary stress testing script that covers all major areas:

- **Invalid Configurations**: Tests negative values, zero values, invalid ranges
- **Boundary Conditions**: Tests extreme values and edge cases
- **Invalid Inputs**: Tests None values, wrong types, malformed data
- **Race Conditions**: Tests concurrent operations and threading issues
- **Memory & Performance**: Tests under heavy load and memory pressure
- **GUI Stress**: Tests rapid UI updates and button interactions
- **Data Corruption**: Tests corrupted internal state handling
- **Exception Handling**: Tests error recovery and prevention
- **Resource Exhaustion**: Tests memory and thread limits
- **Integration Stress**: Tests full system under load

### 2. `gui_stress_test.py` - GUI-Specific Stress Tester
Focused on breaking the user interface components:

- **Rapid UI Updates**: Tests freezing under rapid metric updates
- **Memory Leaks**: Tests Tkinter memory management
- **Button States**: Tests button corruption under stress
- **Layout Breaking**: Tests UI layout stability
- **Event Queue**: Tests event handling overflow
- **Concurrent GUI**: Tests multi-threaded UI operations
- **Invalid Inputs**: Tests malformed GUI inputs
- **Resource Exhaustion**: Tests window creation limits

### 3. `config_corruption_test.py` - Configuration File Corruption Tester
Tests how the application handles corrupted configuration files:

- **Malformed CSV**: Tests broken CSV structure
- **Invalid Data Types**: Tests wrong data types in fields
- **Missing Fields**: Tests required field validation
- **File Corruption**: Tests binary corruption and encoding issues
- **Permissions**: Tests file access permission handling
- **File System Errors**: Tests various file system scenarios
- **Large Files**: Tests performance with huge configurations
- **Unicode/Special Chars**: Tests character encoding issues
- **Concurrent Access**: Tests file access race conditions
- **Recovery**: Tests corruption recovery mechanisms

## 🚀 Running the Tests

### Prerequisites
```bash
# Install required dependencies
pip install psutil  # For memory monitoring (optional)
```

### Basic Usage

#### Run All Tests
```bash
# Run the main comprehensive stress test
python stress_test.py

# Run GUI-specific stress tests
python gui_stress_test.py

# Run configuration corruption tests
python config_corruption_test.py
```

#### Run Specific Test Categories
```bash
# You can modify the scripts to run only specific test categories
# by commenting out unwanted test methods in the run_all_tests() function
```

### Expected Output
```
🚀 Starting Elevator Simulation Stress Tests...
============================================================

🔧 Testing Invalid Configurations...
✓ Negative floors properly rejected
✓ Zero floors properly rejected
✓ Single floor properly rejected
...

📊 STRESS TEST SUMMARY
============================================================

✅ Tests Passed: 45
❌ Failures: 3
⚠️ Warnings: 2

🎯 Success Rate: 45/48

🚨 CRITICAL ISSUES FOUND!
The application has vulnerabilities that need immediate attention.
```

## 🎯 What These Tests Look For

### Critical Issues (Failures)
- **Application crashes** under stress
- **Data corruption** from invalid inputs
- **Security vulnerabilities** from malformed data
- **Resource leaks** that could cause system instability
- **Race conditions** that lead to inconsistent state

### Performance Issues (Warnings)
- **Memory leaks** over time
- **Slow performance** under load
- **UI freezing** during rapid updates
- **Resource exhaustion** with large inputs
- **Poor error recovery** from corruption

### Robustness Indicators (Passes)
- **Graceful degradation** under stress
- **Proper validation** of inputs
- **Error handling** without crashes
- **Resource cleanup** after failures
- **Consistent behavior** under load

## 🔍 Interpreting Results

### Green (✓) - Good
- Application handled the stress gracefully
- Proper error handling and validation
- No crashes or data corruption
- Good performance under load

### Yellow (⚠️) - Warning
- Application worked but with issues
- Performance degradation under stress
- Potential memory leaks or resource issues
- Should be investigated but not critical

### Red (❌) - Critical
- Application crashed or failed completely
- Data corruption or loss
- Security vulnerabilities exposed
- Resource exhaustion or system instability
- **Requires immediate attention**

## 🛠️ Customizing Tests

### Adding New Test Cases
```python
def test_new_scenario(self):
    """Test a new edge case."""
    try:
        # Your test logic here
        result = some_operation()
        if result == expected:
            self.test_results.append("✓ New scenario handled correctly")
        else:
            self.failures.append("New scenario failed")
    except Exception as e:
        self.test_results.append(f"✓ New scenario properly handled: {e}")
```

### Modifying Test Parameters
```python
# Adjust test intensity
for i in range(1000):  # Increase from 1000 to 10000 for more stress
    # Test logic

# Adjust memory thresholds
if memory_mb > 100:  # Change from 100MB to 50MB for stricter testing
    self.warnings.append(f"High memory usage: {memory_mb:.1f}MB")
```

### Skipping Specific Tests
```python
def run_all_tests(self):
    """Run all stress tests."""
    # Comment out tests you want to skip
    # self.test_memory_performance()  # Skip memory tests
    self.test_gui_stress()  # Keep GUI tests
    # self.test_race_conditions()     # Skip race condition tests
```

## 📊 Monitoring During Tests

### System Resources
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep stress'

# Monitor CPU usage
htop

# Monitor file system
iotop
```

### Application Logs
```bash
# Check application logs for errors
tail -f elevator_simulation.log

# Check system logs for crashes
dmesg | tail -20
```

## 🚨 Common Issues and Solutions

### Application Crashes
- **Symptom**: Script stops with error or system becomes unresponsive
- **Solution**: Check logs, reduce test intensity, add more error handling

### Memory Exhaustion
- **Symptom**: System becomes slow, out of memory errors
- **Solution**: Reduce test scale, add memory monitoring, implement cleanup

### GUI Freezing
- **Symptom**: UI becomes unresponsive during tests
- **Solution**: Add delays between operations, reduce concurrent operations

### File System Issues
- **Symptom**: Permission errors, corrupted files
- **Solution**: Check file permissions, ensure proper cleanup, use temp directories

## 🔧 Debugging Failed Tests

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Add Debug Output
```python
def test_something(self):
    try:
        print(f"Testing with parameters: {params}")
        result = operation(params)
        print(f"Result: {result}")
        # ... rest of test
    except Exception as e:
        print(f"Exception details: {e}")
        import traceback
        traceback.print_exc()
```

### Isolate Test Cases
```python
# Run only one test method
if __name__ == "__main__":
    tester = ElevatorStressTester()
    tester.test_specific_method()  # Run only one test
```

## 📈 Performance Benchmarks

### Baseline Performance
- **Small building (10 floors, 2 elevators)**: < 1 second to load
- **Medium building (50 floors, 5 elevators)**: < 3 seconds to load
- **Large building (100 floors, 10 elevators)**: < 10 seconds to load

### Memory Usage
- **Normal operation**: < 50MB
- **Heavy load**: < 200MB
- **Stress testing**: < 500MB (temporary)

### Response Time
- **UI updates**: < 100ms
- **Elevator operations**: < 50ms
- **Configuration loading**: < 1 second

## 🎯 Best Practices

### Test Environment
- Use dedicated testing machine
- Monitor system resources
- Have recovery procedures ready
- Test during off-peak hours

### Test Execution
- Start with small tests
- Gradually increase intensity
- Monitor for system instability
- Stop tests if system becomes unstable

### Result Analysis
- Document all failures
- Prioritize critical issues
- Track performance regressions
- Validate fixes with regression tests

## 🤝 Contributing

### Adding New Test Scenarios
1. Identify a potential vulnerability or edge case
2. Create a test method in the appropriate test class
3. Follow the existing test pattern and naming conventions
4. Add proper error handling and cleanup
5. Document the test purpose and expected behavior

### Improving Existing Tests
1. Add more comprehensive error checking
2. Improve performance monitoring
3. Add cleanup procedures
4. Enhance result reporting
5. Add configuration options

## 📚 Additional Resources

- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Stress Testing Methodologies](https://en.wikipedia.org/wiki/Stress_testing)
- [Memory Leak Detection](https://docs.python.org/3/library/tracemalloc.html)
- [Performance Profiling](https://docs.python.org/3/library/profile.html)

## 📞 Support

If you encounter issues with these stress tests:

1. Check the application logs for errors
2. Verify system resources are adequate
3. Reduce test intensity and try again
4. Report bugs with detailed error messages
5. Include system specifications and test parameters

---

**Remember: These tests are designed to break things! Use them responsibly and only in appropriate testing environments.**
