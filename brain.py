import os
import sys
import time
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from PIL import ImageGrab, Image
import pyautogui
import subprocess
from google import genai
from google.genai import types # NAYA: Tools configure karne ke liye
from dotenv import load_dotenv

# API Setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================
# 1. THE MCP SERVER (AGENTIC TOOLS)
# ==========================================
def open_windows_app(app_name: str) -> str:
    """Opens a Windows application like 'calc', 'notepad', 'cmd', or 'explorer'."""
    try:
        subprocess.Popen(app_name)
        return f"System Action Complete: Successfully opened {app_name}"
    except Exception as e:
        return f"System Error: Failed to open {app_name}. Error: {str(e)}"

def save_text_to_desktop(filename: str, content: str) -> str:
    """Saves code, notes, or any text to a new file directly on the user's Desktop."""
    try:
        user_profile = os.environ['USERPROFILE']
        # Pehle OneDrive wala path check karega
        onedrive_desktop = os.path.join(user_profile, 'OneDrive', 'Desktop')
        default_desktop = os.path.join(user_profile, 'Desktop')
        
        if os.path.exists(onedrive_desktop):
            desktop_path = onedrive_desktop
        else:
            desktop_path = default_desktop
            
        filepath = os.path.join(desktop_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"System Action Complete: File saved successfully at {filepath}"
    except Exception as e:
        return f"System Error: Failed to save file. Error: {str(e)}"

# ==========================================
# 2. THE UI & SCREENSHOT ENGINE
# ==========================================
def show_result_ui(result_text):
    root = tk.Tk()
    root.title("🤖 OmniContext Agent")
    root.geometry("600x450")
    root.attributes('-topmost', True)
    root.configure(bg="#121212")
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11), bg="#1e1e1e", fg="#00ff00", padx=15, pady=15)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_area.insert(tk.INSERT, result_text)
    text_area.configure(state='disabled')
    root.bind('<Escape>', lambda e: root.destroy())
    root.mainloop()

def get_full_screenshot():
    img = ImageGrab.grab() 
    img_path = "full_screen.png"
    img = img.convert("RGB")
    img.save(img_path, "PNG")
    return img_path

def get_custom_screenshot():
    subprocess.run(['clip'], input='', text=True) 
    time.sleep(0.5) 
    pyautogui.hotkey('win', 'shift', 's')
    img = None
    for _ in range(60): 
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image): 
            break
        time.sleep(0.5)
    if isinstance(img, Image.Image):
        img_path = "custom_snip.png"
        img = img.convert("RGB") 
        img.save(img_path, "PNG")
        return img_path
    return None

# ==========================================
# 3. THE MAIN ORCHESTRATOR
# ==========================================
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    root = tk.Tk()
    root.withdraw() 
    user_prompt = simpledialog.askstring("OmniContext AI", "Sawal pucho ya koi task do:", parent=root)
    
    if not user_prompt:
        return 
        
    if mode == "crop":
        messagebox.showinfo("Action", "OK dabane ke baad screen ka hissa crop karein.")
        img_path = get_custom_screenshot()
    else:
        img_path = get_full_screenshot()
    
    if not img_path:
        return
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        vision_image = Image.open(img_path)
        
        # System ko saaf instruction diya hai ki tools use karne hain
        system_instruction = "You are a smart AI assistant with access to system tools. Look at the attached image context. If the user asks to open an app or save code/notes, DO NOT just write the code, USE YOUR TOOLS to perform the action automatically. Then summarize what you did in Hinglish."
        
        # 'chats' mode automatically hamare python tools ko call kar leta hai!
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                temperature=0.2,
                tools=[open_windows_app, save_text_to_desktop], # AI KO HAATH DE DIYE
            )
        )
        
        # Prompt aur Image dono bhej diye
        response = chat.send_message([system_instruction, "\n\nUser: " + user_prompt, vision_image])
        
        show_result_ui(str(response.text))
        
    except Exception as e:
        messagebox.showerror("Error ❌", f"Agent Failed:\n{str(e)}")

if __name__ == "__main__":
    main()