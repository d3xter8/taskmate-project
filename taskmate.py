import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random
import os
import json
import threading
import time
from datetime import datetime
import re
import winsound 
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

todo_list = [] # List to store tasks
reminder_tasks = [] # List to store reminder times
tasks_collection = [] # Placeholder for MongoDB collection
edit_task = [] # Placeholder for editing tasks

# MongoDB connection
# Ensure MongoDB is running on localhost:27017
# and the database and collection are created
client = MongoClient("mongodb://localhost:27017")
db = client["todo_app"]
collection = db["tasks"]
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully.")
except Exception as e:
    print("❌ Failed to connect to MongoDB:", e)
# Check if the collection exists

# List of motivational quotes
quotes = [
    "Write it down. Make it happen.",
    "A short pencil is better than a long memory.",
    "What gets scheduled gets done.",
    "One task at a time. One step at a time.",
    "Writing clears the mind and defines the goal.",
    "Productivity starts with the first written word.",
    "Your task list is your success blueprint.",
    "The faintest ink is more powerful than the strongest memory.",
    "Good ideas die without action. Start writing!",
    "Big goals start with small written steps."
    ]

def add_task():
    task = task_entry.get()
    if task:
        # Check for time or date pattern (e.g. "2025-05-15 14:30")
        match = re.search(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})", task)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            try:
                reminder_time = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
                reminder_tasks.append((task, reminder_time))
                task += " ⏰ [Reminder]"
            except ValueError:
                pass  # Invalid format, ignore reminder logic
        todo_list.append(task)
        task_entry.delete(0, tk.END)
        update_todo_list()
        sync_with_cloud()
    else:
        messagebox.showwarning("Warning", "Please enter a task.")

def reminder_checker():
    while True:
        now = datetime.now()
        for task, reminder_time in reminder_tasks[:]:
            if now >= reminder_time:
                # Play a beep sound
                winsound.Beep(1000, 500)  # Frequency = 1000Hz, Duration = 500ms
                # Show reminder popup
                messagebox.showinfo("Reminder", f"⏰ It's time for: {task}")
                # Remove the task from the reminder list
                reminder_tasks.remove((task, reminder_time))
        time.sleep(60)  # Check every minute
# Start the reminder checker in a separate thread

def edit_task():
    try:
        selected_index = todo_listbox.curselection()[0]
        old_task = todo_list[selected_index]
        new_task = simpledialog.askstring("Edit Task", "Update your task:", initialvalue=old_task)
        if new_task:
            todo_list[selected_index] = new_task
            update_todo_list()
            sync_with_cloud()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to edit.")

def remove_task():
    try:
        selected_task_index = todo_listbox.curselection()[0]
        removed_task = todo_list.pop(selected_task_index)
        collection.delete_one({"task": removed_task})
        update_todo_list()
        sync_with_cloud()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to remove.")

def update_todo_list():
    todo_listbox.delete(0, tk.END)
    for task in todo_list:
        todo_listbox.insert(tk.END, task)
    task_count_label.config(text=f"Total Tasks: {len(todo_list)}")

def clear_tasks():
    global todo_list
    todo_list = []
    collection.delete_many({})  # Clear all tasks from MongoDB
    update_todo_list()
    sync_with_cloud()

def sync_with_cloud():
    sync_status_label.config(text="🔄 Syncing...")
    root.update_idletasks()
    collection.delete_many({})
    for task in todo_list:
        collection.insert_one({
            "task": task,
            "timestamp": datetime.now()
        })
    sync_status_label.config(text="✅ Synced")

def load_from_cloud():
    global todo_list, reminder_tasks
    todo_list = []
    reminder_tasks = []
    cursor = list(collection.find())  # Convert cursor to list to check if it's empty
    if not cursor:
        messagebox.showinfo("Info", "No tasks found.")
        update_todo_list()  # Clear the listbox if needed
        return
    for doc in cursor:
        task = doc["task"]
        todo_list.append(task)
        # Extract reminders from task text
        match = re.search(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})", task)
        if match:
            try:
                reminder_time = datetime.strptime(match.group(1) + " " + match.group(2), "%Y-%m-%d %H:%M")
                if reminder_time > datetime.now():
                    reminder_tasks.append((task, reminder_time))
            except:
                pass
    update_todo_list()
    messagebox.showinfo("Info", "Loaded tasks from Cloud.")

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sync_with_cloud()
        root.destroy()

# UI Setup
root = tk.Tk()
root.title("Taskmate")
# Center the window on the screen
window_width = 500
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)
root.configure(bg="#2c3e50")  # Background color
icon_path = (os.path.abspath("taskmate_icon.ico"))
root.iconbitmap(icon_path)  # Set icon
root.protocol("WM_DELETE_WINDOW", on_closing)
threading.Thread(target=reminder_checker, daemon=True).start()

# Entry field
task_entry = tk.Entry(root, font=("Courier New", 14), width=30, bg="#ecf0f1", fg="#2c3e50", borderwidth=2, relief="flat")
task_entry.pack(pady=15)

# Frame to hold buttons in a 2x2 grid layout
button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=10)

# Buttons style
button_style = {"font": ("Segoe UI", 10, "bold"), "width": 15, "height": 1, "bg": "#1abc9c", "fg": "white", "activebackground": "#16a085", "bd": 0}

add_button = tk.Button(button_frame, text="➕ Add Task", command=add_task, **button_style)
add_button.grid(row=0, column=0, padx=5, pady=5)

edit_task_button = tk.Button(button_frame, text="✏️ Edit Task", command=edit_task, **button_style)
edit_task_button.grid(row=0, column=1, padx=5, pady=5)

remove_button = tk.Button(button_frame, text="❌ Delete", command=remove_task, **button_style)
remove_button.grid(row=1, column=0, padx=5, pady=5)

clear_button = tk.Button(button_frame, text="🧹 Clear all", command=clear_tasks, **button_style)
clear_button.grid(row=1, column=1, padx=5, pady=5)

load_cloud_button = tk.Button(button_frame, text="☁️ Load Tasks", command=load_from_cloud, **button_style)
load_cloud_button.grid(row=2, column=0, columnspan=2, pady=5)  # Centered across both columns

# Task Listbox
todo_listbox = tk.Listbox(root, width=40, height=12, font=("Courier New", 12), bg="#34495e", fg="white", selectbackground="#1abc9c", relief="flat", highlightthickness=0)
todo_listbox.pack(pady=15)

# Task count display
task_count_label = tk.Label(root, text="Total Tasks: 0", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 9, "bold"))
task_count_label.pack(pady=(0, 5))

# Load tasks from MongoDB on startup
sync_status_label = tk.Label(root, text="🔄 Syncing...", fg="white", bg="#2c3e50", font=("Helvetica", 9, "italic"))
sync_status_label.pack(pady=(10, 0))

# Random motivational quote footer
random_quote = random.choice(quotes)
footer = tk.Label(root, text=f"“{random_quote}”", bg="#2c3e50", fg="#f1c40f", font=("Courier New", 9, "italic"), wraplength=380, justify="center")
footer.pack(side=tk.BOTTOM, pady=10)

# Start the app
root.mainloop()

# This is a simple To-Do List application using Tkinter.    
# It allows users to add, remove, clear, save, and load tasks.
# The UI is styled with a modern look and feel.
# The app also includes a reminder feature that plays a sound and shows a popup when a task's time is reached.
# The tasks are stored in a MongoDB database, allowing for cloud synchronization.
# The app includes a motivational quote at the bottom to inspire users.
# The app is designed to be user-friendly and efficient.
# The code is structured to handle user interactions and manage the task list effectively.
# The app is built with Python and Tkinter, making it easy to run on any platform with Python installed.