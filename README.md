# AutoCAD Gemini Copilot - Enhanced v2.0

**Created by Vishal Vastava**

AutoCAD Gemini Copilot is an intelligent assistant that integrates [Google Gemini](https://ai.google) and AutoCAD automation using `pyautocad`. It helps users generate and run Python code for AutoCAD drawings using natural language prompts.

---

## ✨ Features

- 🧠 **AI-Powered Code Generation**: Uses Google Gemini to generate `pyautocad` Python scripts based on your drawing and prompt.
- 📊 **Drawing Summary**: Automatically summarizes lines, circles, text, polylines, and more from your current AutoCAD drawing.
- 🛠️ **Run Directly in AutoCAD**: Execute generated code inside AutoCAD instantly.
- ↩️ **Undo / Redo Stack**: Supports undo and redo of generated commands (manual redraw may be required).
- 💾 **Code & Prompt History**: Saves every executed code and prompt for review and reuse.
- 🖼️ **Context Modes**: Customize code generation based on drawing context like annotation, hatch, block insert, etc.
- 🖥️ **Modern GUI**: Built using `tkinter`, with interactive inputs, options, and log display.

---

## 🔧 Requirements

- **Python 3.7+**
- **AutoCAD (with COM support enabled)**
- **Installed Python packages:**
  ```bash
  pip install pyautocad google-generativeai
  ```

---

## 🗂 File Overview

| File Name                | Description                                  |
|-------------------------|----------------------------------------------|
| `main.py`               | Main application script (this file)          |
| `autocad_gemini_log.txt`| Error log file                               |
| `code_history.txt`      | Stores all previously generated codes        |
| `prompt_memory.txt`     | Stores all user prompts                      |

---

## 🚀 How to Use

1. Clone this repository or download `main.py`.
2. Make sure AutoCAD is installed and open.
3. Run the script:
   ```bash
   python main.py
   ```
4. Enter a prompt (e.g., "Draw a rectangle on layer Walls").
5. Choose a drawing mode (optional).
6. Click **Generate Code**.
7. Review and click **Run in AutoCAD** to execute.

---

## 🔐 API Key

Make sure to replace the `GEMINI_API_KEY` value with your valid [Google Gemini API Key](https://makersuite.google.com/app/apikey).

```python
GEMINI_API_KEY = "your_api_key_here"
```

---

## ⚠️ Disclaimer

- This tool is for educational and productivity use.
- Always review generated code before execution in production drawings.

---

## 📄 License

Apache 2.0 License. See `LICENSE` file (copyright is held with the developer).

---

## 🤝 Contribute

Pull requests and feedback are welcome!

---

## 📬 Contact

**Vishal Vastava**

You can connect on [LinkedIn](https://www.linkedin.com/VishalVastava) or email for queries, feedback, or enhancements.

