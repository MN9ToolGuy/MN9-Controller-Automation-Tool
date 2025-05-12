import customtkinter as ctk
import threading
import time
import vgamepad as vg
import os

# Constants
SCRIPT_DIR = "saved_scripts"
os.makedirs(SCRIPT_DIR, exist_ok=True)

# Try initializing gamepad safely
try:
    gamepad = vg.VX360Gamepad()
except Exception as e:
    print(f"Failed to initialize virtual gamepad: {e}")
    exit(1)

# GUI Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Controller Automation Tool")
app.geometry("900x650")
app.resizable(False, False)
app.wm_attributes("-topmost", True)

# Global control
running = False

# --- Core Controller Functions ---
def get_button_from_command(command):
    mapping = {
        "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }
    return mapping.get(command.upper())

def press_button(button, duration=0.2):
    gamepad.press_button(button=button)
    gamepad.update()
    time.sleep(duration)
    gamepad.release_button(button=button)
    gamepad.update()

def hold_button(button, duration):
    gamepad.press_button(button=button)
    gamepad.update()
    time.sleep(duration)
    gamepad.release_button(button=button)
    gamepad.update()

def insert_output(text):
    output_box.configure(state="normal")
    output_box.insert("end", text + "\n")
    output_box.see("end")
    output_box.configure(state="disabled")

def execute_commands():
    global running
    running = True
    status_label.configure(text="Status: Running", text_color="orange")
    try:
        text = input_box.get("1.0", "end").strip()
        commands = text.splitlines()
        while running:
            for line in commands:
                if not running:
                    break
                cmd = line.strip().upper()
                if not cmd:
                    continue
                insert_output(f"> {cmd}")
                try:
                    if cmd.startswith("PRESS"):
                        button = get_button_from_command(cmd.split()[1])
                        press_button(button)
                    elif cmd.startswith("HOLD"):
                        parts = cmd.split()
                        button = get_button_from_command(parts[1])
                        duration = float(parts[3]) if len(parts) > 3 else 1
                        hold_button(button, duration)
                    elif cmd.startswith("WAIT") or cmd.startswith("SLEEP"):
                        duration = float(cmd.split()[1])
                        time.sleep(duration)
                    elif cmd.startswith("REPEAT"):
                        parts = cmd.split()
                        button = get_button_from_command(parts[1])
                        times = int(parts[2])
                        delay = 0.5
                        if len(parts) >= 5 and parts[3] == "DELAY":
                            delay = float(parts[4])
                        for _ in range(times):
                            if not running:
                                break
                            press_button(button)
                            time.sleep(delay)
                    else:
                        insert_output(f"Unknown command: {cmd}")
                except Exception as e:
                    insert_output(f"Error: {str(e)}")
            if not loop_var.get():
                break
    finally:
        status_label.configure(text="Status: Idle", text_color="lightgreen")
        running = False

def start_thread():
    if not running:
        threading.Thread(target=execute_commands, daemon=True).start()

def stop_commands():
    global running
    running = False
    status_label.configure(text="Status: Stopped", text_color="red")
    insert_output("Command execution stopped.")

# --- Script Management ---
def save_script():
    name = script_name_entry.get().strip()
    if name:
        path = os.path.join(SCRIPT_DIR, name + ".txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(input_box.get("1.0", "end").strip())
        update_script_list()

def load_script():
    selected = saved_scripts_listbox.get()
    if selected:
        path = os.path.join(SCRIPT_DIR, selected + ".txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                input_box.delete("1.0", "end")
                input_box.insert("1.0", f.read())

def delete_script():
    selected = saved_scripts_listbox.get()
    if selected and selected != "Choose script" and selected != "No scripts available":
        path = os.path.join(SCRIPT_DIR, selected + ".txt")
        if os.path.exists(path):
            os.remove(path)
            update_script_list()

def update_script_list():
    scripts = [f.replace(".txt", "") for f in os.listdir(SCRIPT_DIR) if f.endswith(".txt")]
    if scripts:
        saved_scripts_listbox.configure(values=scripts)
        saved_scripts_listbox.set("Choose script")
    else:
        saved_scripts_listbox.configure(values=["No scripts available"])
        saved_scripts_listbox.set("No scripts available")

# --- UI Setup ---
tabview = ctk.CTkTabview(app, width=860, height=600, corner_radius=12,
                         segmented_button_fg_color="#1a1a1a",
                         segmented_button_selected_color="#0044cc",
                         segmented_button_selected_hover_color="#0033aa")
tabview._segmented_button.configure(font=("Segoe UI", 16, "bold"), height=40)
tabview.pack(pady=20, padx=20)

tab_main = tabview.add("\ud83d\udcbb Run")
tab_saved = tabview.add("\ud83d\udcc2 Saved Scripts")

input_label = ctk.CTkLabel(tab_main, text="\ud83c\udfae Command Input", font=("Segoe UI", 18, "bold"))
input_label.pack(pady=(10, 5), anchor="w")

input_box = ctk.CTkTextbox(tab_main, height=160, font=("Consolas", 14), wrap="word")
input_box.pack(fill="x", padx=5, pady=(0, 10))

helper_label = ctk.CTkLabel(tab_main, text="\ud83e\udde0 Command Helper", font=("Segoe UI", 16, "bold"))
helper_label.pack(anchor="w", padx=5, pady=(10, 0))

helper_frame = ctk.CTkFrame(tab_main, corner_radius=10)
helper_frame.pack(fill="x", padx=5, pady=(5, 10))

def insert_command(cmd):
    input_box.insert("end", f"{cmd}\n")

helper_buttons = [
    ("PRESS A", "#007BFF"),
    ("HOLD B FOR 1", "#007BFF"),
    ("WAIT 2", "#007BFF"),
    ("REPEAT X 5 DELAY 0.5", "#007BFF"),
    ("PRESS START", "#007BFF")
]

for text, color in helper_buttons:
    btn = ctk.CTkButton(helper_frame, text=text, command=lambda t=text: insert_command(t),
                        fg_color=color, hover_color="#333", text_color="black",
                        corner_radius=10, font=("Segoe UI", 13), width=140)
    btn.pack(side="left", padx=5, pady=5)

button_frame = ctk.CTkFrame(tab_main, corner_radius=10)
button_frame.pack(fill="x", pady=5)

run_button = ctk.CTkButton(button_frame, text="\u25b6 Run", command=start_thread, width=150, height=45, font=("Segoe UI", 14, "bold"))
run_button.pack(side="left", padx=(0, 10))

stop_button = ctk.CTkButton(button_frame, text="\u25a0 Stop", command=stop_commands, width=150, height=45, font=("Segoe UI", 14, "bold"))
stop_button.pack(side="left", padx=(0, 10))

clear_button = ctk.CTkButton(button_frame, text="\ud83e\uddf9 Clear Input", command=lambda: input_box.delete("1.0", "end"), width=150, height=45, font=("Segoe UI", 14))
clear_button.pack(side="left", padx=(0, 10))

loop_var = ctk.BooleanVar()
loop_checkbox = ctk.CTkCheckBox(button_frame, text="Loop Commands", variable=loop_var, font=("Segoe UI", 13))
loop_checkbox.pack(side="left", padx=(10, 0))

status_label = ctk.CTkLabel(tab_main, text="Status: Idle", text_color="lightgreen", font=("Segoe UI", 16, "bold"))
status_label.pack(anchor="w", pady=(10, 0))

output_label = ctk.CTkLabel(tab_main, text="\ud83d\udcec Output / Log", font=("Segoe UI", 18, "bold"))
output_label.pack(pady=(15, 5), anchor="w")

output_box = ctk.CTkTextbox(tab_main, height=180, font=("Consolas", 14), wrap="word", state="disabled")
output_box.pack(fill="both", expand=True, padx=5)

script_name_entry = ctk.CTkEntry(tab_saved, placeholder_text="Enter script name", font=("Segoe UI", 14))
script_name_entry.pack(pady=10)

save_button = ctk.CTkButton(tab_saved, text="\ud83d\udcc2 Save Current Script", command=save_script, width=200, height=40, font=("Segoe UI", 14))
save_button.pack(pady=5)

saved_scripts_listbox = ctk.CTkOptionMenu(tab_saved, values=[], font=("Segoe UI", 14))
saved_scripts_listbox.pack(pady=5)

load_button = ctk.CTkButton(tab_saved, text="\ud83d\udcc2 Load Script", command=load_script, width=200, height=40, font=("Segoe UI", 14))
load_button.pack(pady=5)

delete_button = ctk.CTkButton(tab_saved, text="\ud83d\uddd1\ufe0f Delete Script", command=delete_script, width=200, height=40, font=("Segoe UI", 14))
delete_button.pack(pady=5)

update_script_list()

# Clipboard Shortcuts
def bind_clipboard_shortcuts(textbox):
    textbox.bind("<Control-c>", lambda e: textbox.event_generate("<<Copy>>"))
    textbox.bind("<Control-v>", lambda e: textbox.event_generate("<<Paste>>"))
    textbox.bind("<Control-x>", lambda e: textbox.event_generate("<<Cut>>"))
    textbox.bind("<Control-a>", lambda e: (textbox.tag_add("sel", "1.0", "end"), "break"))

bind_clipboard_shortcuts(input_box)



# Run app
if __name__ == "__main__":
    app.mainloop()
