# Taskmate

Taskmate is a modern To-Do List application built with Python (Tkinter) and MongoDB. It allows users to manage tasks, set reminders, and sync tasks with MongoDB for cloud storage.

# Structure

- `taskmate.py`: Main application script containing the Tkinter GUI and task logic

- `taskmate_icon.ico`: Optional app icon for the window

## Setup

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install pymongo
```

3. Ensure MongoDB is running locally:

Database: todo_app

Collection: tasks

4. Run the app:
```bash
python taskmate.py
```

# Features

- ➕ Add, ✏️ Edit, ❌ Delete, and 🧹 Clear all tasks

- ⏰ Set reminders using YYYY-MM-DD HH:MM format

- ☁️ Sync tasks with MongoDB

 🔄 Sync status indicator

- 💡 Motivational quotes footer

- Modern, user-friendly dark-themed interface

# 💡 Future Improvements

- Add tags & categories for tasks

- Implement due date calendar picker

- Add search & filter functionality

- Cross-platform sound support (Linux/macOS)

# License

MIT
