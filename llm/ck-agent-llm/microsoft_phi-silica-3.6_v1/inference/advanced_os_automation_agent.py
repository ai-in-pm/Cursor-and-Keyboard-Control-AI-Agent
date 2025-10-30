#!/usr/bin/env python3
"""
Advanced OS Automation Agent for Windows, Linux, and macOS
Performs human-level system tasks across all major operating systems.
"""

import os
import sys
import platform
import time
import logging
import subprocess
import threading
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from enum import Enum

# Platform-specific imports with fallbacks
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    from pynput.keyboard import Key
except ImportError:
    mouse = keyboard = Button = Key = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    webdriver = By = Keys = WebDriverWait = EC = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "Darwin"

class ApplicationType(Enum):
    BROWSER = "browser"
    TEXT_EDITOR = "text_editor"
    TERMINAL = "terminal"
    FILE_MANAGER = "file_manager"
    MEDIA_PLAYER = "media_player"
    OFFICE_SUITE = "office_suite"

class AdvancedOSAutomationAgent:
    """Advanced agent for performing human-level OS tasks across Windows, Linux, and macOS"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.screen_width, self.screen_height = self._get_screen_size()
        self.current_app = None
        self.system_info = self._get_system_info()
        self.task_history = []
        
        # Initialize platform-specific controllers
        self._init_platform_controllers()
        
        logger.info(f"Initialized Advanced OS Automation Agent for {self.os_type.value}")
        logger.info(f"Screen size: {self.screen_width}x{self.screen_height}")
        logger.info(f"System info: {self.system_info}")
    
    def _detect_os(self) -> OperatingSystem:
        """Detect the current operating system"""
        system = platform.system()
        if system == "Windows":
            return OperatingSystem.WINDOWS
        elif system == "Linux":
            return OperatingSystem.LINUX
        elif system == "Darwin":
            return OperatingSystem.MACOS
        else:
            raise NotImplementedError(f"Unsupported operating system: {system}")
    
    def _get_screen_size(self):
        """Get screen size with platform-specific methods"""
        try:
            if pyautogui:
                return pyautogui.size()
            else:
                # Fallback screen sizes
                return 1920, 1080
        except:
            return 1920, 1080
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        info = {
            "os": self.os_type.value,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version()
        }
        
        if psutil:
            info.update({
                "cpu_cores": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_usage": {partition.device: psutil.disk_usage(partition.mountpoint)._asdict() 
                              for partition in psutil.disk_partitions()}
            })
        
        return info
    
    def _init_platform_controllers(self):
        """Initialize platform-specific automation controllers"""
        if self.os_type == OperatingSystem.WINDOWS:
            self._init_windows_controllers()
        elif self.os_type == OperatingSystem.LINUX:
            self._init_linux_controllers()
        elif self.os_type == OperatingSystem.MACOS:
            self._init_macos_controllers()
    
    def _init_windows_controllers(self):
        """Initialize Windows-specific automation controllers"""
        try:
            import win32gui
            import win32con
            import win32api
            self.win32gui = win32gui
            self.win32con = win32con
            self.win32api = win32api
        except ImportError:
            logger.warning("pywin32 not available - some Windows features disabled")
            self.win32gui = self.win32con = self.win32api = None
    
    def _init_linux_controllers(self):
        """Initialize Linux-specific automation controllers"""
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, Gdk
            self.gtk = Gtk
            self.gdk = Gdk
        except ImportError:
            logger.warning("GTK not available - some Linux features disabled")
            self.gtk = self.gdk = None
    
    def _init_macos_controllers(self):
        """Initialize macOS-specific automation controllers"""
        try:
            from AppKit import NSWorkspace, NSScreen
            self.nsworkspace = NSWorkspace
            self.nsscreen = NSScreen
        except ImportError:
            logger.warning("AppKit not available - some macOS features disabled")
            self.nsworkspace = self.nsscreen = None

    # File System Operations
    def file_operations(self, operation: str, source: str, destination: str = None) -> Dict[str, Any]:
        """Perform file system operations"""
        try:
            source_path = Path(source)
            
            if operation == "create_file":
                source_path.touch()
                return {"status": "success", "message": f"Created file: {source}"}
            
            elif operation == "create_directory":
                source_path.mkdir(parents=True, exist_ok=True)
                return {"status": "success", "message": f"Created directory: {source}"}
            
            elif operation == "delete":
                if source_path.is_file():
                    source_path.unlink()
                    return {"status": "success", "message": f"Deleted file: {source}"}
                elif source_path.is_dir():
                    import shutil
                    shutil.rmtree(source_path)
                    return {"status": "success", "message": f"Deleted directory: {source}"}
            
            elif operation == "copy" and destination:
                dest_path = Path(destination)
                if source_path.is_file():
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    return {"status": "success", "message": f"Copied {source} to {destination}"}
                elif source_path.is_dir():
                    import shutil
                    shutil.copytree(source_path, dest_path)
                    return {"status": "success", "message": f"Copied directory {source} to {destination}"}
            
            elif operation == "move" and destination:
                source_path.rename(destination)
                return {"status": "success", "message": f"Moved {source} to {destination}"}
            
            elif operation == "list_directory":
                items = list(source_path.iterdir())
                return {
                    "status": "success", 
                    "items": [{"name": item.name, "type": "file" if item.is_file() else "directory"} 
                             for item in items]
                }
            
            else:
                return {"status": "error", "message": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Window Management
    def window_operations(self, operation: str, window_title: str = None) -> Dict[str, Any]:
        """Perform window management operations"""
        try:
            if self.os_type == OperatingSystem.WINDOWS and self.win32gui:
                return self._windows_window_operations(operation, window_title)
            elif self.os_type == OperatingSystem.LINUX:
                return self._linux_window_operations(operation, window_title)
            elif self.os_type == OperatingSystem.MACOS and self.nsworkspace:
                return self._macos_window_operations(operation, window_title)
            else:
                return {"status": "error", "message": "Window management not available on this platform"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _windows_window_operations(self, operation: str, window_title: str) -> Dict[str, Any]:
        """Windows-specific window operations"""
        if operation == "get_active_window":
            hwnd = self.win32gui.GetForegroundWindow()
            title = self.win32gui.GetWindowText(hwnd)
            return {"status": "success", "window_title": title, "hwnd": hwnd}
        
        elif operation == "minimize_window" and window_title:
            hwnd = self._find_window_by_title(window_title)
            if hwnd:
                self.win32gui.ShowWindow(hwnd, self.win32con.SW_MINIMIZE)
                return {"status": "success", "message": f"Minimized window: {window_title}"}
        
        elif operation == "maximize_window" and window_title:
            hwnd = self._find_window_by_title(window_title)
            if hwnd:
                self.win32gui.ShowWindow(hwnd, self.win32con.SW_MAXIMIZE)
                return {"status": "success", "message": f"Maximized window: {window_title}"}
        
        return {"status": "error", "message": f"Operation not supported: {operation}"}
    
    def _find_window_by_title(self, title: str):
        """Find window by title on Windows"""
        def callback(hwnd, windows):
            if self.win32gui.IsWindowVisible(hwnd) and title in self.win32gui.GetWindowText(hwnd):
                windows.append(hwnd)
        
        windows = []
        self.win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    
    def _linux_window_operations(self, operation: str, window_title: str) -> Dict[str, Any]:
        """Linux-specific window operations using wmctrl"""
        try:
            if operation == "get_active_window":
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
                return {"status": "success", "windows": result.stdout}
            else:
                return {"status": "error", "message": "Linux window operations require wmctrl"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _macos_window_operations(self, operation: str, window_title: str) -> Dict[str, Any]:
        """macOS-specific window operations"""
        if operation == "get_active_window":
            app = self.nsworkspace.sharedWorkspace().frontmostApplication()
            return {"status": "success", "app_name": app.localizedName()}
        else:
            return {"status": "error", "message": "macOS window operations limited"}

    # Application Management
    def application_operations(self, operation: str, app_name: str = None, app_path: str = None) -> Dict[str, Any]:
        """Manage applications - launch, close, etc."""
        try:
            if operation == "launch":
                if app_path:
                    subprocess.Popen([app_path])
                elif app_name:
                    if self.os_type == OperatingSystem.WINDOWS:
                        subprocess.Popen([app_name])
                    elif self.os_type == OperatingSystem.LINUX:
                        subprocess.Popen([app_name])
                    elif self.os_type == OperatingSystem.MACOS:
                        subprocess.Popen(['open', '-a', app_name])
                return {"status": "success", "message": f"Launched application: {app_name or app_path}"}
            
            elif operation == "close" and app_name:
                if self.os_type == OperatingSystem.WINDOWS:
                    subprocess.run(['taskkill', '/IM', app_name], capture_output=True)
                elif self.os_type == OperatingSystem.LINUX:
                    subprocess.run(['pkill', app_name], capture_output=True)
                elif self.os_type == OperatingSystem.MACOS:
                    subprocess.run(['pkill', app_name], capture_output=True)
                return {"status": "success", "message": f"Closed application: {app_name}"}
            
            elif operation == "list_running_apps":
                if psutil:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'status']):
                        processes.append(proc.info)
                    return {"status": "success", "processes": processes}
                else:
                    return {"status": "error", "message": "psutil required for process listing"}
            
            else:
                return {"status": "error", "message": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Web Browser Automation
    def browser_operations(self, operation: str, url: str = None, element: str = None, text: str = None) -> Dict[str, Any]:
        """Perform web browser automation"""
        try:
            if not webdriver:
                return {"status": "error", "message": "Selenium not available for browser automation"}
            
            if operation == "open_url" and url:
                # Initialize browser (using Chrome as default)
                options = webdriver.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                self.browser = webdriver.Chrome(options=options)
                self.browser.get(url)
                return {"status": "success", "message": f"Opened URL: {url}"}
            
            elif operation == "click_element" and element:
                if hasattr(self, 'browser'):
                    element_obj = self.browser.find_element(By.CSS_SELECTOR, element)
                    element_obj.click()
                    return {"status": "success", "message": f"Clicked element: {element}"}
            
            elif operation == "type_text" and element and text:
                if hasattr(self, 'browser'):
                    element_obj = self.browser.find_element(By.CSS_SELECTOR, element)
                    element_obj.send_keys(text)
                    return {"status": "success", "message": f"Typed text in element: {element}"}
            
            elif operation == "close_browser":
                if hasattr(self, 'browser'):
                    self.browser.quit()
                    return {"status": "success", "message": "Closed browser"}
            
            else:
                return {"status": "error", "message": f"Unknown browser operation: {operation}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # System Information and Monitoring
    def system_monitoring(self, operation: str) -> Dict[str, Any]:
        """Monitor system resources and status"""
        try:
            if not psutil:
                return {"status": "error", "message": "psutil required for system monitoring"}
            
            if operation == "cpu_usage":
                usage = psutil.cpu_percent(interval=1)
                return {"status": "success", "cpu_usage_percent": usage}
            
            elif operation == "memory_usage":
                memory = psutil.virtual_memory()
                return {
                    "status": "success",
                    "memory_used_gb": round(memory.used / (1024**3), 2),
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "memory_percent": memory.percent
                }
            
            elif operation == "disk_usage":
                disk = psutil.disk_usage('/')
                return {
                    "status": "success",
                    "disk_used_gb": round(disk.used / (1024**3), 2),
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "disk_percent": disk.percent
                }
            
            elif operation == "battery_status":
                battery = psutil.sensors_battery()
                if battery:
                    return {
                        "status": "success",
                        "battery_percent": round(battery.percent, 2),
                        "power_plugged": battery.power_plugged,
                        "time_remaining": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited"
                    }
                else:
                    return {"status": "error", "message": "Battery information not available"}
            
            elif operation == "network_info":
                net_io = psutil.net_io_counters()
                return {
                    "status": "success",
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_received": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_received": net_io.packets_recv
                }
            
            else:
                return {"status": "error", "message": f"Unknown monitoring operation: {operation}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Advanced Task Automation
    def perform_complex_task(self, task_description: str) -> Dict[str, Any]:
        """Perform complex multi-step tasks based on natural language description"""
        try:
            task_lower = task_description.lower()
            result = {"status": "success", "steps": [], "task": task_description}
            
            # File management tasks
            if "create file" in task_lower:
                filename = "new_file.txt"  # Extract from description in real implementation
                file_result = self.file_operations("create_file", filename)
                result["steps"].append({"action": "create_file", "result": file_result})
            
            elif "list directory" in task_lower or "list folder" in task_lower:
                dir_result = self.file_operations("list_directory", ".")
                result["steps"].append({"action": "list_directory", "result": dir_result})
            
            # System monitoring tasks
            elif "check cpu" in task_lower or "cpu usage" in task_lower:
                cpu_result = self.system_monitoring("cpu_usage")
                result["steps"].append({"action": "check_cpu", "result": cpu_result})
            
            elif "check memory" in task_lower or "memory usage" in task_lower:
                memory_result = self.system_monitoring("memory_usage")
                result["steps"].append({"action": "check_memory", "result": memory_result})
            
            # Application tasks
            elif "open browser" in task_lower:
                browser_result = self.browser_operations("open_url", "https://www.google.com")
                result["steps"].append({"action": "open_browser", "result": browser_result})
            
            else:
                result["status"] = "warning"
                result["message"] = f"Task pattern not recognized: {task_description}"
            
            # Add to task history
            self.task_history.append(result)
            
            return result
            
        except Exception as e:
            error_result = {"status": "error", "message": str(e), "task": task_description}
            self.task_history.append(error_result)
            return error_result

    # Utility Methods
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get history of performed tasks"""
        return self.task_history
    
    def clear_task_history(self):
        """Clear task history"""
        self.task_history.clear()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return self.system_info
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform-specific information"""
        return {
            "os": self.os_type.value,
            "screen_size": f"{self.screen_width}x{self.screen_height}",
            "available_features": self._get_available_features()
        }
    
    def _get_available_features(self) -> List[str]:
        """Get list of available automation features"""
        features = ["file_operations", "system_monitoring", "application_management"]
        
        if webdriver:
            features.append("browser_automation")
        
        if self.os_type == OperatingSystem.WINDOWS and self.win32gui:
            features.append("window_management")
        
        if psutil:
            features.extend(["process_management", "system_metrics"])
        
        return features

def main():
    """Main function to demonstrate advanced OS automation"""
    print("Advanced OS Automation Agent")
    print("=" * 50)
    
    try:
        agent = AdvancedOSAutomationAgent()
        
        # Display system information
        print(f"Operating System: {agent.os_type.value}")
        print(f"Screen Size: {agent.screen_width}x{agent.screen_height}")
        print(f"Available Features: {', '.join(agent._get_available_features())}")
        print()
        
        # Demonstrate file operations
        print("1. File Operations Demo:")
        result = agent.file_operations("create_file", "test_file.txt")
        print(f"   Create file: {result}")
        
        result = agent.file_operations("list_directory", ".")
        print(f"   List directory: {len(result.get('items', []))} items")
        print()
        
        # Demonstrate system monitoring
        print("2. System Monitoring Demo:")
        result = agent.system_monitoring("cpu_usage")
        print(f"   CPU Usage: {result.get('cpu_usage_percent', 'N/A')}%")
        
        result = agent.system_monitoring("memory_usage")
        print(f"   Memory Usage: {result.get('memory_percent', 'N/A')}%")
        print()
        
        # Demonstrate complex task
        print("3. Complex Task Demo:")
        result = agent.perform_complex_task("create file and check system resources")
        print(f"   Complex task result: {result['status']}")
        print(f"   Steps performed: {len(result.get('steps', []))}")
        print()
        
        # Show task history
        print("4. Task History:")
        for i, task in enumerate(agent.get_task_history(), 1):
            print(f"   {i}. {task.get('task', 'Unknown')} - {task.get('status', 'Unknown')}")
        
        print("\nAdvanced OS Automation Agent is ready for human-level tasks!")
        
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Some features may be limited due to missing dependencies.")

if __name__ == "__main__":
    main()