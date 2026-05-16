import os
import sys
import time
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from PIL import ImageGrab, Image
import pyautogui
import subprocess
import speech_recognition as sr
import winsound
from google import genai
from dotenv import load_dotenv

# API Setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================
# 1. THE MCP SERVER (AGENTIC TOOLS)
# ==========================================
def open_windows_app(app_name: str) -> str:
    """Opens a Windows application like 'calc', 'notepad', 'cmd', 'code' or 'cpeditor'."""
    try:
        # shell=True se Win+R wale saare commands (jaise 'code') chalenge
        subprocess.Popen(app_name, shell=True)
        return f"System Action Complete: Successfully opened {app_name}"
    except Exception as e:
        return f"System Error: Failed to open {app_name}. Error: {str(e)}"

def save_text_to_desktop(filename: str, content: str) -> str:
    """Saves code or text to a new file directly on the Desktop (handles OneDrive too)."""
    try:
        user_profile = os.environ.get('USERPROFILE', '')
        onedrive_desktop = os.path.join(user_profile, 'OneDrive', 'Desktop')
        default_desktop = os.path.join(user_profile, 'Desktop')
        
        desktop_path = onedrive_desktop if os.path.exists(onedrive_desktop) else default_desktop
            
        filepath = os.path.join(desktop_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"System Action Complete: File saved successfully at {filepath}"
    except Exception as e:
        return f"System Error: Failed to save file. Error: {str(e)}"

# ==========================================
# 2. VOICE & SCREENSHOT ENGINE
# ==========================================
def get_voice_input():
    """Voice Assistant style floating widget for real-time feedback"""
    # 1. Floating Widget Setup (Borderless UI)
    overlay = tk.Tk()
    overlay.title("Voice Assistant")
    overlay.overrideredirect(True) # Window ke borders/buttons hata dega (Clean Linux Widget look)
    overlay.configure(bg="#202124") # Dark Material Theme
    overlay.attributes('-topmost', True) # Hamesha screen ke upar rahega
    
    # Widget ko screen ke bottom-center mein set karna
    window_width = 500
    window_height = 100
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int(screen_height - 150) # Thoda neeche
    overlay.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
    
    # 2. UI Elements
    lbl_status = tk.Label(overlay, text="Listening... 🎙️", font=("Segoe UI", 14, "bold"), fg="#8ab4f8", bg="#202124")
    lbl_status.pack(pady=(15, 5))
    
    lbl_text = tk.Label(overlay, text="Boliye, main sun raha hoon...", font=("Segoe UI", 11), fg="white", bg="#202124", wraplength=480)
    lbl_text.pack()
    
    # UI ko screen par render karna
    overlay.update() 
    
    recognized_text = None
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        winsound.Beep(1000, 200) # Start Beep
        try:
            # Aawaz record karna
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
            # Sunne ke baad UI update karna
            lbl_status.config(text="Processing... ⏳", fg="#fbbc04")
            lbl_text.config(text="Aawaz ko text mein convert kar raha hoon...")
            overlay.update()
            winsound.Beep(1500, 200) # End Beep
            
            # API se text nikalna
            text = r.recognize_google(audio, language="en-IN") 
            
            # Final Result UI par dikhana
            lbl_status.config(text="Recognized ✅", fg="#34a853")
            lbl_text.config(text=f'"{text}"')
            overlay.update()
            time.sleep(4) # User ko padhne ke liye 1.5 sec ka time dena
            recognized_text = text
            
        except sr.WaitTimeoutError:
            lbl_status.config(text="Timeout ❌", fg="#ea4335")
            lbl_text.config(text="Aapne kuch nahi bola.")
            overlay.update()
            time.sleep(1.5)
        except Exception as e:
            lbl_status.config(text="Error ❌", fg="#ea4335")
            lbl_text.config(text="Aawaz theek se samajh nahi aayi.")
            overlay.update()
            time.sleep(1.5)
            
    overlay.destroy() # Widget ko clean tareeqe se band karna
    return recognized_text
    """Microphone se aawaz sun kar text mein convert karta hai"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        winsound.Beep(1000, 200) # Start Beep (Bolo!)
        try:
            # 5 sec silence wait karega, max 15 sec tak sunega
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            winsound.Beep(1500, 200) # End Beep (Sun liya!)
            
            # Google Free API se convert
            text = r.recognize_google(audio, language="en-IN")
            return text
        except:
            # Agar aawaz nahi aayi ya samajh nahi aayi
            return None

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
        if isinstance(img, Image.Image): break
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
    
    # ==== JARVIS MODE: Voice Input ====
    user_prompt = get_voice_input()
    
    # Agar voice fail ho jaye, toh purana Text Box aa jayega (Fallback)
    if not user_prompt:
        root = tk.Tk()
        root.withdraw() 
        user_prompt = simpledialog.askstring("Fallback Mode", "Voice samajh nahi aayi. Type kijiye:", parent=root)
        if not user_prompt: return

    # ==== Vision Mode ====
    if mode == "crop":
        img_path = get_custom_screenshot()
    else:
        img_path = get_full_screenshot()
    
    if not img_path: return
    
    # ==== AI Processing ====
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        vision_image = Image.open(img_path)
        
        system_instruction = "You are a smart AI assistant with system tools. Look at the image. If the user asks to open an app (like 'code', 'cpeditor', etc) or save code/notes, USE YOUR TOOLS to perform the action automatically. Respond in Hinglish."
        
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config={
                "temperature": 0.2,
                "tools": [open_windows_app, save_text_to_desktop]
            }
        )
        
        response = chat.send_message([system_instruction, "\n\nUser Voice Command: " + user_prompt, vision_image])
        show_result_ui(str(response.text))
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error ❌", f"Agent Failed:\n{str(e)}")

if __name__ == "__main__":
    main()