#!/usr/bin/env python3
"""
Test physical cursor movement capabilities
This will actually move your cursor on screen!
"""

import sys
from pathlib import Path
import time

# Add the agent directory to Python path
agent_dir = Path(__file__).parent / "llm" / "ck-agent-llm" / "microsoft_phi-silica-3.6_v1"
sys.path.insert(0, str(agent_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def countdown(seconds, message):
    """Countdown before action"""
    print(f"\n{message}")
    for i in range(seconds, 0, -1):
        print(f"  {i}...", end='\r')
        time.sleep(1)
    print("  GO!   ")

def test_physical_cursor_movement():
    """Test that the cursor actually moves on screen"""
    print_header("PHYSICAL CURSOR MOVEMENT TEST")
    print("\n⚠️  WARNING: This test will physically move your cursor!")
    print("   Make sure you're ready and have saved any work.")
    
    input("\nPress ENTER to continue or Ctrl+C to cancel...")
    
    agent = SimpleCursorKeyboardAgent()
    
    # Get initial position
    initial_x, initial_y = agent.get_current_position()
    print(f"\n📍 Initial cursor position: ({initial_x}, {initial_y})")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Move to center
    print_header("Test 1: Move Cursor to Center")
    countdown(3, "Moving cursor to center in...")
    
    center_x = agent.screen_width // 2
    center_y = agent.screen_height // 2
    
    result = agent.execute_command("move cursor to center")
    time.sleep(0.5)
    
    current_x, current_y = agent.get_current_position()
    print(f"\n✓ Command executed: {result['message']}")
    print(f"📍 Current position: ({current_x}, {current_y})")
    print(f"🎯 Expected position: ({center_x}, {center_y})")
    
    # Check if cursor actually moved to center (with some tolerance)
    tolerance = 10
    if abs(current_x - center_x) <= tolerance and abs(current_y - center_y) <= tolerance:
        print("✅ PASS: Cursor moved to center!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to center")
        tests_failed += 1
    
    time.sleep(2)
    
    # Test 2: Move to top left
    print_header("Test 2: Move Cursor to Top Left")
    countdown(3, "Moving cursor to top left in...")
    
    result = agent.execute_command("move cursor to top left")
    time.sleep(0.5)
    
    current_x, current_y = agent.get_current_position()
    print(f"\n✓ Command executed: {result['message']}")
    print(f"📍 Current position: ({current_x}, {current_y})")
    
    # Top left should be near (0, 0)
    if current_x < 100 and current_y < 100:
        print("✅ PASS: Cursor moved to top left!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to top left")
        tests_failed += 1
    
    time.sleep(2)
    
    # Test 3: Move to bottom right
    print_header("Test 3: Move Cursor to Bottom Right")
    countdown(3, "Moving cursor to bottom right in...")
    
    result = agent.execute_command("move cursor to bottom right")
    time.sleep(0.5)
    
    current_x, current_y = agent.get_current_position()
    print(f"\n✓ Command executed: {result['message']}")
    print(f"📍 Current position: ({current_x}, {current_y})")
    
    # Bottom right should be near screen dimensions
    if current_x > agent.screen_width - 100 and current_y > agent.screen_height - 100:
        print("✅ PASS: Cursor moved to bottom right!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to bottom right")
        tests_failed += 1
    
    time.sleep(2)
    
    # Test 4: Move to specific coordinates
    print_header("Test 4: Move to Specific Coordinates (500, 300)")
    countdown(3, "Moving cursor to (500, 300) in...")
    
    result = agent.execute_command("move cursor to position 500, 300")
    time.sleep(0.5)
    
    current_x, current_y = agent.get_current_position()
    print(f"\n✓ Command executed: {result['message']}")
    print(f"📍 Current position: ({current_x}, {current_y})")
    print(f"🎯 Expected position: (500, 300)")
    
    if abs(current_x - 500) <= tolerance and abs(current_y - 300) <= tolerance:
        print("✅ PASS: Cursor moved to specific coordinates!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to specified coordinates")
        tests_failed += 1
    
    time.sleep(2)
    
    # Test 5: Click at current position
    print_header("Test 5: Perform Click")
    countdown(3, "Performing click in...")
    
    result = agent.execute_command("click")
    time.sleep(0.5)
    
    print(f"\n✓ Command executed: {result['message']}")
    if result['success']:
        print("✅ PASS: Click performed!")
        tests_passed += 1
    else:
        print("❌ FAIL: Click failed")
        tests_failed += 1
    
    time.sleep(2)
    
    # Test 6: Return to initial position
    print_header("Test 6: Return to Initial Position")
    countdown(3, f"Moving cursor back to ({initial_x}, {initial_y}) in...")
    
    result = agent.execute_command(f"move cursor to position {initial_x}, {initial_y}")
    time.sleep(0.5)
    
    current_x, current_y = agent.get_current_position()
    print(f"\n✓ Command executed: {result['message']}")
    print(f"📍 Current position: ({current_x}, {current_y})")
    print(f"🎯 Expected position: ({initial_x}, {initial_y})")
    
    if abs(current_x - initial_x) <= tolerance and abs(current_y - initial_y) <= tolerance:
        print("✅ PASS: Cursor returned to initial position!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not return to initial position")
        tests_failed += 1
    
    # Final summary
    print_header("FINAL RESULTS")
    print(f"\n✅ Tests Passed: {tests_passed}/6")
    print(f"❌ Tests Failed: {tests_failed}/6")
    
    if tests_failed == 0:
        print("\n🎉 SUCCESS! Physical cursor movement is working perfectly!")
        print("\nThe agent can:")
        print("  ✓ Move cursor to center")
        print("  ✓ Move cursor to corners (top left, bottom right)")
        print("  ✓ Move cursor to specific coordinates")
        print("  ✓ Perform clicks")
        print("  ✓ Return cursor to original position")
        return True
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review above.")
        return False

if __name__ == "__main__":
    try:
        success = test_physical_cursor_movement()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

