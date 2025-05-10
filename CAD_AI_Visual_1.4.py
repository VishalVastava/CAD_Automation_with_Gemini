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
        update_visuals()  # Refresh visual display after execution
    except Exception as e:
        error_text = traceback.format_exc()
        with open(LOG_FILE, "a") as f:
            f.write(error_text)
        status_label.config(text="Execution error.")
        if messagebox.askyesno("Execution Error", "An error occurred.\nWould you like to see details?"):
            messagebox.showerror("Error Details", error_text)

# ========== GUI Interface ========== #
def create_gui():
    global status_label, canvas

    window = tk.Tk()
    window.title("AutoCAD Gemini Copilot - Advanced v3.0")
    window.geometry("1080x780")

    # Main Frame - Split Left/Right
    main_frame = tk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Left Frame (Commands)
    left_frame = tk.Frame(main_frame, width=400)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Prompt Entry
    tk.Label(left_frame, text="Your Prompt:").pack(anchor='w', padx=10, pady=2)
    prompt_entry = tk.Entry(left_frame, width=40)
    prompt_entry.pack(padx=10)

    # Buttons Frame
    btn_frame = tk.Frame(left_frame)
    tk.Button(btn_frame, text="Generate Code", command=lambda: on_generate(prompt_entry, code_display, mode_var)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear All", command=lambda: on_clear(prompt_entry, code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Run in AutoCAD", command=lambda: on_run(code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Undo", command=on_undo).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Redo", command=on_redo).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save Code", command=lambda: on_save_code(code_display)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Show History", command=on_load_prompt_history).pack(side=tk.LEFT, padx=5)
    btn_frame.pack(pady=10)

    # Mode Selector
    mode_frame = tk.Frame(left_frame)
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
    tk.Label(left_frame, text="Generated Python Code:").pack(anchor='w', padx=10)
    code_display = scrolledtext.ScrolledText(left_frame, width=40, height=10)
    code_display.pack(padx=10)

    # Drawing Summary Panel
    tk.Label(left_frame, text="Drawing Summary:").pack(anchor='w', padx=10, pady=(10, 0))
    context_display = scrolledtext.ScrolledText(left_frame, width=40, height=5)
    context_display.pack(padx=10)
    tk.Button(left_frame, text="Refresh Drawing Context", command=lambda: on_refresh_context(context_display)).pack(pady=5)

    # Right Frame (Visual Display)
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Canvas for Visuals
    canvas = tk.Canvas(right_frame, bg="white", width=680, height=780)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Status Bar
    status_label = tk.Label(window, text="Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    window.mainloop()
    
# ========== Update Visuals (existing + generated) ========== #
def update_visuals():
    canvas.delete("all")  # Clear the canvas first
    
    # Draw the existing AutoCAD drawing
    for entity in acad.iter_objects(['Line', 'Circle', 'Polyline', 'Text', 'MText']):
        if entity.ObjectName == 'AcDbLine':
            start, end = entity.StartPoint, entity.EndPoint
            canvas.create_line(start[0], start[1], end[0], end[1], fill="black")
        elif entity.ObjectName == 'AcDbCircle':
            center, radius = entity.Center, entity.Radius
            canvas.create_oval(center[0] - radius, center[1] - radius,
                               center[0] + radius, center[1] + radius, outline="black")
        elif entity.ObjectName == 'AcDbPolyline':
            points = [APoint(p[0], p[1]) for p in entity.GetVertices()]
            canvas.create_polygon([(p[0], p[1]) for p in points], outline="black", fill="")
        elif entity.ObjectName in ['AcDbText', 'AcDbMText']:
            text = entity.TextString
            pos = entity.InsertionPoint
            canvas.create_text(pos[0], pos[1], text=text, fill="black", anchor=tk.NW)
    
    # Now overlay generated shapes (if any)
    if hasattr(update_visuals, 'generated_code_entities'):
        for entity in update_visuals.generated_code_entities:
            if isinstance(entity, dict):
                # Draw the generated entity (example: a generated line or circle)
                if entity["type"] == "Line":
                    start, end = entity["start"], entity["end"]
                    canvas.create_line(start[0], start[1], end[0], end[1], fill="blue", dash=(4, 2))
                elif entity["type"] == "Circle":
                    center, radius = entity["center"], entity["radius"]
                    canvas.create_oval(center[0] - radius, center[1] - radius,
                                       center[0] + radius, center[1] + radius, outline="blue", dash=(4, 2))
                elif entity["type"] == "Text":
                    text = entity["text"]
                    pos = entity["position"]
                    canvas.create_text(pos[0], pos[1], text=text, fill="blue", anchor=tk.NW)

# Call this function when the new code is generated
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
        
        # Store generated entities (lines, circles, etc.) for overlay
        generated_entities = []
        exec(code, {}, {"acad": acad, "APoint": APoint, "generated_entities": generated_entities})
        update_visuals.generated_code_entities = generated_entities  # Store generated entities for later use
        update_visuals()  # Refresh visuals with the updated drawing
        
    except Exception as e:
        status_label.config(text="Error generating code.")
        messagebox.showerror("Gemini Error", f"Error: {e}")

# Other handlers (on_clear, on_run, etc.) remain the same.

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
