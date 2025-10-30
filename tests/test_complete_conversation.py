#!/usr/bin/env python3
"""
Comprehensive test for conversational AI improvements
Tests greetings, commands, and mixed scenarios
"""

import sys
from pathlib import Path

# Add the agent directory to Python path
agent_dir = Path(__file__).parent / "llm" / "ck-agent-llm" / "microsoft_phi-silica-3.6_v1"
sys.path.insert(0, str(agent_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent

def print_test_header(test_num, description):
    """Print a formatted test header"""
    print(f"\n{'='*70}")
    print(f"Test {test_num}: {description}")
    print('='*70)

def print_result(command, response, expected_behavior, passed):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\nCommand: '{command}'")
    print(f"Response: '{response}'")
    print(f"Expected: {expected_behavior}")
    print(f"Result: {status}")

def test_complete_conversation():
    """Test all conversation scenarios"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE CONVERSATIONAL AI TEST")
    print("="*70)
    
    agent = SimpleCursorKeyboardAgent()
    
    passed = 0
    failed = 0
    test_num = 0
    
    # Test 1: Simple greeting
    test_num += 1
    print_test_header(test_num, "Simple Greeting")
    result = agent.execute_command("hello")
    is_greeting = "Hello!" in result['message'] and "help you" in result['message']
    print_result("hello", result['message'], "Friendly greeting response", is_greeting)
    if is_greeting:
        passed += 1
    else:
        failed += 1
    
    # Test 2: Greeting with punctuation
    test_num += 1
    print_test_header(test_num, "Greeting with Punctuation")
    result = agent.execute_command("Hi!")
    is_greeting = "Hello!" in result['message']
    print_result("Hi!", result['message'], "Friendly greeting response", is_greeting)
    if is_greeting:
        passed += 1
    else:
        failed += 1
    
    # Test 3: Move cursor to center
    test_num += 1
    print_test_header(test_num, "Move Cursor to Center")
    result = agent.execute_command("move cursor to center")
    is_move = result['success'] and "cursor moved to center" in result['message']
    print_result("move cursor to center", result['message'], "Cursor movement confirmation", is_move)
    if is_move:
        passed += 1
    else:
        failed += 1
    
    # Test 4: Type hello world (should NOT trigger greeting)
    test_num += 1
    print_test_header(test_num, "Type 'hello world' - Should Type, Not Greet")
    result = agent.execute_command("type hello world")
    is_typing = result['success'] and "typed" in result['message'].lower() and "hello world" in result['message']
    is_not_greeting = "Hello! I'm ready" not in result['message']
    passed_test = is_typing and is_not_greeting
    print_result("type hello world", result['message'], "Should type text, not respond with greeting", passed_test)
    if passed_test:
        passed += 1
    else:
        failed += 1
    
    # Test 5: Click command
    test_num += 1
    print_test_header(test_num, "Click Command")
    result = agent.execute_command("click")
    is_click = result['success'] and "click" in result['message'].lower()
    print_result("click", result['message'], "Click confirmation", is_click)
    if is_click:
        passed += 1
    else:
        failed += 1
    
    # Test 6: Double click
    test_num += 1
    print_test_header(test_num, "Double Click")
    result = agent.execute_command("double click")
    is_double = result['success'] and "double click" in result['message'].lower()
    print_result("double click", result['message'], "Double click confirmation", is_double)
    if is_double:
        passed += 1
    else:
        failed += 1
    
    # Test 7: Thank you
    test_num += 1
    print_test_header(test_num, "Gratitude Expression")
    result = agent.execute_command("thanks")
    is_thanks = result['success'] and "welcome" in result['message'].lower()
    print_result("thanks", result['message'], "Polite acknowledgment", is_thanks)
    if is_thanks:
        passed += 1
    else:
        failed += 1
    
    # Test 8: Help request
    test_num += 1
    print_test_header(test_num, "Help Request")
    result = agent.execute_command("what can you do")
    is_help = result['success'] and "help you" in result['message'].lower()
    print_result("what can you do", result['message'], "List of capabilities", is_help)
    if is_help:
        passed += 1
    else:
        failed += 1
    
    # Test 9: Type with quotes
    test_num += 1
    print_test_header(test_num, "Type with Quotes")
    result = agent.execute_command('type "test message"')
    is_typing = result['success'] and "typed" in result['message'].lower() and "test message" in result['message']
    print_result('type "test message"', result['message'], "Should type quoted text", is_typing)
    if is_typing:
        passed += 1
    else:
        failed += 1
    
    # Test 10: Scroll down
    test_num += 1
    print_test_header(test_num, "Scroll Down")
    result = agent.execute_command("scroll down")
    is_scroll = result['success'] and "scroll" in result['message'].lower()
    print_result("scroll down", result['message'], "Scroll confirmation", is_scroll)
    if is_scroll:
        passed += 1
    else:
        failed += 1
    
    # Test 11: Press Enter
    test_num += 1
    print_test_header(test_num, "Press Enter Key")
    result = agent.execute_command("press enter")
    is_press = result['success'] and "enter" in result['message'].lower()
    print_result("press enter", result['message'], "Key press confirmation", is_press)
    if is_press:
        passed += 1
    else:
        failed += 1
    
    # Test 12: Copy (hotkey)
    test_num += 1
    print_test_header(test_num, "Copy Hotkey")
    result = agent.execute_command("copy")
    is_copy = result['success'] and "clipboard" in result['message'].lower()
    print_result("copy", result['message'], "Copy action confirmation", is_copy)
    if is_copy:
        passed += 1
    else:
        failed += 1
    
    # Test 13: Unknown command
    test_num += 1
    print_test_header(test_num, "Unknown Command")
    result = agent.execute_command("do something random xyz")
    is_helpful_error = not result['success'] and "not sure" in result['message'].lower()
    print_result("do something random xyz", result['message'], "Helpful error message", is_helpful_error)
    if is_helpful_error:
        passed += 1
    else:
        failed += 1
    
    # Test 14: Move to specific position
    test_num += 1
    print_test_header(test_num, "Move to Specific Position")
    result = agent.execute_command("move cursor to position 500, 300")
    is_move = result['success'] and "500" in result['message'] and "300" in result['message']
    print_result("move cursor to position 500, 300", result['message'], "Move to coordinates", is_move)
    if is_move:
        passed += 1
    else:
        failed += 1
    
    # Test 15: Right click
    test_num += 1
    print_test_header(test_num, "Right Click")
    result = agent.execute_command("right click")
    is_right = result['success'] and "right click" in result['message'].lower()
    print_result("right click", result['message'], "Right click confirmation", is_right)
    if is_right:
        passed += 1
    else:
        failed += 1
    
    # Final summary
    print("\n" + "="*70)
    print(f"  FINAL RESULTS: {passed}/{test_num} tests passed")
    print("="*70)
    
    if failed == 0:
        print("\n✓ SUCCESS! All conversational scenarios work correctly!")
        print("  - Greetings are handled naturally")
        print("  - Commands execute properly")
        print("  - 'type hello' doesn't trigger greeting")
        print("  - Responses are conversational and natural")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed. Please review above.")
        return False

if __name__ == "__main__":
    success = test_complete_conversation()
    sys.exit(0 if success else 1)

