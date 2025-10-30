#!/usr/bin/env python3
"""
Cursor and Keyboard Control Agent using fine-tuned Microsoft Phi Silica 3.6 model.
This agent interprets natural language commands and executes real-time cursor/keyboard actions.
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
import pyautogui
import time
import logging
import threading
from typing import List, Dict, Any, Optional
from queue import Queue, Empty

# Configure pyautogui for real-time performance
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01  # Reduced for real-time responsiveness

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeActionQueue:
    """Queue for managing real-time actions with priority"""
    def __init__(self):
        self.queue = Queue()
        self.running = True
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
                if action_type == 'move_cursor':
                    x, y, duration = args
                    pyautogui.moveTo(x, y, duration=duration)
                elif action_type == 'type_text':
                    text, interval = args
                    pyautogui.write(text, interval=interval)
                elif action_type == 'key_press':
                    key = args
                    pyautogui.press(key)
                elif action_type == 'key_combination':
                    keys = args
                    pyautogui.hotkey(*keys)
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

class CursorKeyboardAgent:
    def __init__(self, model_path: str = None, lora_path: str = None):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.action_queue = RealTimeActionQueue()
        self.current_position = pyautogui.position()
        
        if model_path:
            self.load_model(model_path, lora_path)
            
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
        system_prompt = "You are a cursor and keyboard control agent. Respond with ACTION: commands for mouse movements, clicks, scrolling, and keyboard inputs."
        
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
            # Common action patterns
            patterns = [
                r'move_cursor\([^)]+\)',
                r'mouse_click\([^)]+\)',
                r'mouse_double_click\([^)]+\)',
                r'mouse_scroll\([^)]+\)',
                r'type_text\([^)]+\)',
                r'press_key\([^)]+\)',
                r'press_key_combination\([^)]+\)',
                r'mouse_drag\([^)]+\)',
                r'mouse_down\([^)]+\)',
                r'mouse_up\([^)]+\)',
                r'move_cursor_relative\([^)]+\)'
            ]
            
            for pattern in patterns:
                actions.extend(re.findall(pattern, response))
                
        return actions
    
    def execute_action(self, action: str, real_time: bool = True):
        """Execute a single action command with real-time capabilities"""
        try:
            action = action.strip()
            logger.info(f"Executing: {action}")
            
            # Update current position
            self.current_position = pyautogui.position()
            
            # Mouse movement commands
            if action.startswith('move_cursor('):
                # Extract coordinates: move_cursor(x, y)
                match = re.match(r'move_cursor\((\d+),\s*(\d+)\)', action)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    if real_time:
                        # Real-time smooth movement with minimal duration
                        self.action_queue.add_action('move_cursor', (x, y, 0.2))
                    else:
                        pyautogui.moveTo(x, y, duration=0.2)
                        
            elif action.startswith('move_cursor_relative('):
                # Extract relative movement: move_cursor_relative(dx, dy)
                match = re.match(r'move_cursor_relative\((-?\d+),\s*(-?\d+)\)', action)
                if match:
                    dx, dy = int(match.group(1)), int(match.group(2))
                    current_x, current_y = self.current_position
                    target_x, target_y = current_x + dx, current_y + dy
                    if real_time:
                        self.action_queue.add_action('move_cursor', (target_x, target_y, 0.15))
                    else:
                        pyautogui.moveRel(dx, dy, duration=0.15)
                        
            # Mouse click commands
            elif action.startswith('mouse_click('):
                # mouse_click(button)
                match = re.match(r'mouse_click\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    if real_time:
                        # Immediate click in real-time queue
                        threading.Thread(target=lambda: pyautogui.click(button=button), daemon=True).start()
                    else:
                        pyautogui.click(button=button)
                        
            elif action.startswith('mouse_double_click('):
                # mouse_double_click(button)
                match = re.match(r'mouse_double_click\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    if real_time:
                        threading.Thread(target=lambda: pyautogui.doubleClick(button=button), daemon=True).start()
                    else:
                        pyautogui.doubleClick(button=button)
                        
            elif action.startswith('mouse_down('):
                # mouse_down(button)
                match = re.match(r'mouse_down\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    pyautogui.mouseDown(button=button)
                    
            elif action.startswith('mouse_up('):
                # mouse_up(button)
                match = re.match(r'mouse_up\((\w+)\)', action)
                if match:
                    button = match.group(1).lower()
                    pyautogui.mouseUp(button=button)
                    
            # Mouse scroll commands
            elif action.startswith('mouse_scroll('):
                # mouse_scroll(clicks)
                match = re.match(r'mouse_scroll\((-?\d+)\)', action)
                if match:
                    clicks = int(match.group(1))
                    if real_time:
                        threading.Thread(target=lambda: pyautogui.scroll(clicks), daemon=True).start()
                    else:
                        pyautogui.scroll(clicks)
                        
            # Mouse drag commands
            elif action.startswith('mouse_drag('):
                # mouse_drag(x, y)
                match = re.match(r'mouse_drag\((\d+),\s*(\d+)\)', action)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    if real_time:
                        threading.Thread(target=lambda: pyautogui.dragTo(x, y, duration=0.2), daemon=True).start()
                    else:
                        pyautogui.dragTo(x, y, duration=0.2)
                        
            # Keyboard typing commands
            elif action.startswith('type_text('):
                # type_text('text')
                match = re.match(r"type_text\('([^']+)'\)", action)
                if match:
                    text = match.group(1)
                    if real_time:
                        # Real-time typing with minimal interval for physical typing feel
                        self.action_queue.add_action('type_text', (text, 0.01))
                    else:
                        pyautogui.write(text, interval=0.02)
                        
            # Single key press commands
            elif action.startswith('press_key('):
                # press_key('keyname')
                match = re.match(r"press_key\('([^']+)'\)", action)
                if match:
                    key = match.group(1).lower()
                    if real_time:
                        self.action_queue.add_action('key_press', (key,))
                    else:
                        pyautogui.press(key)
                        
            # Key combination commands
            elif action.startswith('press_key_combination('):
                # press_key_combination(['key1', 'key2', ...])
                match = re.match(r"press_key_combination\(\[([^\]]+)\]\)", action)
                if match:
                    keys_str = match.group(1)
                    keys = [k.strip().strip("'\"") for k in keys_str.split(',')]
                    if real_time:
                        self.action_queue.add_action('key_combination', (keys,))
                    else:
                        pyautogui.hotkey(*keys)
                        
            # Real-time specific commands for fine-grained control
            elif action.startswith('real_time_move('):
                # real_time_move(x, y, duration)
                match = re.match(r'real_time_move\((\d+),\s*(\d+),\s*([\d.]+)\)', action)
                if match:
                    x, y, duration = int(match.group(1)), int(match.group(2)), float(match.group(3))
                    self.action_queue.add_action('move_cursor', (x, y, duration))
                    
            elif action.startswith('real_time_type('):
                # real_time_type('text', interval)
                match = re.match(r"real_time_type\('([^']+)',\s*([\d.]+)\)", action)
                if match:
                    text, interval = match.group(1), float(match.group(2))
                    self.action_queue.add_action('type_text', (text, interval))
                    
            else:
                logger.warning(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}")
            
    def process_command(self, user_command: str, execute: bool = True, real_time: bool = True) -> Dict[str, Any]:
        """Process a user command and optionally execute the actions with real-time capabilities"""
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
        print("Cursor Keyboard Agent - Interactive Mode")
        print("Type commands or 'quit' to exit")
        print("Screen size:", self.screen_width, "x", self.screen_height)
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

def main():
    """Main function to run the agent"""
    # Example usage
    agent = CursorKeyboardAgent()
    
    # You would typically load a fine-tuned model here:
    # agent.load_model("path/to/fine-tuned-model", "path/to/lora-weights")
    
    # For now, run in interactive mode with a placeholder model
    print("Note: This is a demo version. To use with a fine-tuned model,")
    print("please specify the model path in the load_model() call.")
    print()
    
    # Run interactive mode (will work once model is loaded)
    agent.interactive_mode()

if __name__ == "__main__":
    main()