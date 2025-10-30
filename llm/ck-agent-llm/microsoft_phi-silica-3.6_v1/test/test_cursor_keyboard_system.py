#!/usr/bin/env python3
"""
Test script for the cursor and keyboard control system.
This script tests the training data, model configurations, and inference setup.
"""

import os
import json
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCursorKeyboardSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.train_data_path = "../training_data/cursor_keyboard_train.json"
        self.test_data_path = "../training_data/cursor_keyboard_test.json"
        self.lora_config_path = "../lora/lora.yaml"
        self.soft_prompt_config_path = "../soft_prompt/soft_prompt.yaml"
        
    def test_training_data_exists(self):
        """Test that training data files exist and are valid JSONL"""
        # Check train data
        self.assertTrue(os.path.exists(self.train_data_path), 
                       "Training data file does not exist")
        
        with open(self.train_data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0, "Training data file is empty")
            
            # Test that each line is valid JSON
            for i, line in enumerate(lines):
                try:
                    data = json.loads(line)
                    self.assertIn('messages', data, f"Line {i+1}: Missing 'messages' key")
                    self.assertIsInstance(data['messages'], list, f"Line {i+1}: 'messages' should be a list")
                    
                    # Check message structure
                    for msg in data['messages']:
                        self.assertIn('role', msg, f"Line {i+1}: Message missing 'role'")
                        self.assertIn('content', msg, f"Line {i+1}: Message missing 'content'")
                        self.assertIn(msg['role'], ['system', 'user', 'assistant'], 
                                    f"Line {i+1}: Invalid role '{msg['role']}'")
                        
                except json.JSONDecodeError as e:
                    self.fail(f"Line {i+1}: Invalid JSON - {e}")
        
        # Check test data
        self.assertTrue(os.path.exists(self.test_data_path), 
                       "Test data file does not exist")
        
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0, "Test data file is empty")
            
            for i, line in enumerate(lines):
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    self.fail(f"Test data line {i+1}: Invalid JSON - {e}")
    
    def test_lora_config_exists(self):
        """Test that LoRA configuration file exists"""
        self.assertTrue(os.path.exists(self.lora_config_path), 
                       "LoRA configuration file does not exist")
        
    def test_soft_prompt_config_exists(self):
        """Test that Soft Prompt configuration file exists"""
        self.assertTrue(os.path.exists(self.soft_prompt_config_path), 
                       "Soft Prompt configuration file does not exist")
    
    def test_training_scripts_exist(self):
        """Test that training scripts exist"""
        scripts_dir = "../training_scripts"
        self.assertTrue(os.path.exists(scripts_dir), "Training scripts directory does not exist")
        
        lora_script = os.path.join(scripts_dir, "train_cursor_keyboard_lora.py")
        soft_prompt_script = os.path.join(scripts_dir, "train_cursor_keyboard_soft_prompt.py")
        
        self.assertTrue(os.path.exists(lora_script), "LoRA training script does not exist")
        self.assertTrue(os.path.exists(soft_prompt_script), "Soft Prompt training script does not exist")
    
    def test_inference_code_exists(self):
        """Test that inference code exists"""
        inference_dir = "../inference"
        self.assertTrue(os.path.exists(inference_dir), "Inference directory does not exist")
        
        agent_script = os.path.join(inference_dir, "cursor_keyboard_agent.py")
        self.assertTrue(os.path.exists(agent_script), "Cursor keyboard agent script does not exist")
    
    def test_requirements_exists(self):
        """Test that requirements file exists"""
        req_file = "../requirements.txt"
        self.assertTrue(os.path.exists(req_file), "Requirements file does not exist")
    
    def test_action_parsing_logic(self):
        """Test the action parsing logic from the inference code"""
        from inference.cursor_keyboard_agent import CursorKeyboardAgent
        
        agent = CursorKeyboardAgent()
        
        # Test various action patterns
        test_responses = [
            "ACTION: move_cursor(100, 200)",
            "I will move the cursor. ACTION: mouse_click(left)",
            "Here are the actions: ACTION: type_text('hello') and ACTION: press_key('enter')",
            "move_cursor(300, 400) mouse_scroll(5)",
            "No action commands here, just text"
        ]
        
        expected_actions = [
            ['move_cursor(100, 200)'],
            ['mouse_click(left)'],
            ["type_text('hello')", "press_key('enter')"],
            ['move_cursor(300, 400)', 'mouse_scroll(5)'],
            []
        ]
        
        for response, expected in zip(test_responses, expected_actions):
            actions = agent.parse_action_commands(response)
            self.assertEqual(actions, expected, 
                           f"Failed to parse actions from: {response}")
    
    @patch('pyautogui.moveTo')
    def test_action_execution_mock(self, mock_move):
        """Test action execution with mocked pyautogui"""
        from inference.cursor_keyboard_agent import CursorKeyboardAgent
        
        agent = CursorKeyboardAgent()
        
        # Test mouse movement
        agent.execute_action('move_cursor(500, 300)')
        mock_move.assert_called_once_with(500, 300, duration=0.5)
        
        # Reset mock
        mock_move.reset_mock()
        
        # Test relative movement
        agent.execute_action('move_cursor_relative(50, -25)')
        mock_move.assert_called_once()
    
    def test_data_quality(self):
        """Test the quality and coverage of training data"""
        with open(self.train_data_path, 'r', encoding='utf-8') as f:
            train_data = [json.loads(line) for line in f]
        
        with open(self.test_data_path, 'r', encoding='utf-8') as f:
            test_data = [json.loads(line) for line in f]
        
        # Check data size
        self.assertGreaterEqual(len(train_data), 40, "Training data should have at least 40 examples")
        self.assertGreaterEqual(len(test_data), 15, "Test data should have at least 15 examples")
        
        # Check action coverage
        all_actions = []
        for item in train_data + test_data:
            for msg in item['messages']:
                if msg['role'] == 'assistant':
                    all_actions.append(msg['content'])
        
        # Check for common action patterns
        action_patterns = [
            'move_cursor',
            'mouse_click',
            'mouse_double_click',
            'mouse_scroll',
            'type_text',
            'press_key',
            'press_key_combination'
        ]
        
        for pattern in action_patterns:
            found = any(pattern in action for action in all_actions)
            self.assertTrue(found, f"Action pattern '{pattern}' not found in training data")

class TestConfigurationFiles(unittest.TestCase):
    
    def test_lora_yaml_structure(self):
        """Test that LoRA YAML file has expected structure"""
        import yaml
        
        with open("../lora/lora.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = [
            'model', 'model_path', 'learning_rate', 'epochs',
            'finetune_dataset', 'finetune_train_batch_size'
        ]
        
        for field in required_fields:
            self.assertIn(field, config, f"LoRA config missing required field: {field}")
    
    def test_soft_prompt_yaml_structure(self):
        """Test that Soft Prompt YAML file has expected structure"""
        import yaml
        
        with open("../soft_prompt/soft_prompt.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = [
            'model', 'model_path', 'learning_rate', 'epochs',
            'finetune_dataset', 'init_prompt', 'number_of_virtual_tokens'
        ]
        
        for field in required_fields:
            self.assertIn(field, config, f"Soft Prompt config missing required field: {field}")

def run_all_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCursorKeyboardSystem)
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationFiles))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed! The cursor keyboard system is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Testing Cursor Keyboard Control System...")
    print("="*50)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 System is ready for training and deployment!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run LoRA training: python training_scripts/train_cursor_keyboard_lora.py")
        print("3. Run Soft Prompt training: python training_scripts/train_cursor_keyboard_soft_prompt.py")
        print("4. Test the agent: python inference/cursor_keyboard_agent.py")
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")
    
    sys.exit(0 if success else 1)