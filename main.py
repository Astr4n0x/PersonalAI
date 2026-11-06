"""
main.py — Jarvis AI Assistant GUI Entry Point
Bridges the animated GUI (gui.py) with the backend brain (services/brain.py).
"""
import sys
import os
import threading

# Ensure services/ is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from gui import (
    JarvisGUI,
    STATE_IDLE, STATE_LISTENING, STATE_THINKING, STATE_SPEAKING,
)

# ── Import backend services ──────────────────────────────────────────────────
from services.brain import DecisionMakingModel, route
from services.text_to_speach import speak


# ── Task → display label mapping ────────────────────────────────────────────
TASK_LABEL_MAP = {
    "general":        "general",
    "realtime":       "realtime",
    "stocks":         "stocks",
    "crypto":         "crypto",
    "weather":        "weather",
    "open":           "open",
    "close":          "close",
    "play":           "play",
    "youtube search": "youtube search",
    "google search":  "google search",
    "content":        "content",
    "generate image": "generate image",
    "reminder":       "reminder",
    "system":         "system",
}


def detect_task_key(decision: str) -> str:
    """Map a brain decision string to a task badge key."""
    d = decision.lower().strip()
    for key in TASK_LABEL_MAP:
        if d.startswith(key):
            return key
    return "general"


def handle_input(text: str, gui: JarvisGUI):
    """
    Runs in a background thread.
    1. Decision-making → show task badge
    2. Route to service → get result
    3. Speak result → show speaking animation
    4. Reset to idle
    """
    try:
        # ── Step 1: Thinking ────────────────────────────────────────────────
        gui.set_state(STATE_THINKING)
        gui.set_task("thinking")
        gui.show_typing()

        decision = DecisionMakingModel(text)

        # Exit command
        if decision.strip().lower() == "exit":
            gui.hide_typing()
            gui.add_ai_message("Goodbye! Have a great day.")
            gui.set_state(STATE_IDLE)
            gui.set_task("idle")
            threading.Thread(target=speak, args=("Goodbye! Have a great day.",), daemon=True).start()
            return

        # ── Step 2: Task-specific label ─────────────────────────────────────
        task_key = detect_task_key(decision)
        gui.set_task(task_key)

        # ── Step 3: Route & execute ─────────────────────────────────────────
        result = route(decision)

        if result is None:
            result = "I've completed that for you."

        # ── Step 4: Display result ───────────────────────────────────────────
        gui.hide_typing()
        gui.add_ai_message(result)

        # ── Step 5: Speak result ─────────────────────────────────────────────
        gui.set_state(STATE_SPEAKING)
        gui.set_task("speaking")
        speak(result)

    except Exception as e:
        gui.hide_typing()
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        gui.add_ai_message(error_msg)

    finally:
        gui.set_state(STATE_IDLE)
        gui.set_task("idle")


def main():
    app = JarvisGUI()

    # Wire up the callback — called from GUI thread (send button / mic button)
    def on_user_input(text: str):
        handle_input(text, app)

    app.on_user_input = on_user_input

    # Graceful close
    app.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Start GUI mainloop (blocks until window is closed)
    app.mainloop()


if __name__ == "__main__":
    main()
