import subprocess
import os 
from PIL import Image
import google.generativeai as genai

# ==========================================
# 1. API Setup (Apna API Key yahan dalein)
# ==========================================
# DHYAN DEIN: Apni asli Gemini API key yahan string mein dalein
GEMINI_API_KEY = "AIzaSyC3I9EyS2wxDPQeTaiqU4qdvLyKtXFjB6c"
genai.configure(api_key=GEMINI_API_KEY)

def capture_and_analyze():
    # File paths
    exe_path = r"screenshot.exe"
    bmp_path = "mine_screenshot.bmp"
    png_path = "current_screen.png"

    # ==========================================
    # 2. C++ "Muscle" ko trigger karna
    # ==========================================
    print("📸 1. C++ tool se screenshot le raha hoon...")
    try:
        subprocess.run([exe_path], check=True, capture_output=True)
    except FileNotFoundError:
        print("❌ Error: 'screenshot.exe' nahi mila. Kya aapne C++ code compile kiya hai?")
        return
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: C++ program crash ho gaya.\n{e}")
        return
    
    # ==========================================
    # 3. Image Conversion (.bmp -> .png)
    # ==========================================
    print("🔄 2. Image ko Gemini ke liye .png mein convert kar raha hoon...")
    if not os.path.exists(bmp_path):
        print(f"❌ Error: {bmp_path} nahi mili!")
        return
    
    img = Image.open(bmp_path)
    img.save(png_path, "PNG")

    # Optional: Original .bmp file ko delete kar sakte hain space bachane ke liye
    # os.remove(bmp_path)

    # ==========================================
    # 4. Gemini API "Brain" ko prompt bhejna
    # ==========================================
    print("🧠 3. Screen ko analyse karne ke liye Gemini ke paas bhej raha hoon...")

    model = genai.GenerativeModel('gemini-1.5-flash')

    vision_image = Image.open(png_path)
    prompt = "Main apne laptop par abhi kya kar raha hoon? Is screen ko dekh kar detail mein samjhao ki screen par kaunse apps khule hain aur kya kaam chal raha hai."

    try:
        response = model.generate_content([prompt, vision_image])
        print("\n==================================================")
        print("🤖 GEMINI KA JAWAB:")
        print("==================================================")
        print(response.text)
        print("==================================================\n")
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    capture_and_analyze()