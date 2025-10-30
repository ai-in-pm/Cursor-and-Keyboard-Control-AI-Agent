#!/usr/bin/env python3
"""
Test script for pynput integration without model dependencies.
This verifies that the enhanced cursor and keyboard control works.
"""

import sys
import os
import time
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener

class PynputTestController:
    """Test controller for pynput mouse and keyboard functionality"""
    
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.test_results = {
            'mouse_movement': False,
            'mouse_clicks': False,
            'keyboard_typing': False,
            'keyboard_special_keys': False
        }
        
    def test_mouse_movement(self):
        """Test mouse movement functionality"""
        print("Testing mouse movement...")
        try:
            # Get current position
            start_x, start_y = self.mouse_controller.position
            print(f"Starting position: ({start_x}, {start_y})")
            
            # Move to a new position
            target_x = start_x + 100
            target_y = start_y + 100
            self.mouse_controller.position = (target_x, target_y)
            time.sleep(0.5)
            
            # Check if movement worked
            new_x, new_y = self.mouse_controller.position
            print(f"New position: ({new_x}, {new_y})")
            
            # Move back
            self.mouse_controller.position = (start_x, start_y)
            
            if abs(new_x - target_x) < 10 and abs(new_y - target_y) < 10:
                self.test_results['mouse_movement'] = True
                print("✓ Mouse movement test PASSED")
            else:
                print("✗ Mouse movement test FAILED")
                
        except Exception as e:
            print(f"✗ Mouse movement test FAILED: {e}")
            
    def test_mouse_clicks(self):
        """Test mouse click functionality"""
        print("Testing mouse clicks...")
        try:
            # Test left click
            self.mouse_controller.click(Button.left, 1)
            time.sleep(0.2)
            
            # Test right click
            self.mouse_controller.click(Button.right, 1)
            time.sleep(0.2)
            
            # Test double click
            self.mouse_controller.click(Button.left, 2)
            
            self.test_results['mouse_clicks'] = True
            print("✓ Mouse clicks test PASSED")
            
        except Exception as e:
            print(f"✗ Mouse clicks test FAILED: {e}")
            
    def test_keyboard_typing(self):
        """Test keyboard typing functionality"""
        print("Testing keyboard typing...")
        try:
            # Type some text
            test_text = "Hello World"
            self.keyboard_controller.type(test_text)
            time.sleep(0.5)
            
            # Press backspace to delete it
            for _ in range(len(test_text)):
                self.keyboard_controller.press(Key.backspace)
                self.keyboard_controller.release(Key.backspace)
                time.sleep(0.05)
                
            self.test_results['keyboard_typing'] = True
            print("✓ Keyboard typing test PASSED")
            
        except Exception as e:
            print(f"✗ Keyboard typing test FAILED: {e}")
            
    def test_keyboard_special_keys(self):
        """Test keyboard special keys functionality"""
        print("Testing keyboard special keys...")
        try:
            # Test special keys
            special_keys = [Key.ctrl, Key.alt, Key.shift, Key.enter]
            
            for key in special_keys:
                self.keyboard_controller.press(key)
                time.sleep(0.1)
                self.keyboard_controller.release(key)
                time.sleep(0.1)
                
            # Test key combination (Ctrl+A)
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('a')
                self.keyboard_controller.release('a')
                
            self.test_results['keyboard_special_keys'] = True
            print("✓ Keyboard special keys test PASSED")
            
        except Exception as e:
            print(f"✗ Keyboard special keys test FAILED: {e}")
            
    def run_all_tests(self):
        """Run all pynput functionality tests"""
        print("=" * 50)
        print("PYNPUT INTEGRATION TEST")
        print("=" * 50)
        print()
        
        print("WARNING: This test will move your mouse and type on your keyboard.")
        print("Make sure you are ready for these actions.")
        print()
        
        input("Press Enter to start the tests...")
        print()
        
        # Run tests
        self.test_mouse_movement()
        time.sleep(1)
        
        self.test_mouse_clicks()
        time.sleep(1)
        
        self.test_keyboard_typing()
        time.sleep(1)
        
        self.test_keyboard_special_keys()
        time.sleep(1)
        
        # Print results
        print()
        print("=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        
        all_passed = True
        for test_name, passed in self.test_results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{test_name}: {status}")
            if not passed:
                all_passed = False
                
        print()
        if all_passed:
            print("🎉 ALL TESTS PASSED! Pynput integration is working correctly.")
        else:
            print("❌ SOME TESTS FAILED. Check the errors above.")
            
        return all_passed

class InputListenerTest:
    """Test input listener functionality"""
    
    def __init__(self):
        self.mouse_events = []
        self.keyboard_events = []
        self.running = False
        
    def on_mouse_move(self, x, y):
        """Handle mouse movement"""
        event = f"Mouse moved to ({x}, {y})"
        self.mouse_events.append(event)
        print(f"Mouse: {event}")
        
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click"""
        action = "pressed" if pressed else "released"
        event = f"Mouse {button} {action} at ({x}, {y})"
        self.mouse_events.append(event)
        print(f"Mouse: {event}")
        
    def on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll"""
        event = f"Mouse scrolled at ({x}, {y}) - dx: {dx}, dy: {dy}"
        self.mouse_events.append(event)
        print(f"Mouse: {event}")
        
    def on_key_press(self, key):
        """Handle key press"""
        try:
            key_str = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_str = str(key)
            
        event = f"Key pressed: {key_str}"
        self.keyboard_events.append(event)
        print(f"Keyboard: {event}")
        
    def on_key_release(self, key):
        """Handle key release"""
        try:
            key_str = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_str = str(key)
            
        event = f"Key released: {key_str}"
        self.keyboard_events.append(event)
        print(f"Keyboard: {event}")
        
    def start_listening(self, duration=10):
        """Start listening for input events"""
        print(f"\nStarting input listener test for {duration} seconds...")
        print("Move your mouse, click buttons, and type on your keyboard.")
        print("Press 'Esc' key to stop early.")
        print()
        
        self.running = True
        self.mouse_events = []
        self.keyboard_events = []
        
        # Start listeners
        mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        
        keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        mouse_listener.start()
        keyboard_listener.start()
        
        # Listen for duration or until Esc is pressed
        start_time = time.time()
        while self.running and (time.time() - start_time) < duration:
            time.sleep(0.1)
            
        # Stop listeners
        mouse_listener.stop()
        keyboard_listener.stop()
        
        print(f"\nInput listener test completed.")
        print(f"Mouse events captured: {len(self.mouse_events)}")
        print(f"Keyboard events captured: {len(self.keyboard_events)}")
        
        return len(self.mouse_events) > 0 or len(self.keyboard_events) > 0

def main():
    """Main test function"""
    print("Pynput Integration Test Suite")
    print("This will test mouse and keyboard control capabilities.")
    print()
    
    # Test 1: Controller functionality
    print("TEST 1: Controller Functionality")
    controller_test = PynputTestController()
    controller_passed = controller_test.run_all_tests()
    
    if controller_passed:
        print("\n" + "="*50)
        print("TEST 2: Input Listener Functionality")
        print("="*50)
        
        # Test 2: Input listener functionality
        listener_test = InputListenerTest()
        listener_passed = listener_test.start_listening(duration=5)
        
        if listener_passed:
            print("✓ Input listener test PASSED")
        else:
            print("✗ Input listener test FAILED - no events captured")
    else:
        print("\nSkipping input listener test due to controller failures.")
        
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    if controller_passed:
        print("✓ Pynput integration is working correctly!")
        print("✓ Enhanced cursor and keyboard control is ready for use.")
    else:
        print("❌ Pynput integration has issues that need to be resolved.")
        
    print("\nYou can now use the enhanced agent with pynput for advanced control.")

if __name__ == "__main__":
    main()