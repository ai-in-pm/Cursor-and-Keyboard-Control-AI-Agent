#!/usr/bin/env python3
"""
Automated test for physical cursor movement capabilities
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

def test_cursor_movement():
    """Test that the cursor actually moves on screen"""
    print_header("AUTOMATED PHYSICAL CURSOR MOVEMENT TEST")
    print("\n⚠️  This test will physically move your cursor!")
    print("   Starting in 3 seconds...")
    time.sleep(3)
    
    agent = SimpleCursorKeyboardAgent()
    
    # Get initial position
    initial_x, initial_y = agent.get_current_position()
    print(f"\n📍 Initial cursor position: ({initial_x}, {initial_y})")
    print(f"🖥️  Screen size: {agent.screen_width} x {agent.screen_height}")
    
    tests_passed = 0
    tests_failed = 0
    tolerance = 10
    
    # Test 1: Move to center
    print_header("Test 1: Move Cursor to Center")
    
    center_x = agent.screen_width // 2
    center_y = agent.screen_height // 2
    
    print(f"Moving to center ({center_x}, {center_y})...")
    result = agent.execute_command("move cursor to center")
    time.sleep(1)
    
    current_x, current_y = agent.get_current_position()
    print(f"✓ Command: {result['message']}")
    print(f"📍 Current: ({current_x}, {current_y})")
    print(f"🎯 Expected: ({center_x}, {center_y})")
    
    if abs(current_x - center_x) <= tolerance and abs(current_y - center_y) <= tolerance:
        print("✅ PASS: Cursor moved to center!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to center")
        tests_failed += 1
    
    time.sleep(1)
    
    # Test 2: Move to specific coordinates
    print_header("Test 2: Move to Specific Coordinates (500, 300)")
    
    print(f"Moving to (500, 300)...")
    result = agent.execute_command("move cursor to position 500, 300")
    time.sleep(1)
    
    current_x, current_y = agent.get_current_position()
    print(f"✓ Command: {result['message']}")
    print(f"📍 Current: ({current_x}, {current_y})")
    print(f"🎯 Expected: (500, 300)")
    
    if abs(current_x - 500) <= tolerance and abs(current_y - 300) <= tolerance:
        print("✅ PASS: Cursor moved to specific coordinates!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to specified coordinates")
        tests_failed += 1
    
    time.sleep(1)
    
    # Test 3: Move to top left
    print_header("Test 3: Move Cursor to Top Left")
    
    print(f"Moving to top left...")
    result = agent.execute_command("move cursor to top left")
    time.sleep(1)
    
    current_x, current_y = agent.get_current_position()
    print(f"✓ Command: {result['message']}")
    print(f"📍 Current: ({current_x}, {current_y})")

    # Top left should be near (0, 0) - allowing for safe margins
    if current_x < 150 and current_y < 150:
        print("✅ PASS: Cursor moved to top left!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to top left")
        tests_failed += 1
    
    time.sleep(1)
    
    # Test 4: Move to bottom right
    print_header("Test 4: Move Cursor to Bottom Right")
    
    print(f"Moving to bottom right...")
    result = agent.execute_command("move cursor to bottom right")
    time.sleep(1)
    
    current_x, current_y = agent.get_current_position()
    print(f"✓ Command: {result['message']}")
    print(f"📍 Current: ({current_x}, {current_y})")

    # Bottom right should be near screen dimensions - allowing for safe margins
    if current_x > agent.screen_width - 150 and current_y > agent.screen_height - 150:
        print("✅ PASS: Cursor moved to bottom right!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not move to bottom right")
        tests_failed += 1
    
    time.sleep(1)
    
    # Test 5: Return to initial position
    print_header("Test 5: Return to Initial Position")
    
    print(f"Moving back to ({initial_x}, {initial_y})...")
    result = agent.execute_command(f"move cursor to position {initial_x}, {initial_y}")
    time.sleep(1)
    
    current_x, current_y = agent.get_current_position()
    print(f"✓ Command: {result['message']}")
    print(f"📍 Current: ({current_x}, {current_y})")
    print(f"🎯 Expected: ({initial_x}, {initial_y})")
    
    if abs(current_x - initial_x) <= tolerance and abs(current_y - initial_y) <= tolerance:
        print("✅ PASS: Cursor returned to initial position!")
        tests_passed += 1
    else:
        print("❌ FAIL: Cursor did not return to initial position")
        tests_failed += 1
    
    # Final summary
    print_header("FINAL RESULTS")
    print(f"\n✅ Tests Passed: {tests_passed}/5")
    print(f"❌ Tests Failed: {tests_failed}/5")
    
    if tests_failed == 0:
        print("\n🎉 SUCCESS! Physical cursor movement is working perfectly!")
        print("\nThe agent can:")
        print("  ✓ Move cursor to center")
        print("  ✓ Move cursor to specific coordinates")
        print("  ✓ Move cursor to corners (top left, bottom right)")
        print("  ✓ Return cursor to original position")
        print("\n✨ The cursor physically moved on your screen during this test!")
        return True
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review above.")
        return False

if __name__ == "__main__":
    try:
        success = test_cursor_movement()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

