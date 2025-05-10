'''
========== AutoCAD Gemini Copilot =========
This script integrates Google Gemini AI with AutoCAD using pyautocad.
It allows users to generate AutoCAD commands based on natural language prompts.
It provides a GUI for user interaction and includes undo/redo functionality.
============================================
This script is designed to work with AutoCAD and requires the pyautocad library.
It also requires the Google Gemini API for AI generation.
It is important to have the necessary permissions and API keys to use these services.
============================================
Author: Vishal Vastava
Date: 10-05-2025
Version: 1.0
============================================
'''

import tkinter as tk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai
from pyautocad import Autocad, APoint
import traceback

# ========== CONFIG ========== #
GEMINI_API_KEY = "AIzaSyDbG38EbHSqY46F208LJlN7YngrvIllOm0"  # Replace this with your actual API key
# Gemini Studio:  https://aistudio.google.com/app/apikey

# ========== INIT Gemini ========== #
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ========== INIT AutoCAD ========== #
acad = Autocad(create_if_not_exists=True)

# ========== Undo/Redo ========== #
undo_stack = []
redo_stack = []

# ========== Drawing Summary ========== #
def get_drawing_summary():
    try:
        summary = []
        for entity in acad.iter_objects(['Line', 'Circle', 'Polyline', 'Text', 'MText']):
            layer = entity.Layer
            if entity.ObjectName == 'AcDbLine':
                start = entity.StartPoint
                end = entity.EndPoint
                summary.append(f"[{layer}] Line from {start} to {end}")
            elif entity.ObjectName == 'AcDbCircle':
                center = entity.Center
                radius = entity.Radius
                summary.append(f"[{layer}] Circle at {center} with radius {radius}")
            elif entity.ObjectName == 'AcDbPolyline':
                summary.append(f"[{layer}] Polyline with {entity.NumberOfVertices} vertices")
            elif entity.ObjectName in ['AcDbText', 'AcDbMText']:
                summary.append(f"[{layer}] Text: {entity.TextString}")
        return "\n".join(summary) if summary else "No entities in drawing."
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

# ========== Run Python Code Dynamically ========== #
def run_code(code):
    try:
        exec_globals = {"acad": acad, "APoint": APoint}
        exec(code, exec_globals)
        undo_stack.append(code)
        messagebox.showinfo("Success", "Code executed successfully.")
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Execution Error", f"{str(e)}")

# ========== GUI Interface ========== #
def create_gui():
    window = tk.Tk()
    window.title("AutoCAD Gemini Copilot")
    window.geometry("950x700")

    tk.Label(window, text="Your Prompt:").pack(pady=5)
    prompt_entry = tk.Entry(window, width=100)
    prompt_entry.pack(pady=5)

    mode_frame = tk.Frame(window)
    tk.Label(mode_frame, text="Drawing Mode:").pack(side=tk.LEFT)
    mode_var = tk.StringVar(value="default")
    tk.OptionMenu(mode_frame, mode_var, "default", "layer info", "group insert", "annotation").pack(side=tk.LEFT)
    mode_frame.pack()

    tk.Label(window, text="Generated Code:").pack(pady=5)
    code_display = scrolledtext.ScrolledText(window, width=115, height=18)
    code_display.pack()

    def on_generate():
        prompt = prompt_entry.get().strip()
        if not prompt:
            messagebox.showwarning("Missing Input", "Please enter a prompt.")
            return
        mode = mode_var.get()
        code = ask_gemini(prompt, mode=mode)
        code_display.delete(1.0, tk.END)
        code_display.insert(tk.END, code)

    def on_run():
        code = code_display.get(1.0, tk.END).strip()
        if code:
            run_code(code)

    def on_undo():
        if undo_stack:
            last = undo_stack.pop()
            redo_stack.append(last)
            messagebox.showinfo("Undo", "Last action undone (manual intervention may be needed).")
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")

    def on_redo():
        if redo_stack:
            redo_code = redo_stack.pop()
            run_code(redo_code)
        else:
            messagebox.showinfo("Redo", "Nothing to redo.")

    button_frame = tk.Frame(window)
    tk.Button(button_frame, text="Generate Code", command=on_generate).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Run in AutoCAD", command=on_run).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Undo", command=on_undo).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Redo", command=on_redo).pack(side=tk.LEFT, padx=5)
    button_frame.pack(pady=10)

    tk.Label(window, text="Drawing Context:").pack(pady=5)
    context_display = scrolledtext.ScrolledText(window, width=115, height=10)
    context_display.pack()

    def refresh_context():
        context = get_drawing_summary()
        context_display.delete(1.0, tk.END)
        context_display.insert(tk.END, context)

    tk.Button(window, text="Refresh Drawing Context", command=refresh_context).pack(pady=5)

    window.mainloop()

# ========== START APP ========== #
if __name__ == "__main__":
    create_gui()
