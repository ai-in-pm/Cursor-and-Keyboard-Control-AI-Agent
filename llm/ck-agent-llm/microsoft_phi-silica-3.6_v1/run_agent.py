#!/usr/bin/env python3
"""
Command-line interface for the Cursor and Keyboard Control Agent.
This script allows running the agent directly from the command line.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from inference.simple_cursor_agent import SimpleCursorKeyboardAgent
from inference.advanced_os_automation_agent import AdvancedOSAutomationAgent

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_cursor_keyboard_agent(command=None, interactive=False, model_path=None, lora_path=None):
    """Run the cursor and keyboard control agent"""
    print("Initializing Simple Cursor and Keyboard Control Agent...")
    
    agent = SimpleCursorKeyboardAgent()
    
    # Model loading is not supported in simple agent
    if model_path or lora_path:
        print("Warning: Model loading is not supported in simple agent mode")
    
    if interactive:
        print("Starting interactive mode...")
        agent.interactive_mode()
    elif command:
        print(f"Executing command: {command}")
        result = agent.execute_command(command)
        status = "SUCCESS" if result['success'] else "FAILED"
        print(f"{status}: {result['message']}")
    else:
        print("No command provided. Use --interactive for interactive mode or --command to execute a single command.")
        return 1
    
    return 0

def run_os_automation_agent(command=None, interactive=False):
    """Run the advanced OS automation agent"""
    print("Initializing Advanced OS Automation Agent...")
    
    agent = AdvancedOSAutomationAgent()
    
    if interactive:
        print("Starting interactive mode...")
        print("Available commands:")
        print("  - file_operations(operation, source, [destination])")
        print("  - system_monitoring(operation)")
        print("  - application_operations(operation, [app_name], [app_path])")
        print("  - browser_operations(operation, [url], [element], [text])")
        print("  - perform_complex_task(description)")
        print("  - get_system_info()")
        print("  - get_task_history()")
        print()
        
        while True:
            try:
                user_input = input("OS Agent> ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input:
                    # Try to evaluate as Python expression
                    try:
                        result = eval(f"agent.{user_input}")
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"Error: {e}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    elif command:
        print(f"Executing complex task: {command}")
        result = agent.perform_complex_task(command)
        print(f"Task result: {result['status']}")
        if 'steps' in result:
            for i, step in enumerate(result['steps'], 1):
                print(f"  Step {i}: {step}")
    else:
        print("No command provided. Use --interactive for interactive mode or --command to execute a single command.")
        return 1
    
    return 0

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Cursor and Keyboard Control Agent - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run cursor/keyboard agent in interactive mode
  python run_agent.py --agent cursor --interactive
  
  # Execute a single cursor command
  python run_agent.py --agent cursor --command "move cursor to top left"
  
  # Run OS automation agent
  python run_agent.py --agent os --command "create file and check system resources"
  
  # Run with verbose logging
  python run_agent.py --agent cursor --command "type hello world" --verbose
        """
    )
    
    parser.add_argument(
        '--agent', 
        choices=['cursor', 'os'], 
        default='cursor',
        help='Which agent to run (cursor: cursor/keyboard control, os: OS automation)'
    )
    
    parser.add_argument(
        '--command', 
        type=str,
        help='Command to execute (e.g., "move cursor to center")'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--model-path', 
        type=str,
        help='Path to fine-tuned model (for cursor agent)'
    )
    
    parser.add_argument(
        '--lora-path', 
        type=str,
        help='Path to LoRA weights (for cursor agent)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate arguments
    if not args.command and not args.interactive:
        parser.error("Either --command or --interactive must be specified")
    
    if args.command and args.interactive:
        parser.error("Cannot specify both --command and --interactive")
    
    try:
        if args.agent == 'cursor':
            return run_cursor_keyboard_agent(
                command=args.command,
                interactive=args.interactive,
                model_path=args.model_path,
                lora_path=args.lora_path
            )
        elif args.agent == 'os':
            return run_os_automation_agent(
                command=args.command,
                interactive=args.interactive
            )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())