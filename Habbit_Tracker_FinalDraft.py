import sqlite3
import tkinter as tk
from tkinter import messagebox, font, ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta

# -------------------- Initialize Database --------------------
def initialize_database():
    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS habit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        date TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits (id)
    )''')
    conn.commit()
    conn.close()

# -------------------- Build Home Screen --------------------
def build_home_screen():
    frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((canvas.winfo_width() // 2, canvas.winfo_height() // 2), window=frame, anchor="center")

    # Title
    title = tk.Label(frame, text="Habit Tracker Dashboard", font=heading_font, fg="#ffffff", bg=bg_color)
    title.pack(pady=20)

    # Display habit stats
    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) FROM habits GROUP BY category")
    category_stats = cursor.fetchall()
    conn.close()

    if category_stats:
        for category, count in category_stats:
            tk.Label(frame, text=f"{category}: {count} habits", font=("Arial", 12), fg="#ffffff", bg=bg_color).pack()

    # Buttons for features
    buttons = [
        ("View All Habits", build_habit_list_screen, "#33cc33"),
        ("Add New Habit", build_add_habit_screen, "#ff9933"),
        ("View Calendar", build_calendar_view, "#0099cc"),
        ("Progress Dashboard", build_progress_dashboard, "#ff4d4d")
    ]

    for text, command, color in buttons:
        btn = tk.Button(frame, text=text, bg=color, fg="white", font=("Arial", 12, "bold"), command=lambda c=command: show_screen(c))
        btn.pack(pady=10)

    canvas.update_idletasks()

# -------------------- Add Habit Screen --------------------
def build_add_habit_screen():
    frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((canvas.winfo_width() // 2, canvas.winfo_height() // 2), window=frame, anchor="center")

    tk.Label(frame, text="Add a New Habit", font=heading_font, fg="#ff8c00", bg=bg_color).pack(pady=10)
    tk.Label(frame, text="Habit Name:", font=("Arial", 12), fg="#ffffff", bg=bg_color).pack(pady=5)
    habit_name_entry = tk.Entry(frame, font=("Arial", 12), width=30)
    habit_name_entry.pack(pady=5)

    tk.Label(frame, text="Category (e.g., Health, Productivity):", font=("Arial", 12), fg="#ffffff", bg=bg_color).pack(pady=5)
    habit_category_entry = tk.Entry(frame, font=("Arial", 12), width=30)
    habit_category_entry.pack(pady=5)

    def save_habit():
        name = habit_name_entry.get()
        category = habit_category_entry.get()
        if not name or not category:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        conn = sqlite3.connect("habit_tracker.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO habits (name, category) VALUES (?, ?)", (name, category))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Habit added!")
        show_screen(build_home_screen)

    tk.Button(frame, text="Save Habit", bg="#ff8c00", fg="white", font=("Arial", 10, "bold"),
              command=save_habit).pack(pady=20)

    canvas.update_idletasks()

# -------------------- Habit List Screen --------------------
def build_habit_list_screen():
    frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((canvas.winfo_width() // 2, canvas.winfo_height() // 2), window=frame, anchor="center")

    tk.Label(frame, text="Your Habits", font=heading_font, fg="#0066cc", bg=bg_color).pack(pady=10)

    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, streak FROM habits")
    habits = cursor.fetchall()
    conn.close()

    for habit_id, name, category, streak in habits:
        tk.Label(frame, text=f"{name} ({category}) - Streak: {streak}", font=("Arial", 12), fg="#ffffff", bg=bg_color).pack()
        tk.Button(frame, text="Complete Today", bg="#33cc33", fg="white", font=("Arial", 10, "bold"),
                  command=lambda h_id=habit_id: complete_habit(h_id)).pack(pady=5)

    canvas.update_idletasks()

# -------------------- Calendar View --------------------
def build_calendar_view():
    frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((canvas.winfo_width() // 2, canvas.winfo_height() // 2), window=frame, anchor="center")

    tk.Label(frame, text="Habit Calendar", font=heading_font, fg="#ffffff", bg=bg_color).pack(pady=10)
    cal = Calendar(frame, selectmode="day", year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
    cal.pack(pady=10)

    canvas.update_idletasks()

# -------------------- Progress Dashboard --------------------
def build_progress_dashboard():
    frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((canvas.winfo_width() // 2, canvas.winfo_height() // 2), window=frame, anchor="center")

    tk.Label(frame, text="Progress Dashboard", font=heading_font, fg="#ffffff", bg=bg_color).pack(pady=10)

    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, streak, points FROM habits")
    habits = cursor.fetchall()
    conn.close()

    for name, streak, points in habits:
        tk.Label(frame, text=f"{name} - Streak: {streak} | Points: {points}", font=("Arial", 12), fg="#ffffff", bg=bg_color).pack(pady=5)

    canvas.update_idletasks()

# -------------------- Complete Habit --------------------
def complete_habit(habit_id):
    today = str(datetime.today().date())
    conn = sqlite3.connect("habit_tracker.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM habit_log WHERE habit_id = ? AND date = ?", (habit_id, today))
    if cursor.fetchone():
        messagebox.showinfo("Info", "Already marked as complete today!")
        conn.close()
        return

    cursor.execute("INSERT INTO habit_log (habit_id, date, completed) VALUES (?, ?, 1)", (habit_id, today))
    cursor.execute("UPDATE habits SET streak = streak + 1, points = points + 10, longest_streak = \
                    CASE WHEN streak + 1 > longest_streak THEN streak + 1 ELSE longest_streak END WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Habit completed for today!")
    show_screen(build_habit_list_screen)

# -------------------- Main Application --------------------
def show_screen(screen_function):
    canvas.delete("all")  # Clear the canvas before showing a new screen
    draw_gradient_background()  # Redraw gradient background
    screen_function()

def draw_gradient_background():
    canvas.delete("gradient")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for i in range(height):
        color = f"#{int(43 + (255 - 43) * (i / height)):02x}{int(43 + (102 - 43) * (i / height)):02x}{int(43 + (255 - 43) * (i / height)):02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

initialize_database()

root = tk.Tk()
root.title("Advanced Habit Tracker")
root.geometry("800x600")

# Canvas and Scrollbar
canvas = tk.Canvas(root, bg="#2b2b2b")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Fonts and Styling
heading_font = font.Font(family="Helvetica", size=16, weight="bold")
bg_color = "#2b2b2b"

# Menu Bar
menu = tk.Menu(root, tearoff=0)
root.config(menu=menu)
menu.add_command(label="Home", command=lambda: show_screen(build_home_screen))
menu.add_command(label="Add Habit", command=lambda: show_screen(build_add_habit_screen))
menu.add_command(label="Calendar", command=lambda: show_screen(build_calendar_view))
menu.add_command(label="Progress", command=lambda: show_screen(build_progress_dashboard))

# Initial Screen
root.update_idletasks()
draw_gradient_background()
show_screen(build_home_screen)

# Handle window resizing
canvas.bind("<Configure>", lambda event: draw_gradient_background())

root.mainloop()
