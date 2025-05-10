# AutoCAD Gemini Copilot - Enhanced v3.0 by Vishal Vastava
# All-new features: externalized API key, Clear All, status bar, improved UX, better error handling.

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import google.generativeai as genai
from pyautocad import Autocad, APoint
import traceback
import datetime
import os

# ========== CONFIG ========== #
def load_api_key():
    try:
        with open("config.txt", "r") as f:
            key = f.read().strip()
            if not key:
                raise ValueError("Empty API key")
            return key
    except Exception:
        messagebox.showerror(
            "API Key Missing",
            "Please create a file named 'config.txt' with your Gemini API key."
        )
        exit()

GEMINI_API_KEY = load_api_key()
LOG_FILE = "autocad_gemini_log.txt"
CODE_HISTORY_FILE = "code_history.txt"
PROMPT_MEMORY_FILE = "prompt_memory.txt"

# ========== INIT Gemini ========== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ========== INIT AutoCAD ========== #
acad = Autocad(create_if_not_exists=True)

# ========== Undo/Redo Stacks ========== #
undo_stack = []
redo_stack = []

# ========== Drawing Summary ========== #
def get_drawing_summary():
    try:
        summary = []
        counts = {'Line': 0, 'Circle': 0, 'Polyline': 0, 'Text': 0}
        for entity in acad.iter_objects(['Line', 'Circle', 'Polyline', 'Text', 'MText']):
            layer = entity.Layer
            if entity.ObjectName == 'AcDbLine':
                start, end = entity.StartPoint, entity.EndPoint
                summary.append(f"[{layer}] Line from {start} to {end}")
                counts['Line'] += 1
            elif entity.ObjectName == 'AcDbCircle':
                center, radius = entity.Center, entity.Radius
                summary.append(f"[{layer}] Circle at {center} with radius {radius}")
                counts['Circle'] += 1
            elif entity.ObjectName == 'AcDbPolyline':
                summary.append(f"[{layer}] Polyline with {entity.NumberOfVertices} vertices")
                counts['Polyline'] += 1
            elif entity.ObjectName in ['AcDbText', 'AcDbMText']:
                summary.append(f"[{layer}] Text: {entity.TextString}")
                counts['Text'] += 1
        count_summary = "\n".join([f"{k}s: {v}" for k, v in counts.items()])
        details = "\n".join(summary) if summary else "No entities."
        return f"Entities Count:\n{count_summary}\n\nDetails:\n{details}"
    except Exception as e:
        return f"Error reading drawing: {e}"

# ========== Gemini Prompt ========== #
def ask_gemini(prompt_text, mode="default"):  
    context = get_drawing_summary()  
    prompt = f"""
You are an AutoCAD assistant using pyautocad in Python.

Drawing mode: {mode}
Current drawing context:
{context}

User prompt: {prompt_text}

Respond ONLY with Python code using pyautocad. Do not include explanations.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# ========== Save Command/Prompt History ========== #
def save_code_to_file(code):
    with open(CODE_HISTORY_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n--- {timestamp} ---\n{code}\n")


def save_prompt(prompt):
    with open(PROMPT_MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{prompt}\n")

# ========== Run Code ========== #
def run_code(code):
    try:
        exec_globals = {"acad": acad, "APoint": APoint}
        exec(code, exec_globals)
        undo_stack.append(code)
        save_code_to_file(code)
        status_label.config(text="Code executed successfully.")
        messagebox.showinfo("Success", "Code executed successfully.")
    except Exception as e:
        error_text = traceback.format_exc()
        with open(LOG_FILE, "a") as f:
            f.write(error_text)
        status_label.config(text="Execution error.")
        if messagebox.askyesno("Execution Error", "An error occurred.\nWould you like to see details?"):
            messagebox.showerror("Error Details", error_text)

# ========== GUI Interface ========== #
def create_gui():
    global status_label
    window = tk.Tk()
    window.title("AutoCAD Gemini Copilot - Advanced v3.0")
    window.geometry("1080x780")

    # Prompt Entry
    tk.Label(window, text="Your Prompt:").pack(anchor='w', padx=10, pady=2)
    prompt_entry = tk.Entry(window, width=120)
    prompt_entry.pack(padx=10)

    # Buttons Frame
    btn_frame = tk.Frame(window)
    tk.Button(btn_frame, text="Generate Code", command=lambda: on_generate(prompt_entry, code_display, mode_var)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear All", command=lambda: on_clear(prompt_entry, code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Run in AutoCAD", command=lambda: on_run(code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Undo", command=on_undo).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Redo", command=on_redo).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save Code", command=lambda: on_save_code(code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Show History", command=on_load_prompt_history).pack(side=tk.LEFT, padx=5)
    btn_frame.pack(pady=10)

    # Mode Selector
    mode_frame = tk.Frame(window)
    tk.Label(mode_frame, text="Drawing Mode:").pack(side=tk.LEFT)
    mode_var = tk.StringVar(value="default")
    tk.OptionMenu(
        mode_frame, mode_var,
        "default", "layer info", "group insert", "annotation",
        "dimension", "block insert", "sketch assist", "offset",
        "mirror", "hatch", "erase", "text insert",
        "polyline", "smart wall", "symbol add"
    ).pack(side=tk.LEFT)
    mode_frame.pack(anchor='w', padx=10)

    # Code Display
    tk.Label(window, text="Generated Python Code:").pack(anchor='w', padx=10)
    code_display = scrolledtext.ScrolledText(window, width=130, height=20)
    code_display.pack(padx=10)

    # Drawing Summary Panel
    tk.Label(window, text="Drawing Summary:").pack(anchor='w', padx=10, pady=(10,0))
    context_display = scrolledtext.ScrolledText(window, width=130, height=10)
    context_display.pack(padx=10)
    tk.Button(window, text="Refresh Drawing Context", command=lambda: on_refresh_context(context_display)).pack(pady=5)

    # Status Bar
    status_label = tk.Label(window, text="Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    window.mainloop()

# ========== Button Handlers & Utilities ========== #
def on_generate(prompt_entry, code_display, mode_var):
    prompt = prompt_entry.get().strip()
    if not prompt:
        messagebox.showwarning("Input Required", "Please enter a prompt.")
        return
    if undo_stack:
        if not messagebox.askyesno("Warning", "Generating new code will reset undo history. Continue?"):
            return
    mode = mode_var.get()
    save_prompt(prompt)
    try:
        code = ask_gemini(prompt, mode)
        code_display.delete(1.0, tk.END)
        code_display.insert(tk.END, code)
        status_label.config(text="Code generated.")
    except Exception as e:
        status_label.config(text="Error generating code.")
        messagebox.showerror("Gemini Error", f"Error: {e}")


def on_clear(prompt_entry, code_display):
    prompt_entry.delete(0, tk.END)
    code_display.delete(1.0, tk.END)
    status_label.config(text="Cleared prompt and code.")


def on_run(code_display):
    code = code_display.get(1.0, tk.END).strip()
    if code:
        run_code(code)


def on_undo():
    if undo_stack:
        last = undo_stack.pop()
        redo_stack.append(last)
        status_label.config(text="Undo performed.")
        messagebox.showinfo("Undo", "Undo completed (manual redraw may be needed).")
    else:
        messagebox.showinfo("Undo", "No actions to undo.")


def on_redo():
    if redo_stack:
        redo_code = redo_stack.pop()
        run_code(redo_code)
    else:
        messagebox.showinfo("Redo", "Nothing to redo.")


def on_save_code(code_display):
    code = code_display.get(1.0, tk.END).strip()
    if not code:
        messagebox.showinfo("Empty", "No code to save.")
        return
    save_code_to_file(code)
    status_label.config(text="Code saved to history.")


def on_load_prompt_history():
    if os.path.exists(PROMPT_MEMORY_FILE):
        with open(PROMPT_MEMORY_FILE, "r", encoding="utf-8") as f:
            history = f.read()
        messagebox.showinfo("Prompt History", history)
    else:
        messagebox.showinfo("Prompt History", "No prompt history found.")


def on_refresh_context(context_display):
    context = get_drawing_summary()
    context_display.delete(1.0, tk.END)
    context_display.insert(tk.END, context)

# ========== START APP ========== #
if __name__ == "__main__":
    create_gui()