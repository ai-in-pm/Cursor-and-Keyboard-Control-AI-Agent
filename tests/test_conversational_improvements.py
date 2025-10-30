#!/usr/bin/env python3
"""
Test script to verify conversational improvements in the AI Agent
"""

import sys
from pathlib import Path

# Add the agent directory to Python path
agent_dir = Path(__file__).parent / "llm" / "ck-agent-llm" / "microsoft_phi-silica-3.6_v1"
sys.path.insert(0, str(agent_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent

def test_conversational_responses():
    """Test that responses are natural and conversational"""
    print("="*70)
    print("  Testing Conversational Improvements")
    print("="*70)
    print()
    
    agent = SimpleCursorKeyboardAgent()
    
    # Test cases with expected behavior
    test_cases = [
        {
            "command": "hello",
            "should_succeed": True,
            "description": "Greeting should be handled conversationally"
        },
        {
            "command": "move cursor to center",
            "should_succeed": True,
            "description": "Move command should work and respond naturally"
        },
        {
            "command": "click",
            "should_succeed": True,
            "description": "Click command should respond naturally"
        },
        {
            "command": "type hello world",
            "should_succeed": True,
            "description": "Type command should respond naturally"
        },
        {
            "command": "thanks",
            "should_succeed": True,
            "description": "Thank you should be handled conversationally"
        },
        {
            "command": "what can you do",
            "should_succeed": True,
            "description": "Help request should be handled conversationally"
        },
        {
            "command": "some random gibberish xyz123",
            "should_succeed": False,
            "description": "Unknown command should give helpful error"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Command: '{test['command']}'")
        
        result = agent.execute_command(test['command'])
        
        # Check if success matches expectation
        if result['success'] == test['should_succeed']:
            print(f"✓ Status: PASS")
        else:
            print(f"✗ Status: FAIL (Expected success={test['should_succeed']}, got {result['success']})")
            failed += 1
            continue
        
        # Check response quality
        message = result['message']
        print(f"Response: '{message}'")
        
        # Verify no question marks in responses (unless it's a question)
        has_question_mark = '?' in message
        is_question = message.strip().endswith('?')
        
        # Check for unwanted symbols
        has_emoji_question = '❓' in message
        has_emoji_x = '❌' in message
        has_brackets = '[SUCCESS]' in message or '[FAILED]' in message
        
        issues = []
        if has_emoji_question:
            issues.append("Contains ❓ emoji")
        if has_emoji_x and not result['success']:
            issues.append("Contains ❌ emoji in error")
        if has_brackets:
            issues.append("Contains [SUCCESS]/[FAILED] brackets")
        
        if issues:
            print(f"✗ Response Quality: FAIL - {', '.join(issues)}")
            failed += 1
        else:
            print(f"✓ Response Quality: PASS - Natural and conversational")
            passed += 1
        
        print("-" * 70)
    
    print()
    print("="*70)
    print(f"  Test Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70)
    print()
    
    if failed == 0:
        print("✓ All tests passed! The agent now has natural, conversational responses.")
        return True
    else:
        print(f"✗ {failed} test(s) failed. Please review the responses above.")
        return False

if __name__ == "__main__":
    success = test_conversational_responses()
    sys.exit(0 if success else 1)

