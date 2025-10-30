#!/usr/bin/env python3
"""
Interactive demonstration of the improved conversational AI
Shows natural conversation flow with the agent
"""

import sys
from pathlib import Path
import time

# Add the agent directory to Python path
# demo/demo_conversation.py -> go up to root, then to llm/ck-agent-llm/microsoft_phi-silica-3.6_v1
agent_dir = Path(__file__).parent.parent / "llm" / "ck-agent-llm" / "microsoft_phi-silica-3.6_v1"
sys.path.insert(0, str(agent_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent

def print_conversation(user_msg, ai_msg, delay=0.5):
    """Print a conversation turn with formatting"""
    print(f"\n{'─'*70}")
    print(f"👤 You: {user_msg}")
    time.sleep(delay)
    print(f"🤖 AI:  {ai_msg}")
    time.sleep(delay)

def main():
    """Run an interactive demonstration"""
    print("\n" + "="*70)
    print("  AI AGENT CONVERSATIONAL DEMONSTRATION")
    print("  Showing Natural Language Interactions")
    print("="*70)
    
    agent = SimpleCursorKeyboardAgent()
    
    # Demonstration conversation
    demo_commands = [
        ("hello", "Starting with a greeting"),
        ("move cursor to center", "Moving the cursor"),
        ("click", "Performing a click"),
        ("type hello world", "Typing text (critical test!)"),
        ("scroll down", "Scrolling"),
        ("press enter", "Pressing a key"),
        ("copy", "Using a hotkey"),
        ("what can you do", "Asking for help"),
        ("thanks", "Expressing gratitude"),
    ]
    
    print("\n" + "="*70)
    print("  DEMONSTRATION CONVERSATION")
    print("="*70)
    
    for command, description in demo_commands:
        print(f"\n[{description}]")
        result = agent.execute_command(command)
        print_conversation(command, result['message'], delay=0.3)
    
    print("\n" + "="*70)
    print("  KEY OBSERVATIONS")
    print("="*70)
    print("""
✓ Greetings are handled naturally
✓ Commands execute with clear confirmations
✓ "type hello world" TYPES the text (doesn't greet!)
✓ Responses are conversational and friendly
✓ No unwanted symbols (❓, ❌, [SUCCESS], [FAILED])
✓ Help requests are answered helpfully
✓ Gratitude is acknowledged politely
    """)
    
    print("\n" + "="*70)
    print("  INTERACTIVE MODE")
    print("="*70)
    print("\nYou can now chat with the agent yourself!")
    print("Try commands like:")
    print("  • hello")
    print("  • move cursor to center")
    print("  • type your message here")
    print("  • click")
    print("  • what can you do")
    print("\nType 'quit' to exit.\n")
    
    # Interactive mode
    while True:
        try:
            user_input = input("👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n🤖 AI:  Goodbye! Have a great day!")
                break
            elif user_input:
                result = agent.execute_command(user_input)
                print(f"🤖 AI:  {result['message']}")
        except KeyboardInterrupt:
            print("\n\n🤖 AI:  Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"🤖 AI:  Oops, something went wrong: {e}")

if __name__ == "__main__":
    main()

