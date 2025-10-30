#!/usr/bin/env python3
"""
Modern Chat Interface for Cursor and Keyboard Control Agent
Integrated with Microsoft Phi Silica 3.6 LLM system
"""

import math
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox

# Add the agent directory to path
agent_path = os.path.join(os.path.dirname(__file__), 'llm', 'ck-agent-llm', 'microsoft_phi-silica-3.6_v1')
sys.path.insert(0, agent_path)

try:
    from PIL import ImageTk, Image, ImageOps
except:
    print('Installing PIL.')
    subprocess.check_call(['pip', 'install', 'pillow'])
    print('Done.')
    from PIL import ImageTk, Image, ImageOps

# Import agent modules
try:
    from inference.simple_cursor_agent import SimpleCursorKeyboardAgent
    from inference.advanced_os_automation_agent import AdvancedOSAutomationAgent

    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Agent import error: {e}")
    AGENT_AVAILABLE = False


class ChatGUI:
    def __init__(self):
        self.main = Tk()
        self.main.title('AI Agent - Chat Interface')

        # DPI handling
        self.dpiError = False
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            print('ERROR. Could not set DPI awareness.')
            self.dpiError = True

        if self.dpiError:
            dpi = 96
        else:
            dpi = self.main.winfo_fpixels('1i')

        self.main.geometry('600x600')
        self.main.configure(background='#1E1E1E')
        self.main.resizable(True, True)

        # Initialize agents
        self.cursor_agent = None
        self.os_agent = None
        self.current_agent = "cursor"
        self.chat_history = []

        self.setup_gui()
        self.initialize_agents()

    def setup_gui(self):
        """Setup the modern chat interface"""
        # Main container
        main_container = Frame(self.main, bg='#1E1E1E')
        main_container.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # Header with gradient effect
        header_frame = Frame(main_container, bg='#2D2D2D', height=80)
        header_frame.pack(fill=X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Title and subtitle
        title_frame = Frame(header_frame, bg='#2D2D2D')
        title_frame.pack(fill=X, padx=20, pady=10)

        title_label = Label(title_frame,
                            text="AI Assistant",
                            font=('Arial', 12, 'bold'),
                            fg='#FFFFFF',
                            bg='#2D2D2D')
        title_label.pack(side=LEFT)

        subtitle_label = Label(title_frame,
                               text="Cursor & OS Automation",
                               font=('Arial', 12),
                               fg='#BBBBBB',
                               bg='#2D2D2D')
        subtitle_label.pack(side=LEFT, padx=(5, 0), pady=(8, 0))

        # Agent selection and status
        control_frame = Frame(header_frame, bg='#2D2D2D')
        control_frame.pack(fill=X, padx=20, pady=(0, 5))

        # Agent selection
        agent_label = Label(control_frame, text="Agent:",
                            font=('Arial', 10), fg='#BBBBBB', bg='#2D2D2D')
        agent_label.pack(side=LEFT, padx=(0, 10))

        self.agent_var = StringVar(value="cursor")
        agent_menu = OptionMenu(control_frame, self.agent_var, "cursor", "os", command=self.on_agent_change)
        agent_menu.config(font=('Arial', 10), bg='#404040', fg='white', relief=FLAT)
        agent_menu.pack(side=LEFT, padx=(0, 20))

        # Status indicator
        self.status_label = Label(control_frame,
                                  text="● Ready",
                                  font=('Arial', 12),
                                  fg='#4CAF50',
                                  bg='#2D2D2D')
        self.status_label.pack(side=LEFT)

        # Chat area
        chat_container = Frame(main_container, bg='#1E1E1E')
        chat_container.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # Chat history with modern styling
        self.chat_frame = Frame(chat_container, bg='#1E1E1E')
        self.chat_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Create a canvas and scrollbar for chat history
        self.chat_canvas = Canvas(self.chat_frame, bg='#1E1E1E', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.chat_frame, orient=VERTICAL, command=self.chat_canvas.yview)
        self.scrollable_frame = Frame(self.chat_canvas, bg='#1E1E1E')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )

        self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        self.chat_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Bind mouse wheel to scroll
        self.chat_canvas.bind("<MouseWheel>", self._on_mousewheel)

        # Input area
        input_frame = Frame(chat_container, bg='#2D2D2D', height=120)
        input_frame.pack(fill=X, padx=0, pady=0)
        input_frame.pack_propagate(False)

        # Input area with send button
        input_inner_frame = Frame(input_frame, bg='#2D2D2D')
        input_inner_frame.pack(fill=X, padx=20, pady=(0, 15))

        self.input_entry = Entry(input_inner_frame,
                                 font=('Arial', 12),
                                 bg='#404040',
                                 fg='#FFFFFF',
                                 insertbackground='white',
                                 relief=FLAT)
        self.input_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', lambda e: self.send_message())

        self.send_btn = Button(input_inner_frame,
                               text="Send",
                               font=('Arial', 12, 'bold'),
                               bg='#007ACC',
                               fg='white',
                               relief=FLAT,
                               command=self.send_message)
        self.send_btn.pack(side=RIGHT)

        # Add welcome message
        self.add_welcome_message()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_welcome_message(self):
        """Add welcome message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        msg_frame = Frame(self.scrollable_frame, bg='#1E1E1E')
        msg_frame.pack(fill=X, padx=10, pady=5)
        avatar_container = Frame(msg_frame, bg='#1E1E1E')
        avatar_container.pack(side=LEFT, padx=(0, 10))
        avatar = Label(avatar_container,
                       text="AI",
                       font=('Arial', 10, 'bold'),
                       bg="#4CAF50",
                       fg='white',
                       width=4,
                       height=2)
        avatar.pack()
        content_frame = Frame(msg_frame, bg='#1E1E1E')
        content_frame.pack(side=LEFT, fill=X, expand=True)
        time_label = Label(content_frame,
                           text=timestamp,
                           font=('Arial', 8),
                           fg='#888888',
                           bg='#1E1E1E')
        time_label.pack(anchor=W)
        message_bubble = Label(content_frame,
                               text="Hi there! I'm your AI assistant. I can help you control your cursor and keyboard, or automate OS tasks. What would you like me to do?",
                               font=('Arial', 11),
                               bg='#404040',
                               fg='#E0E0E0',
                               wraplength=450,
                               justify=LEFT,
                               relief=FLAT,
                               padx=8,
                               pady=8)
        message_bubble.pack(fill=X, padx=(0, 0), pady=(2, 2), anchor='w')
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def add_message(self, sender, message):
        """Add a message to the chat history and display recent turns for context"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history.append({"sender": sender, "message": message, "timestamp": timestamp})
        # Display last 6 turns for context
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for turn in self.chat_history[-6:]:
            msg_frame = Frame(self.scrollable_frame, bg='#1E1E1E')
            msg_frame.pack(fill=X, padx=10, pady=5)
            avatar_container = Frame(msg_frame, bg='#1E1E1E')
            avatar_container.pack(side=LEFT, padx=(0, 10))
            avatar_color = "#007ACC" if turn["sender"] == "user" else "#4CAF50"
            avatar_text = "You" if turn["sender"] == "user" else "AI"
            avatar = Label(avatar_container,
                           text=avatar_text,
                           font=('Arial', 10, 'bold'),
                           bg=avatar_color,
                           fg='white',
                           width=4,
                           height=2)
            avatar.pack()
            content_frame = Frame(msg_frame, bg='#1E1E1E')
            content_frame.pack(side=LEFT, fill=X, expand=True)
            time_label = Label(content_frame,
                               text=turn["timestamp"],
                               font=('Arial', 8),
                               fg='#888888',
                               bg='#1E1E1E')
            time_label.pack(anchor=W)
            bubble_color = '#007ACC' if turn["sender"] == "user" else '#404040'
            text_color = 'white' if turn["sender"] == "user" else '#E0E0E0'
            anchor = 'w'
            padx = (0, 50) if turn["sender"] == "user" else (0, 0)
            message_bubble = Label(content_frame,
                                   text=turn["message"],
                                   font=('Arial', 11),
                                   bg=bubble_color,
                                   fg=text_color,
                                   wraplength=450,
                                   justify=LEFT,
                                   relief=FLAT,
                                   padx=8,
                                   pady=8)
            message_bubble.pack(fill=X, padx=padx, pady=(2, 2), anchor=anchor)
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def initialize_agents(self):
        """Initialize the cursor and OS automation agents"""
        if not AGENT_AVAILABLE:
            self.add_message("assistant", "❌ Agent modules not available. Please check the installation.")
            return

        try:
            self.cursor_agent = SimpleCursorKeyboardAgent()
            self.os_agent = AdvancedOSAutomationAgent()
            self.add_message("assistant", "✅ Agents initialized successfully!")
            self.update_status("● Connected", "#4CAF50")
        except Exception as e:
            self.add_message("assistant", f"❌ Error initializing agents: {str(e)}")
            self.update_status("● Error", "#F44336")

    def on_agent_change(self, agent_type):
        """Handle agent type change"""
        self.current_agent = agent_type
        if agent_type == "cursor":
            self.add_message("assistant", "I'm now in Cursor & Keyboard mode. I can help you move the cursor, click, type, and more!")
        else:
            self.add_message("assistant", "I'm now in OS Automation mode. I can help you with file operations, system monitoring, and more!")

    def send_message(self, predefined_message=None):
        """Send a message/command"""
        if predefined_message:
            message = predefined_message
            self.input_entry.delete(0, END)
            self.input_entry.insert(0, message)
        else:
            message = self.input_entry.get().strip()

        if not message:
            return

        # Add user message to chat
        self.add_message("user", message)
        self.input_entry.delete(0, END)

        # Process the command
        self.process_command(message)

    def get_conversation_context(self, num_turns=3):
        """Get recent conversation context for more natural responses"""
        if len(self.chat_history) < 2:
            return ""

        # Get last few user messages to understand context
        recent_messages = []
        for turn in self.chat_history[-(num_turns * 2):]:
            if turn['sender'] == 'user':
                recent_messages.append(turn['message'])

        return " ".join(recent_messages) if recent_messages else ""

    def generate_natural_response(self, result, agent_type):
        """Generate a natural, conversational response based on the result and context"""
        # Get conversation context
        context = self.get_conversation_context()

        if agent_type == "cursor":
            if not result['success']:
                # More natural error responses with context awareness
                command_lower = result.get('command', '').lower()

                if 'move' in command_lower or 'cursor' in command_lower:
                    return "I'm not sure where you want me to move the cursor. Could you specify a location like 'center', 'top left', or specific coordinates?"
                elif 'type' in command_lower:
                    return "I didn't catch what you want me to type. Could you tell me the text you'd like me to enter?"
                elif 'click' in command_lower:
                    return "I can help you click! Just let me know if you want a left click, right click, or double click."
                else:
                    return "I'm not quite sure what you'd like me to do. I can help you move the cursor, click, type text, scroll, or press keys. What would you like?"
            else:
                # Natural success responses - the message from simple_cursor_agent is already natural
                message = result['message']

                # Check if it's a conversational response (greeting, thanks, help)
                if any(phrase in message for phrase in ["Hello!", "You're welcome", "I can help you"]):
                    # Already conversational, return as-is
                    return message

                # For action responses, make them more conversational
                if "cursor moved to" in message:
                    return f"Done! I've moved the {message}"
                elif "click performed" in message:
                    action = message.replace(" performed", "")
                    return f"Got it! I've performed a {action}."
                elif "typed" in message:
                    # Extract the typed text
                    if "'" in message:
                        return f"I've {message}"
                    else:
                        return f"Done! I've {message}"
                elif "key pressed" in message.lower() or "pressed" in message:
                    return f"Done! {message}"
                elif "scrolled" in message.lower():
                    return f"Done! I've {message}"
                elif "clipboard" in message.lower():
                    return f"Done! I've {message}"
                elif "selected all" in message.lower():
                    return f"Done! I've {message}"
                elif "saved" in message.lower():
                    return f"Done! I've {message}"
                else:
                    # Default: return the message as-is
                    return message

        elif agent_type == "os":
            if result.get('status') == 'success':
                response = "Task completed successfully!"
                if 'steps' in result and result['steps']:
                    response += "\n\nHere's what I did:"
                    for i, step in enumerate(result['steps'], 1):
                        response += f"\n  {i}. {step}"
                return response
            elif result.get('status') == 'warning':
                return f"I'm not sure how to handle that task yet. {result.get('message', '')}"
            else:
                return f"I encountered an issue: {result.get('message', 'Unknown error')}"

        return "I'm here to help! What would you like me to do?"

    def process_command(self, command):
        """Process the command and generate context-aware response"""
        if not AGENT_AVAILABLE:
            self.add_message("assistant", "The agents aren't available right now. Please check the installation.")
            return
        typing_frame = Frame(self.scrollable_frame, bg='#1E1E1E')
        typing_frame.pack(fill=X, padx=10, pady=5)
        typing_label = Label(typing_frame,
                             text="AI is thinking...",
                             font=('Arial', 10, 'italic'),
                             fg='#888888',
                             bg='#1E1E1E')
        typing_label.pack(side=LEFT, padx=(50, 0))
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

        def process():
            try:
                response = ""
                if self.current_agent == "cursor":
                    if self.cursor_agent:
                        result = self.cursor_agent.execute_command(command)
                        response = self.generate_natural_response(result, "cursor")
                    else:
                        response = "The cursor control agent isn't initialized yet."
                elif self.current_agent == "os":
                    if self.os_agent:
                        result = self.os_agent.perform_complex_task(command)
                        response = self.generate_natural_response(result, "os")
                    else:
                        response = "The OS automation agent isn't initialized yet."
            except Exception as e:
                response = f"Oops, something went wrong: {str(e)}"
            self.main.after(0, lambda: self.finish_processing(typing_frame, response))

        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

    def finish_processing(self, typing_frame, response):
        """Remove typing indicator and add the actual response"""
        typing_frame.destroy()
        self.add_message("assistant", response)

    def update_status(self, message, color="#4CAF50"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)

    def run(self):
        """Start the GUI main loop"""
        self.main.mainloop()


def main():
    """Main function to start the GUI"""
    gui = ChatGUI()
    gui.run()


if __name__ == "__main__":
    main()
