#!/usr/bin/env python3
"""
Enhanced Cursor and Keyboard Control Agent using pynput for advanced control.
This agent integrates pynput for more sophisticated mouse and keyboard operations.
"""

import os
import re
import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline
)
from peft import PeftModel
import time
import logging
import threading
from typing import List, Dict, Any, Optional, Callable
from queue import Queue, Empty
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMouseController:
    """Enhanced mouse controller using pynput"""
    def __init__(self):
        self.controller = mouse.Controller()
        self.screen_width, self.screen_height = self._get_screen_size()
        
    def _get_screen_size(self):
        """Get screen size using pynput"""
        # pynput doesn't have direct screen size access, so we'll use a fallback
        try:
            import pyautogui
            return pyautogui.size()
        except:
            # Default screen size if pyautogui is not available
            return 1920, 1080
    
    def move_to(self, x: int, y: int, duration: float = 0.0):
        """Move mouse to absolute coordinates"""
        if duration > 0:
            # Smooth movement implementation
            self._smooth_move(x, y, duration)
        else:
            self.controller.position = (x, y)
    
    def _smooth_move(self, x: int, y: int, duration: float):
        """Smooth mouse movement over duration"""
        start_x, start_y = self.controller.position
        steps = int(duration * 100)  # 100 steps per second
        if steps > 0:
            for i in range(steps + 1):
                progress = i / steps
                current_x = start_x + (x - start_x) * progress
                current_y = start_y + (y - start_y) * progress
                self.controller.position = (int(current_x), int(current_y))
                time.sleep(duration / steps)
    
    def move_relative(self, dx: int, dy: int, duration: float = 0.0):
        """Move mouse relative to current position"""
        current_x, current_y = self.controller.position
        target_x = current_x + dx
        target_y = current_y + dy
        self.move_to(target_x, target_y, duration)
    
    def click(self, button: str = 'left', count: int = 1):
        """Perform mouse click"""
        button_obj = self._get_button(button)
        for _ in range(count):
            self.controller.click(button_obj, 1)
    
    def double_click(self, button: str = 'left'):
        """Perform double click"""
        button_obj = self._get_button(button)
        self.controller.click(button_obj, 2)
    
    def press(self, button: str = 'left'):
        """Press mouse button down"""
        button_obj = self._get_button(button)
        self.controller.press(button_obj)
    
    def release(self, button: str = 'left'):
        """Release mouse button"""
        button_obj = self._get_button(button)
        self.controller.release(button_obj)
    
    def scroll(self, dx: int, dy: int):
        """Scroll mouse"""
        self.controller.scroll(dx, dy)
    
    def drag_to(self, x: int, y: int, duration: float = 0.0):
        """Drag mouse to position while holding left button"""
        self.press('left')
        self.move_to(x, y, duration)
        self.release('left')
    
    def _get_button(self, button: str) -> Button:
        """Convert string to pynput Button"""
        button = button.lower()
        if button == 'left':
            return Button.left
        elif button == 'right':
            return Button.right
        elif button == 'middle':
            return Button.middle
        else:
            return Button.left

class EnhancedKeyboardController:
    """Enhanced keyboard controller using pynput"""
    def __init__(self):
        self.controller = keyboard.Controller()
        self.special_keys = {
            'ctrl': Key.ctrl, 'control': Key.ctrl,
            'shift': Key.shift,
            'alt': Key.alt,
            'enter': Key.enter, 'return': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'esc': Key.esc, 'escape': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
        }
    
    def type_text(self, text: str, interval: float = 0.0):
        """Type text with optional interval between characters"""
        if interval > 0:
            for char in text:
                self.controller.type(char)
                time.sleep(interval)
        else:
            self.controller.type(text)
    
    def press_key(self, key: str):
        """Press and release a single key"""
        key_obj = self._get_key(key)
        self.controller.press(key_obj)
        self.controller.release(key_obj)
    
    def press_combination(self, keys: List[str]):
        """Press key combination (like ctrl+c)"""
        key_objs = [self._get_key(key) for key in keys]
        
        # Press all keys
        for key_obj in key_objs:
            self.controller.press(key_obj)
        
        # Release all keys in reverse order
        for key_obj in reversed(key_objs):
            self.controller.release(key_obj)
    
    def hold_key(self, key: str):
        """Hold a key down"""
        key_obj = self._get_key(key)
        self.controller.press(key_obj)
    
    def release_key(self, key: str):
        """Release a held key"""
        key_obj = self._get_key(key)
        self.controller.release(key_obj)
    
    def _get_key(self, key: str):
        """Convert string to pynput Key or character"""
        key_lower = key.lower()
        if key_lower in self.special_keys:
            return self.special_keys[key_lower]
        else:
            return key

class InputListener:
    """Input listener for monitoring mouse and keyboard events"""
    def __init__(self):
        self.mouse_listener = None
        self.keyboard_listener = None
        self.mouse_callbacks = []
        self.keyboard_callbacks = []
        self.running = False
    
    def add_mouse_callback(self, callback: Callable):
        """Add mouse event callback"""
        self.mouse_callbacks.append(callback)
    
    def add_keyboard_callback(self, callback: Callable):
        """Add keyboard event callback"""
        self.keyboard_callbacks.append(callback)
    
    def on_mouse_move(self, x: int, y: int):
        """Handle mouse movement"""
        for callback in self.mouse_callbacks:
            callback('move', {'x': x, 'y': y})
    
    def on_mouse_click(self, x: int, y: int, button: Button, pressed: bool):
        """Handle mouse click"""
        for callback in self.mouse_callbacks:
            callback('click', {'x': x, 'y': y, 'button': str(button), 'pressed': pressed})
    
    def on_mouse_scroll(self, x: int, y: int, dx: int, dy: int):
        """Handle mouse scroll"""
        for callback in self.mouse_callbacks:
            callback('scroll', {'x': x, 'y': y, 'dx': dx, 'dy': dy})
    
    def on_key_press(self, key):
        """Handle key press"""
        try:
            key_str = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_str = str(key)
        
        for callback in self.keyboard_callbacks:
            callback('press', {'key': key_str})
    
    def on_key_release(self, key):
        """Handle key release"""
        try:
            key_str = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_str = str(key)
        
        for callback in self.keyboard_callbacks:
            callback('release', {'key': key_str})
    
    def start(self):
        """Start listening for input events"""
        self.running = True
        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def stop(self):
        """Stop listening for input events"""
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

class EnhancedRealTimeActionQueue:
    """Enhanced queue for managing real-time actions with pynput"""
    def __init__(self):
        self.queue = Queue()
        self.running = True
        self.mouse = EnhancedMouseController()
        self.keyboard = EnhancedKeyboardController()
        self.worker_thread = threading.Thread(target=self._process_actions, daemon=True)
        self.worker_thread.start()
        
    def _process_actions(self):
        """Process actions from the queue in real-time"""
        while self.running:
            try:
                action = self.queue.get(timeout=0.1)
                if action is None:
                    break
                action_type, args = action
                
                # Execute the action using pynput controllers
                if action_type == 'move_cursor':
                    x, y, duration = args
                    self.mouse.move_to(x, y, duration)
                elif action_type == 'move_cursor_relative':
                    dx, dy, duration = args
                    self.mouse.move_relative(dx, dy, duration)
                elif action_type == 'click':
                    button, count = args
                    self.mouse.click(button, count)
                elif action_type == 'double_click':
                    button = args
                    self.mouse.double_click(button)
                elif action_type == 'mouse_down':
                    button = args
                    self.mouse.press(button)
                elif action_type == 'mouse_up':
                    button = args
                    self.mouse.release(button)
                elif action_type == 'scroll':
                    dx, dy = args
                    self.mouse.scroll(dx, dy)
                elif action_type == 'drag':
                    x, y, duration = args
                    self.mouse.drag_to(x, y, duration)
                elif action_type == 'type_text':
                    text, interval = args
                    self.keyboard.type_text(text, interval)
                elif action_type == 'press_key':
                    key = args
                    self.keyboard.press_key(key)
                elif action_type == 'press_combination':
                    keys = args
                    self.keyboard.press_combination(keys)
                elif action_type == 'hold_key':
                    key = args
                    self.keyboard.hold_key(key)
                elif action_type == 'release_key':
                    key = args
                    self.keyboard.release_key(key)
                    
                self.queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing action: {e}")
                
    def add_action(self, action_type: str, args: tuple):
        """Add an action to the real-time queue"""
        self.queue.put((action_type, args))
        
    def stop(self):
        """Stop the action processor"""
        self.running = False
        self.queue.put(None)

class EnhancedCursorKeyboardAgent:
    """Enhanced cursor and keyboard agent using pynput for advanced control"""
    def __init__(self, model_path: str = None, lora_path: str = None):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.action_queue = EnhancedRealTimeActionQueue()
        self.input_listener = InputListener()
        self.current_position = (0, 0)
        
        # Set up input monitoring
        self.input_listener.add_mouse_callback(self._on_mouse_event)
        self.input_listener.add_keyboard_callback(self._on_keyboard_event)
        self.input_listener.start()
        
        if model_path:
            self.load_model(model_path, lora_path)
            
    def _on_mouse_event(self, event_type: str, data: Dict):
        """Handle mouse events for monitoring"""
        if event_type == 'move':
            self.current_position = (data['x'], data['y'])
            logger.debug(f"Mouse moved to {self.current_position}")
            
    def _on_keyboard_event(self, event_type: str, data: Dict):
        """Handle keyboard events for monitoring"""
        logger.debug(f"Keyboard {event_type}: {data['key']}")
    
    def load_model(self, model_path: str, lora_path: Optional[str] = None):
        """Load the fine-tuned model and tokenizer"""
        logger.info("Loading model and tokenizer...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        if lora_path:
            # Load base model and then apply LoRA
            base_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            self.model = PeftModel.from_pretrained(base_model, lora_path)
        else:
            # Load the full fine-tuned model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
        # Create text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        logger.info("Model loaded successfully")
        
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """Generate response from the model"""
        system_prompt = "You are an enhanced cursor and keyboard control agent using pynput. Respond with ACTION: commands for precise mouse movements, clicks, scrolling, and keyboard inputs."
        
        formatted_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
        
        response = self.generator(
            formatted_prompt,
            max_new_tokens=max_length,
            temperature=0.1,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            return_full_text=False
        )
        
        return response[0]['generated_text'].strip()
    
    def parse_action_commands(self, response: str) -> List[str]:
        """Parse ACTION: commands from the model response"""
        # Look for ACTION: patterns in the response
        action_pattern = r'ACTION:\s*([^\n]+)'
        actions = re.findall(action_pattern, response, re.IGNORECASE)
        
        # Also look for commands without ACTION: prefix
        if not actions:
            # Enhanced action patterns with pynput capabilities
            patterns = [
                r'move_cursor\([^)]+\)',
                r'move_cursor_relative\([^)]+\)',
                r'mouse_click\([^)]+\)',
                r'mouse_double_click\([^)]+\)',
                r'mouse_scroll\([^)]+\)',
                r'mouse_down\([^)]+\)',
                r'mouse_up\([^)]+\)',
                r'mouse_drag\([^)]+\)',
                r'type_text\([^)]+\)',
                r'press_key\([^)]+\)',
                r'press_key_combination\([^)]+\)',
                r'hold_key\([^)]+\)',
                r'release_key\([^)]+\)'
            ]
            
            for pattern in patterns:
                actions.extend(re.findall(pattern, response))
                
        return actions
    
    def execute_action(self, action: str, real_time: bool = True):
        """Execute a single action command with enhanced pynput capabilities"""
        try:
            action = action.strip()
            logger.info(f"Executing: {action}")
            
            # Enhanced mouse movement commands with pynput
            if action.startswith('move_cursor('):
                # Extract coordinates: move_cursor(x, y, duration)
                match = re.match(r'move_cursor\((\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', action)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    duration = float(match.group(3)) if match.group(3) else 0.2
                    if real_time:
                        self.action_queue.add_action('move_cursor', (x, y, duration))
                    else:
                        self.action_queue.mouse.move_to(x, y, duration)
                        
            elif action.startswith('move_cursor_relative('):
                # Extract relative movement: move_cursor_relative(dx, dy, duration)
                match = re.match(r'move_cursor_relative\((-?\d+),\s*(-?\d+)(?:,\s*([\d.]+))?\)', action)
                if match:
                    dx, dy = int(match.group(1)), int(match.group(2))
                    duration = float(match.group(3)) if match.group(3) else 0.15
                    if real_time:
                        self.action_queue.add_action('move_cursor_relative', (dx, dy, duration))
                    else:
                        self.action_queue.mouse.move_relative(dx, dy, duration)
                        
            # Enhanced mouse click commands
            elif action.startswith('mouse_click('):
                # mouse_click(button, count)
                match = re.match(r'mouse_click\((\w+)(?:,\s*(\d+))?\)', action)
                if match:
                    button = match.group(1).lower()
                    count = int(match.group(2)) if match.group(2) else 1
                    if real_time:
                        self.action_queue.add_action('click', (button, count))
                    else:
                        self.action_queue.mouse.click(button, count)
                        
            elif action.startswith('mouse_double_click('):
                # mouse_double_click(button)
                match = re.match(r'mouse_double_click\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    if real_time:
                        self.action_queue.add_action('double_click', (button,))
                    else:
                        self.action_queue.mouse.double_click(button)
                        
            elif action.startswith('mouse_down('):
                # mouse_down(button)
                match = re.match(r'mouse_down\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    self.action_queue.add_action('mouse_down', (button,))
                    
            elif action.startswith('mouse_up('):
                # mouse_up(button)
                match = re.match(r'mouse_up\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    self.action_queue.add_action('mouse_up', (button,))
                    
            # Enhanced mouse scroll commands
            elif action.startswith('mouse_scroll('):
                # mouse_scroll(dx, dy)
                match = re.match(r'mouse_scroll\((-?\d+)(?:,\s*(-?\d+))?\)', action)
                if match:
                    dx = int(match.group(1))
                    dy = int(match.group(2)) if match.group(2) else 0
                    self.action_queue.add_action('scroll', (dx, dy))
                    
            # Enhanced mouse drag commands
            elif action.startswith('mouse_drag('):
                # mouse_drag(x, y, duration)
                match = re.match(r'mouse_drag\((\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', action)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    duration = float(match.group(3)) if match.group(3) else 0.2
                    self.action_queue.add_action('drag', (x, y, duration))
                    
            # Enhanced keyboard typing commands
            elif action.startswith('type_text('):
                # type_text('text', interval)
                match = re.match(r"type_text\('([^']+)'(?:,\s*([\d.]+))?\)", action)
                if match:
                    text = match.group(1)
                    interval = float(match.group(2)) if match.group(2) else 0.01
                    if real_time:
                        self.action_queue.add_action('type_text', (text, interval))
                    else:
                        self.action_queue.keyboard.type_text(text, interval)
                        
            # Enhanced single key press commands
            elif action.startswith('press_key('):
                # press_key('keyname')
                match = re.match(r"press_key\('([^']+)'\)", action)
                if match:
                    key = match.group(1).lower()
                    if real_time:
                        self.action_queue.add_action('press_key', (key,))
                    else:
                        self.action_queue.keyboard.press_key(key)
                        
            # Enhanced key combination commands
            elif action.startswith('press_key_combination('):
                # press_key_combination(['key1', 'key2', ...])
                match = re.match(r"press_key_combination\(\[([^\]]+)\]\)", action)
                if match:
                    keys_str = match.group(1)
                    keys = [k.strip().strip("'\"") for k in keys_str.split(',')]
                    if real_time:
                        self.action_queue.add_action('press_combination', (keys,))
                    else:
                        self.action_queue.keyboard.press_combination(keys)
                        
            # Enhanced key hold/release commands
            elif action.startswith('hold_key('):
                # hold_key('keyname')
                match = re.match(r"hold_key\('([^']+)'\)", action)
                if match:
                    key = match.group(1).lower()
                    self.action_queue.add_action('hold_key', (key,))
                    
            elif action.startswith('release_key('):
                # release_key('keyname')
                match = re.match(r"release_key\('([^']+)'\)", action)
                if match:
                    key = match.group(1).lower()
                    self.action_queue.add_action('release_key', (key,))
                    
            else:
                logger.warning(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}")
            
    def process_command(self, user_command: str, execute: bool = True, real_time: bool = True) -> Dict[str, Any]:
        """Process a user command and optionally execute the actions with enhanced real-time capabilities"""
        logger.info(f"Processing command: {user_command}")
        
        # Generate response from model
        response = self.generate_response(user_command)
        logger.info(f"Model response: {response}")
        
        # Parse actions from response
        actions = self.parse_action_commands(response)
        logger.info(f"Parsed actions: {actions}")
        
        # Execute actions if requested
        executed_actions = []
        if execute and actions:
            for action in actions:
                self.execute_action(action, real_time=real_time)
                executed_actions.append(action)
                if not real_time:
                    time.sleep(0.3)  # Small delay between actions in non-real-time mode
                
        return {
            "user_command": user_command,
            "model_response": response,
            "parsed_actions": actions,
            "executed_actions": executed_actions
        }
    
    def interactive_mode(self):
        """Run in interactive mode for testing"""
        print("Enhanced Cursor Keyboard Agent - Interactive Mode")
        print("Using pynput for advanced mouse and keyboard control")
        print("Type commands or 'quit' to exit")
        print()
        
        while True:
            try:
                user_input = input("Command: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if user_input:
                    result = self.process_command(user_input, execute=True)
                    print(f"Response: {result['model_response']}")
                    print(f"Actions executed: {len(result['executed_actions'])}")
                    print()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                
        print("Goodbye!")
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.action_queue.stop()
        self.input_listener.stop()

def main():
    """Main function to run the enhanced agent"""
    # Example usage
    agent = EnhancedCursorKeyboardAgent()
    
    # You would typically load a fine-tuned model here:
    # agent.load_model("path/to/fine-tuned-model", "path/to/lora-weights")
    
    # For now, run in interactive mode with a placeholder model
    print("Enhanced Cursor Keyboard Agent with Pynput Integration")
    print("Note: This is a demo version. To use with a fine-tuned model,")
    print("please specify the model path in the load_model() call.")
    print()
    
    # Run interactive mode
    agent.interactive_mode()

if __name__ == "__main__":
    main()