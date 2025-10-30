#!/usr/bin/env python3
"""
Visual demonstration of cursor movement capabilities
Shows the cursor moving in patterns with visual feedback
"""

import sys
from pathlib import Path
import time

# Add the agent directory to Python path
# demo/cursor_demo_visual.py -> go up to root, then to llm/ck-agent-llm/microsoft_phi-silica-3.6_v1
agent_dir = Path(__file__).parent.parent / "llm" / "ck-agent-llm" / "microsoft_phi-silica-3.6_v1"
sys.path.insert(0, str(agent_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_cursor_position(agent, label="Current"):
    """Print current cursor position with visual indicator"""
    x, y = agent.get_current_position()
    print(f"📍 {label} position: ({x:4d}, {y:4d})")

def demo_cursor_patterns():
    """Demonstrate cursor movement in various patterns"""
    print_header("VISUAL CURSOR MOVEMENT DEMONSTRATION")
    print("\n✨ Watch your cursor move in different patterns!")
    print("   Starting in 3 seconds...")
    time.sleep(3)
    
    agent = SimpleCursorKeyboardAgent()
    
    # Save initial position
    initial_x, initial_y = agent.get_current_position()
    print(f"\n📍 Starting position: ({initial_x}, {initial_y})")
    print(f"🖥️  Screen size: {agent.screen_width} x {agent.screen_height}")
    
    # Pattern 1: Four Corners Tour
    print_header("Pattern 1: Four Corners Tour")
    print("Moving cursor to all four corners of the screen...")
    
    corners = [
        ("Top Left", "move cursor to top left"),
        ("Top Right", "move cursor to top right"),
        ("Bottom Right", "move cursor to bottom right"),
        ("Bottom Left", "move cursor to bottom left"),
    ]
    
    for corner_name, command in corners:
        print(f"\n→ Moving to {corner_name}...")
        result = agent.execute_command(command)
        time.sleep(0.5)
        print_cursor_position(agent, corner_name)
        time.sleep(1)
    
    # Pattern 2: Center and Edges
    print_header("Pattern 2: Center and Edges")
    print("Moving cursor to center and all edges...")
    
    positions = [
        ("Center", "move cursor to center"),
        ("Top Edge", f"move cursor to position {agent.screen_width // 2}, 100"),
        ("Right Edge", f"move cursor to position {agent.screen_width - 100}, {agent.screen_height // 2}"),
        ("Bottom Edge", f"move cursor to position {agent.screen_width // 2}, {agent.screen_height - 100}"),
        ("Left Edge", f"move cursor to position 100, {agent.screen_height // 2}"),
    ]
    
    for pos_name, command in positions:
        print(f"\n→ Moving to {pos_name}...")
        result = agent.execute_command(command)
        time.sleep(0.5)
        print_cursor_position(agent, pos_name)
        time.sleep(1)
    
    # Pattern 3: Diagonal Movement
    print_header("Pattern 3: Diagonal Movement")
    print("Moving cursor diagonally across the screen...")
    
    diagonals = [
        ("Top Left", "move cursor to top left"),
        ("Center", "move cursor to center"),
        ("Bottom Right", "move cursor to bottom right"),
        ("Center", "move cursor to center"),
        ("Top Right", "move cursor to top right"),
        ("Center", "move cursor to center"),
        ("Bottom Left", "move cursor to bottom left"),
    ]
    
    for pos_name, command in diagonals:
        print(f"\n→ Moving to {pos_name}...")
        result = agent.execute_command(command)
        time.sleep(0.5)
        print_cursor_position(agent, pos_name)
        time.sleep(0.8)
    
    # Pattern 4: Spiral Pattern (approximate)
    print_header("Pattern 4: Spiral Pattern")
    print("Moving cursor in a spiral pattern...")
    
    center_x = agent.screen_width // 2
    center_y = agent.screen_height // 2
    
    spiral_points = [
        (center_x, center_y),
        (center_x + 200, center_y),
        (center_x + 200, center_y + 200),
        (center_x - 200, center_y + 200),
        (center_x - 200, center_y - 200),
        (center_x + 400, center_y - 200),
        (center_x + 400, center_y + 400),
        (center_x - 400, center_y + 400),
        (center_x, center_y),
    ]
    
    for i, (x, y) in enumerate(spiral_points):
        print(f"\n→ Spiral point {i+1}/{len(spiral_points)}...")
        result = agent.execute_command(f"move cursor to position {x}, {y}")
        time.sleep(0.3)
        print_cursor_position(agent, f"Point {i+1}")
        time.sleep(0.5)
    
    # Return to initial position
    print_header("Returning to Initial Position")
    print(f"Moving cursor back to starting position ({initial_x}, {initial_y})...")
    result = agent.execute_command(f"move cursor to position {initial_x}, {initial_y}")
    time.sleep(0.5)
    print_cursor_position(agent, "Final")
    
    # Summary
    print_header("DEMONSTRATION COMPLETE")
    print("\n✅ Successfully demonstrated:")
    print("  ✓ Four corners tour")
    print("  ✓ Center and edges movement")
    print("  ✓ Diagonal movements")
    print("  ✓ Spiral pattern")
    print("  ✓ Return to initial position")
    print("\n🎉 The cursor physically moved across your screen!")
    print("   The agent has full control over cursor positioning.")

def demo_interactive_cursor():
    """Interactive cursor movement demo"""
    print_header("INTERACTIVE CURSOR CONTROL")
    print("\nYou can now control the cursor with natural language!")
    print("\nTry commands like:")
    print("  • move cursor to center")
    print("  • move cursor to top left")
    print("  • move cursor to position 800, 600")
    print("  • click")
    print("  • double click")
    print("\nType 'patterns' to see the pattern demo again")
    print("Type 'quit' to exit\n")
    
    agent = SimpleCursorKeyboardAgent()
    
    while True:
        try:
            user_input = input("👤 Command: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n🤖 Goodbye!")
                break
            elif user_input.lower() == 'patterns':
                demo_cursor_patterns()
                print("\n" + "="*70)
                print("  Back to Interactive Mode")
                print("="*70 + "\n")
            elif user_input:
                result = agent.execute_command(user_input)
                print(f"🤖 {result['message']}")
                if result['success']:
                    print_cursor_position(agent)
        except KeyboardInterrupt:
            print("\n\n🤖 Goodbye!")
            break
        except Exception as e:
            print(f"🤖 Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        demo_interactive_cursor()
    else:
        demo_cursor_patterns()
        print("\n" + "="*70)
        print("  Want to try interactive mode?")
        print("  Run: python cursor_demo_visual.py --interactive")
        print("="*70)

