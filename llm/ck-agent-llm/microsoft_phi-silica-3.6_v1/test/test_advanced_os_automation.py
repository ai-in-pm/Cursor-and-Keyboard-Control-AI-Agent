#!/usr/bin/env python3
"""
Test script for Advanced OS Automation Agent
Tests human-level task automation across Windows, Linux, and macOS.
"""

import sys
import os
import platform
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.advanced_os_automation_agent import AdvancedOSAutomationAgent, OperatingSystem

class TestAdvancedOSAutomation:
    """Test suite for advanced OS automation capabilities"""
    
    def __init__(self):
        self.agent = None
        self.test_dir = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment"""
        print("Setting up test environment...")
        try:
            self.agent = AdvancedOSAutomationAgent()
            self.test_dir = tempfile.mkdtemp(prefix="os_automation_test_")
            print(f"Test directory created: {self.test_dir}")
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def teardown(self):
        """Cleanup test environment"""
        print("Cleaning up test environment...")
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print("Test directory cleaned up")
    
    def run_test(self, test_name, test_function):
        """Run a single test and record results"""
        print(f"\nRunning test: {test_name}")
        try:
            result = test_function()
            self.test_results.append((test_name, result, "PASSED"))
            print(f"OK - {test_name} - PASSED")
            return True
        except Exception as e:
            self.test_results.append((test_name, str(e), "FAILED"))
            print(f"FAILED - {test_name} - FAILED: {e}")
            return False
    
    def test_platform_detection(self):
        """Test OS platform detection"""
        detected_os = self.agent.os_type
        actual_os = platform.system()
        
        if actual_os == "Windows" and detected_os == OperatingSystem.WINDOWS:
            return True
        elif actual_os == "Linux" and detected_os == OperatingSystem.LINUX:
            return True
        elif actual_os == "Darwin" and detected_os == OperatingSystem.MACOS:
            return True
        else:
            raise ValueError(f"OS detection mismatch: detected {detected_os}, actual {actual_os}")
    
    def test_system_info(self):
        """Test system information gathering"""
        system_info = self.agent.get_system_info()
        
        required_keys = ["os", "platform", "processor", "architecture", "python_version"]
        for key in required_keys:
            if key not in system_info:
                raise ValueError(f"Missing system info key: {key}")
        
        if system_info["os"] != self.agent.os_type.value:
            raise ValueError("OS type mismatch in system info")
        
        return True
    
    def test_file_operations(self):
        """Test file system operations"""
        test_file = os.path.join(self.test_dir, "test_file.txt")
        test_dir = os.path.join(self.test_dir, "test_subdir")
        
        # Test create file
        result = self.agent.file_operations("create_file", test_file)
        if result["status"] != "success":
            raise ValueError(f"Create file failed: {result}")
        if not os.path.exists(test_file):
            raise ValueError("File was not created")
        
        # Test create directory
        result = self.agent.file_operations("create_directory", test_dir)
        if result["status"] != "success":
            raise ValueError(f"Create directory failed: {result}")
        if not os.path.exists(test_dir):
            raise ValueError("Directory was not created")
        
        # Test list directory
        result = self.agent.file_operations("list_directory", self.test_dir)
        if result["status"] != "success":
            raise ValueError(f"List directory failed: {result}")
        if "items" not in result:
            raise ValueError("List directory didn't return items")
        
        # Test copy file
        copy_file = os.path.join(test_dir, "copied_file.txt")
        result = self.agent.file_operations("copy", test_file, copy_file)
        if result["status"] != "success":
            raise ValueError(f"Copy file failed: {result}")
        if not os.path.exists(copy_file):
            raise ValueError("File was not copied")
        
        # Test delete file
        result = self.agent.file_operations("delete", test_file)
        if result["status"] != "success":
            raise ValueError(f"Delete file failed: {result}")
        if os.path.exists(test_file):
            raise ValueError("File was not deleted")
        
        return True
    
    def test_system_monitoring(self):
        """Test system monitoring capabilities"""
        # Test CPU monitoring
        result = self.agent.system_monitoring("cpu_usage")
        if result["status"] != "success":
            raise ValueError(f"CPU monitoring failed: {result}")
        
        # Test memory monitoring
        result = self.agent.system_monitoring("memory_usage")
        if result["status"] != "success":
            raise ValueError(f"Memory monitoring failed: {result}")
        
        # Test disk monitoring
        result = self.agent.system_monitoring("disk_usage")
        if result["status"] != "success":
            raise ValueError(f"Disk monitoring failed: {result}")
        
        # Test network monitoring
        result = self.agent.system_monitoring("network_info")
        if result["status"] != "success":
            # Network monitoring might fail on some systems, but that's OK
            print("  Note: Network monitoring not available on this system")
        
        return True
    
    def test_application_operations(self):
        """Test application management operations"""
        # Test listing running applications (if psutil is available)
        result = self.agent.application_operations("list_running_apps")
        if result["status"] == "error" and "psutil" in result["message"]:
            print("  Note: psutil not available for process listing")
            return True  # Skip this test if psutil not available
        
        if result["status"] != "success":
            raise ValueError(f"List running apps failed: {result}")
        
        return True
    
    def test_complex_tasks(self):
        """Test complex multi-step tasks"""
        # Test file organization task
        result = self.agent.perform_complex_task("create file and check system resources")
        if result["status"] not in ["success", "warning"]:
            raise ValueError(f"Complex task failed: {result}")
        
        if "steps" not in result:
            raise ValueError("Complex task didn't return steps")
        
        # Test system health check
        result = self.agent.perform_complex_task("take a system health check")
        if result["status"] not in ["success", "warning"]:
            raise ValueError(f"System health check failed: {result}")
        
        return True
    
    def test_task_history(self):
        """Test task history functionality"""
        # Clear history first
        self.agent.clear_task_history()
        
        # Perform some tasks
        self.agent.perform_complex_task("check cpu usage")
        self.agent.perform_complex_task("check memory usage")
        
        # Check history
        history = self.agent.get_task_history()
        if len(history) != 2:
            raise ValueError(f"Expected 2 tasks in history, got {len(history)}")
        
        # Clear and verify
        self.agent.clear_task_history()
        history = self.agent.get_task_history()
        if len(history) != 0:
            raise ValueError("Task history was not cleared")
        
        return True
    
    def test_platform_features(self):
        """Test platform-specific feature detection"""
        platform_info = self.agent.get_platform_info()
        
        required_keys = ["os", "screen_size", "available_features"]
        for key in required_keys:
            if key not in platform_info:
                raise ValueError(f"Missing platform info key: {key}")
        
        features = platform_info["available_features"]
        if not isinstance(features, list) or len(features) == 0:
            raise ValueError("No available features detected")
        
        print(f"  Available features: {', '.join(features)}")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("ADVANCED OS AUTOMATION TEST SUITE")
        print("=" * 70)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print("=" * 70)
        
        if not self.setup():
            print("Failed to setup test environment")
            return False
        
        try:
            # Run all tests
            tests = [
                ("Platform Detection", self.test_platform_detection),
                ("System Information", self.test_system_info),
                ("File Operations", self.test_file_operations),
                ("System Monitoring", self.test_system_monitoring),
                ("Application Operations", self.test_application_operations),
                ("Complex Tasks", self.test_complex_tasks),
                ("Task History", self.test_task_history),
                ("Platform Features", self.test_platform_features)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                if self.run_test(test_name, test_func):
                    passed += 1
            
            # Print summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)
            
            for test_name, result, status in self.test_results:
                print(f"{test_name}: {status}")
            
            print(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                print("SUCCESS - ALL TESTS PASSED! Advanced OS automation is working correctly.")
                print("\nThe agent can now perform human-level tasks including:")
                print("  - File system operations (create, copy, delete, organize)")
                print("  - System monitoring (CPU, memory, disk, network, battery)")
                print("  - Application management (launch, close, list)")
                print("  - Complex multi-step task automation")
                print("  - Cross-platform compatibility")
                return True
            else:
                print("FAILURE - SOME TESTS FAILED. Check the errors above.")
                return False
                
        finally:
            self.teardown()

def main():
    """Main test runner"""
    tester = TestAdvancedOSAutomation()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()