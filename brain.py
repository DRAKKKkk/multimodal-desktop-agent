import subprocess
import os 
from PIL import Image
from google import genai
from dotenv import load_dotenv

# ==========================================
# 1. API Setup (Apna API Key yahan dalein)
# ==========================================
# DHYAN DEIN: Apni asli Gemini API key yahan string mein dalein
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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
        print("\n==================================================")
        print("🤖 GEMINI KA JAWAB:")
        print("==================================================")
        print(response.text)
        print("==================================================\n")
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    capture_and_analyze()