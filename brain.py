import os
import time
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from PIL import ImageGrab, Image
import pyautogui
import subprocess
from google import genai
from dotenv import load_dotenv

# API Setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def show_result_ui(result_text):
    """Modern Dark Theme UI for AI Responses"""
    root = tk.Tk()
    root.title("🤖 OmniContext AI - Response")
    root.geometry("600x450")
    root.attributes('-topmost', True)
    root.configure(bg="#121212")
    
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11), bg="#1e1e1e", fg="#00ff00", padx=15, pady=15)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_area.insert(tk.INSERT, result_text)
    text_area.configure(state='disabled')
    
    root.bind('<Escape>', lambda e: root.destroy())
    root.mainloop()

def get_custom_screenshot():
    """Windows native snipping tool ko trigger karta hai aur clipboard se image uthata hai"""
    # 1. Purana clipboard clear karna (Windows native command)
    subprocess.run(['clip'], input='', text=True)
    
    # 2. Snipping tool open karna (Win + Shift + S)
    time.sleep(0.5) # UI ko thoda saanz lene ka time
    pyautogui.hotkey('win', 'shift', 's')
    
    # 3. User ka wait karna (max 30 seconds) jab tak wo crop na kar le
    img = None
    for _ in range(60): # 0.5 sec * 60 = 30 seconds
        img = ImageGrab.grabclipboard()
        # Agar clipboard mein image aayi hai, toh loop tod do
        if isinstance(img, Image.Image): 
            break
        time.sleep(0.5)
        
    # NAYA: Pylance ko guarantee dena ki yeh exactly ek Image hi hai
    if isinstance(img, Image.Image):
        img_path = "custom_snip.png"
        img = img.convert("RGB") 
        img.save(img_path, "PNG")
        return img_path
        
    return None

def main():
    # 1. THE CONTEXT ENGINE: Custom Prompt UI
    root = tk.Tk()
    root.withdraw() 
    user_prompt = simpledialog.askstring("OmniContext AI", "Aapka Context/Sawal kya hai? (Voice coming soon...)", parent=root)
    
    if user_prompt is None:
        return 
    if user_prompt.strip() == "":
        user_prompt = "Main abhi kya kar raha hoon? Detail mein batao."

    # 2. CUSTOM SNIPPING TOOL INTEGRATION
    # User ko ek alert dete hain taaki wo taiyaar rahe
    messagebox.showinfo("Action Required", "OK dabane ke baad apni screen ka hissa crop karein.")
    
    img_path = get_custom_screenshot()
    
    if not img_path:
        messagebox.showwarning("Timeout", "Aapne koi screenshot nahi liya. AI process cancel ho gaya.")
        return
    
    try:
        # 3. THE AI ORCHESTRATOR
        client = genai.Client(api_key=GEMINI_API_KEY)
        vision_image = Image.open(img_path)
        
        # AI ko clearly command dena ki image padhni hai
        strict_prompt = f"[SYSTEM: Look at the attached image carefully and answer the user's request based on the image content.]\n\nUser Request: {user_prompt}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[strict_prompt, vision_image]
        )
        
        # 4. UI RENDER
        show_result_ui(str(response.text))
        
    except Exception as e:
        messagebox.showerror("System Error ❌", f"AI se connect nahi ho paya:\n{str(e)[:150]}")

if __name__ == "__main__":
    main()