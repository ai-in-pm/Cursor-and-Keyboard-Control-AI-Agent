#!/usr/bin/env python3
"""
Training script for cursor and keyboard control using Soft Prompt fine-tuning
on Microsoft Phi Silica 3.6 model.
"""

import os
import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import PromptTuningConfig, PromptTuningInit, get_peft_model, TaskType
from datasets import Dataset
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoftPromptCursorKeyboardTrainer:
    def __init__(self, model_name="microsoft/Phi-3.6-mini-instruct", output_dir="./cursor_keyboard_soft_prompt"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.model = None
        self.tokenizer = None
        self.soft_prompt_config = None
        
    def load_model_and_tokenizer(self):
        """Load the base model and tokenizer"""
        logger.info(f"Loading model: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        logger.info("Model and tokenizer loaded successfully")
        
    def setup_soft_prompt(self):
        """Configure Soft Prompt tuning"""
        self.soft_prompt_config = PromptTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            prompt_tuning_init=PromptTuningInit.TEXT,
            num_virtual_tokens=128,
            prompt_tuning_init_text="Control cursor and keyboard actions. Respond with ACTION: commands for mouse movements, clicks, scrolling, and keyboard inputs.",
            tokenizer_name_or_path=self.model_name,
        )
        
        self.model = get_peft_model(self.model, self.soft_prompt_config)
        self.model.print_trainable_parameters()
        
    def load_training_data(self, train_path, test_path):
        """Load and preprocess training data"""
        logger.info("Loading training data")
        
        # Load training data
        with open(train_path, 'r', encoding='utf-8') as f:
            train_data = [json.loads(line) for line in f]
            
        with open(test_path, 'r', encoding='utf-8') as f:
            test_data = [json.loads(line) for line in f]
            
        logger.info(f"Loaded {len(train_data)} training samples and {len(test_data)} test samples")
        
        # Format data for training
        def format_conversation(example):
            messages = example['messages']
            text = ""
            for msg in messages:
                if msg['role'] == 'system':
                    text += f"<|system|>\n{msg['content']}<|end|>\n"
                elif msg['role'] == 'user':
                    text += f"<|user|>\n{msg['content']}<|end|>\n"
                elif msg['role'] == 'assistant':
                    text += f"<|assistant|>\n{msg['content']}<|end|>\n"
            return {'text': text}
        
        train_formatted = [format_conversation(item) for item in train_data]
        test_formatted = [format_conversation(item) for item in test_data]
        
        train_dataset = Dataset.from_list(train_formatted)
        test_dataset = Dataset.from_list(test_formatted)
        
        return train_dataset, test_dataset
    
    def tokenize_data(self, dataset):
        """Tokenize the dataset"""
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def train(self, train_dataset, eval_dataset):
        """Train the model"""
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=1,
            evaluation_strategy="steps",
            eval_steps=16,
            save_steps=32,
            logging_steps=10,
            learning_rate=5e-05,
            warmup_steps=50,
            lr_scheduler_type="cosine",
            weight_decay=0.01,
            fp16=True,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to=None  # Disable wandb/tensorboard
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        logger.info("Starting training...")
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        logger.info(f"Training completed. Model saved to {self.output_dir}")
        
    def run_training(self, train_path, test_path):
        """Run the complete training pipeline"""
        self.load_model_and_tokenizer()
        self.setup_soft_prompt()
        
        train_dataset, test_dataset = self.load_training_data(train_path, test_path)
        tokenized_train = self.tokenize_data(train_dataset)
        tokenized_test = self.tokenize_data(test_dataset)
        
        self.train(tokenized_train, tokenized_test)

def main():
    """Main function to run training"""
    # Paths to training data
    train_path = "./training_data/cursor_keyboard_train.json"
    test_path = "./training_data/cursor_keyboard_test.json"
    
    # Create output directory
    os.makedirs("./cursor_keyboard_soft_prompt", exist_ok=True)
    
    # Initialize and run trainer
    trainer = SoftPromptCursorKeyboardTrainer()
    trainer.run_training(train_path, test_path)

if __name__ == "__main__":
    main()