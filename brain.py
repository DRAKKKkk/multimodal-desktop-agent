from winotify import Notification
import subprocess
import os
import re
from PIL import Image
from google import genai
from dotenv import load_dotenv


# ==========================================
# 1. API Setup (Apna API Key yahan dalein)
# ==========================================
# DHYAN DEIN: Apni asli Gemini API key yahan string mein dalein
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: API Key nahi mili! Kya tumne .env file banayi hai?")
    exit()

def execute_ai_action(action_command):
    """Yeh function AI ki di hui command ko PC par execute karta hai."""
    app_name = action_command.strip().lower()
    print(f"\n⚙️ [SYSTEM ACTION] AI ne action trigger kiya: '{app_name}' open kar raha hoon...")

    try:
        subprocess.Popen(app_name)
        print("✅ Action successful!")
    except Exception as e:
        print(f"❌ Action fail ho gaya: {e}")

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
    except Exception as e:
        print(f"❌ Error: C++ program fail ho gaya.\n{e}")
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

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        vision_image = Image.open(png_path)
        prompt = """Main apne laptop par abhi kya kar raha hoon? Is screen ko dekh kar detail mein samjhao ki screen par kaunse apps khule hain aur kya kaam chal raha hai. 
        
        IMPORTANT INSTRUCTION: Tumhara poora jawab sirf aur sirf 'Hinglish' (Hindi spoken language written in English alphabets) mein hona chahiye. Pure Hindi (Devanagari script) ya pure English ka bilkul use mat karna. Jawab natural aur conversational hona chahiye."""

        # Latest Gemini 2.0 Flash model use kar rahe hain
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, vision_image]
        )

        ai_response_text = str(response.text)

        print("\n==================================================")
        print("🤖 GEMINI KA JAWAB:")
        print("==================================================")
        print(response.text)
        print("==================================================\n")

        # ==========================================
        # 5. ACTION EXTRACTOR (Dimaag se Haath tak ka connection)
        # ==========================================
        # RegEx ka use karke hum AI ke jawab mein se <ACTION> wale tag ko dhoondhte hain
        match = re.search(r"<ACTION>(.*?)</ACTION>", ai_response_text)

        if match:
            action_command = match.group(1)
            toast = Notification(
                app_id="OmniContext AI", 
                title="⚡ Action Executing", 
                msg=f"Command: {action_command}", 
                duration="short"
            )
            toast.show()
            execute_ai_action(action_command)
        else:
            print("🛑 AI ne is baar koi PC action lene ki zarurat nahi samjhi.")
            display_text = ai_response_text[:250] + "..." if len(ai_response_text) > 250 else ai_response_text 
    
            toast = Notification(
                app_id="OmniContext AI", 
                title="🧠 AI Response", 
                msg=display_text, 
                duration="long"
            )
            toast.show()

    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    capture_and_analyze()