#!/usr/bin/env python3
"""
Simple system test for cursor and keyboard control setup.
This test verifies all files exist and have the correct structure without importing complex dependencies.
"""

import os
import json
import yaml
import sys

def check_file_exists(path, description):
    """Check if a file exists and print status"""
    exists = os.path.exists(path)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {path}")
    return exists

def check_directory_exists(path, description):
    """Check if a directory exists and print status"""
    exists = os.path.isdir(path)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {path}")
    return exists

def validate_json_file(path, description):
    """Validate that a file contains valid JSON"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.jsonl') or 'train' in path or 'test' in path:
                # For JSONL files, check each line
                for i, line in enumerate(f):
                    json.loads(line)
            else:
                json.load(f)
        print(f"[OK] {description}: Valid JSON")
        return True
    except Exception as e:
        print(f"[FAIL] {description}: Invalid JSON - {e}")
        return False

def validate_yaml_file(path, description):
    """Validate that a file contains valid YAML"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f"[OK] {description}: Valid YAML")
        return True
    except Exception as e:
        print(f"[FAIL] {description}: Invalid YAML - {e}")
        return False

def check_training_data_quality():
    """Check the quality and coverage of training data"""
    print("\nTraining Data Quality Check:")
    
    try:
        with open('training_data/cursor_keyboard_train.json', 'r', encoding='utf-8') as f:
            train_lines = f.readlines()
            
        with open('training_data/cursor_keyboard_test.json', 'r', encoding='utf-8') as f:
            test_lines = f.readlines()
            
        print(f"[OK] Training samples: {len(train_lines)}")
        print(f"[OK] Test samples: {len(test_lines)}")
        
        # Check action coverage
        all_actions = []
        for line in train_lines + test_lines:
            data = json.loads(line)
            for msg in data['messages']:
                if msg['role'] == 'assistant':
                    all_actions.append(msg['content'])
        
        action_patterns = [
            'move_cursor', 'mouse_click', 'mouse_double_click',
            'mouse_scroll', 'type_text', 'press_key', 'press_key_combination'
        ]
        
        coverage = {}
        for pattern in action_patterns:
            found = any(pattern in action for action in all_actions)
            coverage[pattern] = found
            status = "[OK]" if found else "[FAIL]"
            print(f"   {status} {pattern} coverage")
            
        return len(train_lines) >= 40 and len(test_lines) >= 15 and all(coverage.values())
        
    except Exception as e:
        print(f"[FAIL] Training data quality check failed: {e}")
        return False

def check_configuration_files():
    """Check that configuration files have the correct structure"""
    print("\nConfiguration Files Check:")
    
    try:
        # Check LoRA config
        with open('lora/lora.yaml', 'r') as f:
            lora_config = yaml.safe_load(f)
        
        lora_required = ['model', 'model_path', 'learning_rate', 'epochs', 'finetune_dataset']
        lora_ok = all(field in lora_config for field in lora_required)
        print(f"[OK] LoRA configuration: {len(lora_config)} parameters")
        
        # Check Soft Prompt config
        with open('soft_prompt/soft_prompt.yaml', 'r') as f:
            soft_config = yaml.safe_load(f)
        
        soft_required = ['model', 'model_path', 'learning_rate', 'epochs', 'finetune_dataset', 'init_prompt']
        soft_ok = all(field in soft_config for field in soft_required)
        print(f"[OK] Soft Prompt configuration: {len(soft_config)} parameters")
        
        return lora_ok and soft_ok
        
    except Exception as e:
        print(f"[FAIL] Configuration check failed: {e}")
        return False

def main():
    """Run the complete system test"""
    print("Cursor Keyboard Control System Test")
    print("=" * 50)
    
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    all_checks_passed = True
    
    # Check directory structure
    print("\nDirectory Structure Check:")
    directories = [
        ('training_data', 'Training data directory'),
        ('training_scripts', 'Training scripts directory'),
        ('inference', 'Inference code directory'),
        ('test', 'Test directory'),
        ('lora', 'LoRA configuration directory'),
        ('soft_prompt', 'Soft Prompt configuration directory')
    ]
    
    for dir_path, description in directories:
        if not check_directory_exists(dir_path, description):
            all_checks_passed = False
    
    # Check training data files
    print("\nTraining Data Files:")
    data_files = [
        ('training_data/cursor_keyboard_train.json', 'Training data file'),
        ('training_data/cursor_keyboard_test.json', 'Test data file')
    ]
    
    for file_path, description in data_files:
        if check_file_exists(file_path, description):
            if not validate_json_file(file_path, description):
                all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check configuration files
    print("\nConfiguration Files:")
    config_files = [
        ('lora/lora.yaml', 'LoRA configuration'),
        ('soft_prompt/soft_prompt.yaml', 'Soft Prompt configuration'),
        ('model_project.config', 'Project configuration'),
        ('requirements.txt', 'Requirements file')
    ]
    
    for file_path, description in config_files:
        if check_file_exists(file_path, description):
            if file_path.endswith('.yaml'):
                if not validate_yaml_file(file_path, description):
                    all_checks_passed = False
            elif file_path.endswith('.json'):
                if not validate_json_file(file_path, description):
                    all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check training scripts
    print("\nTraining Scripts:")
    script_files = [
        ('training_scripts/train_cursor_keyboard_lora.py', 'LoRA training script'),
        ('training_scripts/train_cursor_keyboard_soft_prompt.py', 'Soft Prompt training script')
    ]
    
    for file_path, description in script_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check inference code
    print("\nInference Code:")
    inference_files = [
        ('inference/cursor_keyboard_agent.py', 'Cursor keyboard agent')
    ]
    
    for file_path, description in inference_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Run quality checks
    if not check_training_data_quality():
        all_checks_passed = False
        
    if not check_configuration_files():
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("SUCCESS: All system checks passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run LoRA training: python training_scripts/train_cursor_keyboard_lora.py")
        print("3. Run Soft Prompt training: python training_scripts/train_cursor_keyboard_soft_prompt.py")
        print("4. Test the agent: python inference/cursor_keyboard_agent.py")
    else:
        print("WARNING: Some checks failed. Please review the issues above.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)