#!/usr/bin/env python3
"""
Simple non-interactive test for pynput integration.
This verifies basic functionality without moving the mouse or typing.
"""

import sys
import os
import time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

def test_pynput_imports():
    """Test that pynput modules can be imported"""
    print("Testing pynput imports...")
    try:
        from pynput import mouse, keyboard
        from pynput.mouse import Button, Listener as MouseListener
        from pynput.keyboard import Key, Listener as KeyboardListener
        print("✓ All pynput imports successful")
        return True
    except ImportError as e:
        print(f"✗ Pynput import failed: {e}")
        return False

def test_mouse_controller():
    """Test mouse controller creation"""
    print("Testing mouse controller...")
    try:
        mouse_ctrl = mouse.Controller()
        current_pos = mouse_ctrl.position
        print(f"✓ Mouse controller created - current position: {current_pos}")
        return True
    except Exception as e:
        print(f"✗ Mouse controller test failed: {e}")
        return False

def test_keyboard_controller():
    """Test keyboard controller creation"""
    print("Testing keyboard controller...")
    try:
        keyboard_ctrl = keyboard.Controller()
        print("✓ Keyboard controller created")
        return True
    except Exception as e:
        print(f"✗ Keyboard controller test failed: {e}")
        return False

def test_special_keys():
    """Test special key mapping"""
    print("Testing special key mapping...")
    try:
        # Test key conversion
        special_keys = {
            'ctrl': Key.ctrl,
            'shift': Key.shift,
            'alt': Key.alt,
            'enter': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'esc': Key.esc
        }
        
        for key_name, key_obj in special_keys.items():
            if key_obj is not None:
                print(f"  ✓ {key_name} -> {key_obj}")
            else:
                print(f"  ✗ {key_name} mapping failed")
                return False
                
        print("✓ All special key mappings successful")
        return True
    except Exception as e:
        print(f"✗ Special key test failed: {e}")
        return False

def test_mouse_buttons():
    """Test mouse button mapping"""
    print("Testing mouse button mapping...")
    try:
        buttons = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        
        for button_name, button_obj in buttons.items():
            if button_obj is not None:
                print(f"  ✓ {button_name} -> {button_obj}")
            else:
                print(f"  ✗ {button_name} mapping failed")
                return False
                
        print("✓ All mouse button mappings successful")
        return True
    except Exception as e:
        print(f"✗ Mouse button test failed: {e}")
        return False

def test_listener_creation():
    """Test listener creation without starting"""
    print("Testing listener creation...")
    try:
        # Test mouse listener creation
        def dummy_mouse_move(x, y):
            pass
            
        def dummy_mouse_click(x, y, button, pressed):
            pass
            
        def dummy_mouse_scroll(x, y, dx, dy):
            pass
            
        mouse_listener = mouse.Listener(
            on_move=dummy_mouse_move,
            on_click=dummy_mouse_click,
            on_scroll=dummy_mouse_scroll
        )
        
        # Test keyboard listener creation
        def dummy_key_press(key):
            pass
            
        def dummy_key_release(key):
            pass
            
        keyboard_listener = keyboard.Listener(
            on_press=dummy_key_press,
            on_release=dummy_key_release
        )
        
        print("✓ Both mouse and keyboard listeners created successfully")
        return True
    except Exception as e:
        print(f"✗ Listener creation test failed: {e}")
        return False

def main():
    """Run all non-interactive tests"""
    print("=" * 60)
    print("PYNPUT INTEGRATION TEST (Non-Interactive)")
    print("=" * 60)
    print()
    
    tests = [
        test_pynput_imports,
        test_mouse_controller,
        test_keyboard_controller,
        test_special_keys,
        test_mouse_buttons,
        test_listener_creation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
        time.sleep(0.5)
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "PASSED" if result else "FAILED"
        print(f"Test {i}: {test.__name__} - {status}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Pynput integration is ready for use.")
        print()
        print("The enhanced agent can now use pynput for:")
        print("  - Precise mouse movement control")
        print("  - Advanced keyboard input handling")
        print("  - Real-time input event monitoring")
        print("  - Smooth cursor animations")
        print("  - Key combination support")
    else:
        print("❌ Some tests failed. Pynput integration may have issues.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)