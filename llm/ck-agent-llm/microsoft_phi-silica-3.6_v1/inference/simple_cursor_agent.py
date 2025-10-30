#!/usr/bin/env python3
"""
Simple Cursor and Keyboard Control Agent
Standalone version without TensorFlow/transformers dependencies
"""

import os
import queue
import sys
import threading
import time
from pathlib import Path

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    from pynput.keyboard import Key, Listener

    PYNUT_AVAILABLE = True
except ImportError:
    PYNUT_AVAILABLE = False
    print("Warning: pynput not available. Install with: pip install pynput")

try:
    import pyautogui

    PY_AUTOGUI_AVAILABLE = True
except ImportError:
    PY_AUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available. Install with: pip install pyautogui")


class SimpleCursorKeyboardAgent:
    """Simple cursor and keyboard control agent without ML dependencies"""

    def __init__(self):
        self.mouse_controller = mouse.Controller() if PYNUT_AVAILABLE else None
        self.keyboard_controller = keyboard.Controller() if PYNUT_AVAILABLE else None
        self.action_queue = queue.Queue()
        self.is_running = False

        # Screen dimensions
        if PY_AUTOGUI_AVAILABLE:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = 1920, 1080  # Default fallback

        self.conversation_history = []  # Track user/agent turns for context

    def get_current_position(self):
        """Get current mouse position"""
        if PY_AUTOGUI_AVAILABLE:
            return pyautogui.position()
        elif self.mouse_controller:
            return self.mouse_controller.position
        else:
            return (0, 0)

    def move_cursor(self, x, y, duration=0.5):
        """Move cursor to specified coordinates"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.moveTo(x, y, duration=duration)
            elif self.mouse_controller:
                # Smooth movement with pynput
                current_x, current_y = self.mouse_controller.position
                steps = int(duration * 100)
                if steps > 0:
                    dx = (x - current_x) / steps
                    dy = (y - current_y) / steps
                    for i in range(steps):
                        new_x = int(current_x + dx * (i + 1))
                        new_y = int(current_y + dy * (i + 1))
                        self.mouse_controller.position = (new_x, new_y)
                        time.sleep(duration / steps)
                self.mouse_controller.position = (x, y)
            return True
        except Exception as e:
            print(f"Error moving cursor: {e}")
            return False

    def move_cursor_relative(self, dx, dy, duration=0.5):
        """Move cursor relative to current position"""
        current_x, current_y = self.get_current_position()
        return self.move_cursor(current_x + dx, current_y + dy, duration)

    def click(self, button='left', count=1):
        """Perform mouse click"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.click(button=button, clicks=count)
            elif self.mouse_controller:
                pynput_button = getattr(Button, button, Button.left)
                for _ in range(count):
                    self.mouse_controller.click(pynput_button)
            return True
        except Exception as e:
            print(f"Error clicking: {e}")
            return False

    def double_click(self, button='left'):
        """Perform double click"""
        return self.click(button, 2)

    def right_click(self):
        """Perform right click"""
        return self.click('right')

    def scroll(self, dx=0, dy=0):
        """Scroll mouse wheel"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.scroll(dy)
            elif self.mouse_controller:
                self.mouse_controller.scroll(dx, dy)
            return True
        except Exception as e:
            print(f"Error scrolling: {e}")
            return False

    def type_text(self, text):
        """Type text using keyboard"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.write(text)
            elif self.keyboard_controller:
                self.keyboard_controller.type(text)
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False

    def press_key(self, key_name):
        """Press a specific key"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.press(key_name)
            elif self.keyboard_controller:
                # Convert string to pynput Key if it's a special key
                if hasattr(Key, key_name):
                    key = getattr(Key, key_name)
                else:
                    key = key_name
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False

    def hotkey(self, *keys):
        """Press combination of keys"""
        try:
            if PY_AUTOGUI_AVAILABLE:
                pyautogui.hotkey(*keys)
            elif self.keyboard_controller:
                # Press and release each key in sequence
                for key_name in keys:
                    if hasattr(Key, key_name):
                        key = getattr(Key, key_name)
                    else:
                        key = key_name
                    self.keyboard_controller.press(key)
                for key_name in reversed(keys):
                    if hasattr(Key, key_name):
                        key = getattr(Key, key_name)
                    else:
                        key = key_name
                    self.keyboard_controller.release(key)
            return True
        except Exception as e:
            print(f"Error with hotkey: {e}")
            return False

    def parse_command(self, command):
        """Parse natural language command and execute appropriate action"""
        original_command = command
        command = command.lower().strip()

        # Handle conversational inputs - check if it's ONLY a greeting/conversation
        # Not part of a command like "type hello"
        command_words = command.split()

        # Greetings - only if it's a standalone greeting
        if command in ['hello', 'hi', 'hey', 'hello!', 'hi!', 'hey!'] or \
           (len(command_words) <= 3 and any(command.startswith(word) for word in ['hello', 'hi', 'hey'])):
            # Make sure it's not "type hello" or similar
            if not any(cmd in command for cmd in ['type', 'move', 'click', 'scroll', 'press']):
                return True, "Hello! I'm ready to help you control your cursor and keyboard. What would you like me to do?"

        # Thanks/gratitude - only if it's standalone
        if command in ['thanks', 'thank you', 'thanks!', 'thank you!', 'ty'] or \
           command.startswith('thanks') or command.startswith('thank you'):
            if not any(cmd in command for cmd in ['type', 'move', 'click', 'scroll', 'press']):
                return True, "You're welcome! Let me know if you need anything else."

        # Help requests
        if any(phrase in command for phrase in ['what can you do', 'help me', 'show me', 'capabilities', 'how do']):
            return True, "I can help you move the cursor, click, type text, scroll, and press keys. Just tell me what you'd like!"

        # Move cursor commands
        if 'move cursor to' in command or 'move mouse to' in command or 'move to' in command:
            if 'center' in command:
                x, y = self.screen_width // 2, self.screen_height // 2
                return self.move_cursor(x, y), f"cursor moved to center at ({x}, {y})"
            elif 'top left' in command:
                return self.move_cursor(100, 100), "cursor moved to top left corner"
            elif 'top right' in command:
                return self.move_cursor(self.screen_width - 100, 100), "cursor moved to top right corner"
            elif 'bottom left' in command:
                return self.move_cursor(100, self.screen_height - 100), "cursor moved to bottom left corner"
            elif 'bottom right' in command:
                return self.move_cursor(self.screen_width - 100,
                                        self.screen_height - 100), "cursor moved to bottom right corner"
            elif 'position' in command:
                # Extract coordinates like "position 500, 300"
                import re
                coords = re.findall(r'\d+', command)
                if len(coords) >= 2:
                    x, y = int(coords[0]), int(coords[1])
                    return self.move_cursor(x, y), f"cursor moved to position ({x}, {y})"

        # Click commands
        elif 'click' in command:
            if 'right' in command:
                return self.right_click(), "right click performed"
            elif 'double' in command:
                return self.double_click(), "double click performed"
            else:
                return self.click(), "left click performed"

        # Scroll commands
        elif 'scroll' in command:
            if 'up' in command:
                return self.scroll(dy=5), "scrolled up"
            elif 'down' in command:
                return self.scroll(dy=-5), "scrolled down"

        # Type commands
        elif 'type' in command:
            # Extract text to type - handle various formats
            import re
            # Try to find quoted text first
            quoted_match = re.search(r'["\']([^"\']+)["\']', original_command)
            if quoted_match:
                text = quoted_match.group(1)
                return self.type_text(text), f"typed '{text}'"
            else:
                # Fall back to text after 'type'
                text_start = command.find('type') + 4
                text = original_command[text_start:].strip().strip('"\'')
                if text:
                    return self.type_text(text), f"typed '{text}'"

        # Key press commands
        elif 'press' in command or 'hit' in command:
            if 'enter' in command:
                return self.press_key('enter'), "Enter key pressed"
            elif 'space' in command:
                return self.press_key('space'), "Space key pressed"
            elif 'tab' in command:
                return self.press_key('tab'), "Tab key pressed"
            elif 'escape' in command or 'esc' in command:
                return self.press_key('esc'), "Escape key pressed"

        # Hotkey commands
        elif 'copy' in command:
            return self.hotkey('ctrl', 'c'), "copied to clipboard (Ctrl+C)"
        elif 'paste' in command:
            return self.hotkey('ctrl', 'v'), "pasted from clipboard (Ctrl+V)"
        elif 'select all' in command:
            return self.hotkey('ctrl', 'a'), "selected all (Ctrl+A)"
        elif 'save' in command:
            return self.hotkey('ctrl', 's'), "saved (Ctrl+S)"

        return False, f"I'm not sure what you want me to do with '{original_command}'"

    def execute_command(self, command):
        """Execute a command and return result"""
        success, message = self.parse_command(command)
        return {
            'success': success,
            'message': message,
            'command': command
        }

    def interactive_mode(self):
        """Run in conversational interactive mode"""
        print("\n" + "="*60)
        print("  Cursor & Keyboard Control Agent - Interactive Mode")
        print("="*60)
        print("\nI can help you with:")
        print("  • Moving the cursor (e.g., 'move to center')")
        print("  • Clicking (e.g., 'double click', 'right click')")
        print("  • Typing text (e.g., 'type hello world')")
        print("  • Scrolling (e.g., 'scroll down')")
        print("  • Pressing keys (e.g., 'press enter', 'copy', 'paste')")
        print("\nType 'quit' or 'exit' to leave.\n")

        while True:
            try:
                command = input("You: ").strip()
                if command.lower() in ['quit', 'exit', 'q']:
                    print("\nAI: Goodbye! Have a great day!")
                    break
                elif command:
                    self.conversation_history.append({'role': 'user', 'content': command})
                    result = self.execute_command(command)

                    # Generate natural response
                    if result['success']:
                        agent_reply = f"AI: {result['message']}"
                    else:
                        agent_reply = f"AI: {result['message']}"

                    print(agent_reply)
                    self.conversation_history.append({'role': 'agent', 'content': agent_reply})

            except KeyboardInterrupt:
                print("\n\nAI: Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"AI: Oops, something went wrong: {e}")


if __name__ == "__main__":
    agent = SimpleCursorKeyboardAgent()
    agent.interactive_mode()
