from flask import Flask, request, jsonify
import google.generativeai as genai
from gtts import gTTS
import pygame
import io
import threading
import time
import json
import winsound  # Windows only — can remove if not needed
import tkinter as tk
from tkinter import ttk

# ─── TTS with gTTS + pygame (reliable, no "run loop not started" issue) ───────
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

def speak_text(text):
    try:
        clean = text.replace("#", "").replace("*", "").replace("**", "").replace("\n", " ").strip()
        if not clean:
            return
        
        print(f"[TTS gTTS] {clean[:80]}...")
        
        tts = gTTS(clean, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"gTTS / pygame error: {e}")

# ─── Gemini Setup ────────────────────────────────────────────────────────────
genai.configure(api_key="AIzaSyCWD_OefSONJaERN4wtL3Sox5M7hw80reQ")
MODEL_ID = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are a helpful South Asian home cooking assistant.
Create realistic, step-by-step recipes with TIMED actions.
Output ONLY valid JSON — no extra text, no markdown, no explanations, no ```json.

Exact format:
{
  "recipe_name": "Short catchy name",
  "steps": [
    {
      "step_number": 1,
      "instruction": "Clear short action sentence",
      "duration_minutes": integer (1 to 15 typical, max 30),
      "details": "very short note or empty string \"\""
    },
    ...
  ]
}

Rules:
- 5–9 steps total
- Each step MUST have its own duration_minutes > 0
- Sequential and realistic (prep → boil/wait → cook/wait → mix/wait → serve)
- South Asian style when possible
- Unique recipe every time
"""

app = Flask(__name__)

# Shared state
current_recipe = {"name": "", "steps": [], "current_step": -1}
timer_start_time = 0.0
current_duration_sec = 0
lock = threading.Lock()

def start_timer(duration_minutes):
    global timer_start_time, current_duration_sec
    with lock:
        current_duration_sec = duration_minutes * 60
        timer_start_time = time.time()
        print(f"[TIMER START] {duration_minutes} min ({current_duration_sec} sec)")  # debug

    time.sleep(duration_minutes * 60)

    try:
        winsound.Beep(1400, 400)
        winsound.Beep(1800, 300)
        winsound.Beep(1400, 400)
    except:
        speak_text("Time is up!")

    speak_text("Time finished. Scan next card when ready.")

@app.route("/recipe", methods=["POST"])
def recipe():
    data = request.json
    print("Received payload:", data)

    with lock:
        if data.get("action") == "next_step":
            if current_recipe["current_step"] < 0 or not current_recipe["steps"]:
                return jsonify({"error": "No active recipe. Scan recipe card first."}), 400

            current_recipe["current_step"] += 1

            if current_recipe["current_step"] >= len(current_recipe["steps"]):
                speak_text("Well done! Recipe is complete.")
                current_recipe.update({"name": "", "steps": [], "current_step": -1})
                return jsonify({"status": "completed"})

            step = current_recipe["steps"][current_recipe["current_step"]]
            duration = step.get("duration_minutes", 5)
            instr = f"Step {step['step_number']}: {step['instruction']}. Set timer for {duration} minutes."

            print(f"[Next step] Triggering speech for step {step['step_number']}")
            speak_text(instr)
            threading.Thread(target=start_timer, args=(duration,)).start()

            return jsonify({
                "recipe_name": current_recipe["name"],
                "step_number": step["step_number"],
                "instruction": instr,
                "remaining_steps": len(current_recipe["steps"]) - current_recipe["current_step"] - 1
            })

        else:
            # New recipe
            recipe_type = data.get("type", "general")
            try:
                model = genai.GenerativeModel(
                    model_name=MODEL_ID,
                    system_instruction=SYSTEM_INSTRUCTION,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.75,
                        "top_p": 0.92,
                        "max_output_tokens": 1800
                    }
                )

                response = model.generate_content(f"Create a detailed step-by-step {recipe_type} recipe suitable for home cooking.")

                recipe_text = response.text.strip()
                print("Raw Gemini output:\n", recipe_text, "\n───────────────")

                parsed = json.loads(recipe_text)

                current_recipe["name"] = parsed.get("recipe_name", f"{recipe_type.capitalize()} Dish")
                current_recipe["steps"] = parsed.get("steps", [])
                current_recipe["current_step"] = 0

                if not current_recipe["steps"]:
                    return jsonify({"error": "AI generated no steps"}), 500

                step = current_recipe["steps"][0]
                duration = step.get("duration_minutes", 5)
                instr = f"Starting {current_recipe['name']}. Step 1: {step['instruction']}. Set timer for {duration} minutes."

                print("[New recipe] Triggering speech for step 1")
                speak_text(instr)
                threading.Thread(target=start_timer, args=(duration,)).start()

                return jsonify({
                    "recipe_name": current_recipe["name"],
                    "step_number": 1,
                    "instruction": instr,
                    "total_steps": len(current_recipe["steps"])
                })

            except json.JSONDecodeError as je:
                print(f"JSON parse failed: {je}")
                print("Raw content:\n", recipe_text)
                return jsonify({"error": "AI response not valid JSON"}), 500
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({"error": str(e)}), 500

# ─── Tkinter UI ──────────────────────────────────────────────────────────────
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Colors (modern dark cooking app theme)
BG_COLOR        = "#1a1a1a"
ACCENT_COLOR    = "#e67e22"
TEXT_COLOR      = "#eeeeee"
SECONDARY_TEXT  = "#bbbbbb"
TIMER_ACTIVE    = "#2ecc71"
TIMER_LOW       = "#e74c3c"

def update_ui():
    with lock:
        name_label.config(text=current_recipe.get('name', 'Ready to cook'))

        if current_recipe["current_step"] >= 0 and current_recipe["steps"]:
            step_idx = current_recipe["current_step"]
            step_num = step_idx + 1
            total = len(current_recipe["steps"])
            dots = "●" * step_num + "○" * (total - step_num)
            step_label.config(text=f"Step {step_num}/{total}  {dots}", fg=ACCENT_COLOR)

            step = current_recipe["steps"][step_idx]
            instr_label.config(text=step.get('instruction', '—'))
            detail_label.config(text=step.get('details', ''), fg=SECONDARY_TEXT)
        else:
            step_label.config(text="No recipe active", fg=SECONDARY_TEXT)
            instr_label.config(text="Scan a recipe card to begin → 🍲")
            detail_label.config(text="")

        # Timer countdown
        if current_duration_sec > 0:
            elapsed = time.time() - timer_start_time
            remaining = max(0, current_duration_sec - elapsed)
            mins, secs = divmod(int(remaining), 60)
            timer_label.config(text=f"{mins:02d}:{secs:02d}")

            progress = (current_duration_sec - remaining) / current_duration_sec if current_duration_sec > 0 else 0
            progress_width = int(progress * 360)
            progress_bar_inner.config(width=progress_width, bg=TIMER_ACTIVE if remaining > 60 else TIMER_LOW)

            if remaining <= 0:
                timer_label.config(text="Time's up!", fg=TIMER_LOW)
                status_label.config(text="Scan next card → ⏭", fg=ACCENT_COLOR)
        else:
            timer_label.config(text="—:--", fg=SECONDARY_TEXT)
            progress_bar_inner.config(width=0, bg=BG_COLOR)

    root.after(800, update_ui)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    root = tk.Tk()
    root.title("Smart Recipe Guide")
    root.geometry("680x520")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

    main_frame = tk.Frame(root, bg=BG_COLOR, padx=30, pady=20)
    main_frame.pack(fill="both", expand=True)

    tk.Label(main_frame, text="🍳 Smart RFID Cooking Assistant", font=("Segoe UI", 18, "bold"),
             bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 15))

    name_label = tk.Label(main_frame, text="Ready to cook", font=("Segoe UI", 16, "bold"),
                          bg=BG_COLOR, fg="#ffffff", wraplength=620)
    name_label.pack(pady=8)

    step_label = tk.Label(main_frame, text="No recipe active", font=("Consolas", 13),
                          bg=BG_COLOR, fg=SECONDARY_TEXT)
    step_label.pack(pady=(0, 4))

    instr_label = tk.Label(main_frame, text="Scan a recipe card to begin → 🍲", font=("Segoe UI", 13),
                           bg=BG_COLOR, fg=TEXT_COLOR, wraplength=620, justify="left")
    instr_label.pack(pady=10)

    detail_label = tk.Label(main_frame, text="", font=("Segoe UI", 11, "italic"),
                            bg=BG_COLOR, fg=SECONDARY_TEXT, wraplength=620, justify="left")
    detail_label.pack(pady=(0, 12))

    timer_frame = tk.Frame(main_frame, bg=BG_COLOR)
    timer_frame.pack(pady=12)

    tk.Label(timer_frame, text="TIME LEFT", font=("Segoe UI", 10),
             bg=BG_COLOR, fg=SECONDARY_TEXT).pack()

    timer_label = tk.Label(timer_frame, text="—:--", font=("Consolas", 32, "bold"),
                           bg=BG_COLOR, fg=TEXT_COLOR)
    timer_label.pack()

    progress_container = tk.Frame(main_frame, bg="#333333", width=360, height=12, bd=0)
    progress_container.pack(pady=8)
    progress_container.pack_propagate(False)

    progress_bar_inner = tk.Frame(progress_container, bg=BG_COLOR, width=0, height=12)
    progress_bar_inner.place(x=0, y=0)

    progress_label = tk.Label(progress_container, text="", font=("Segoe UI", 9),
                              bg="#333333", fg="#ffffff")
    progress_label.place(relx=0.5, rely=0.5, anchor="center")

    status_label = tk.Label(main_frame, text="Waiting for scan...", font=("Segoe UI", 11),
                            bg=BG_COLOR, fg=SECONDARY_TEXT)
    status_label.pack(pady=15)

    tk.Label(main_frame, text="Recipe cards → start   •   Next card → next step",
             font=("Segoe UI", 9), bg=BG_COLOR, fg="#777777").pack(side="bottom", pady=10)

    root.after(800, update_ui)
    root.mainloop()