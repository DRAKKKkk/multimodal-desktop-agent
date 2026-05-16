from mcp.server.fastmcp import FastMCP
import subprocess
import os

# Server ka naam jo AI ko dikhega
mcp = FastMCP("OmniContext-Tools")

@mcp.tool()
def open_windows_app(app_name: str) -> str:
    """
    Ek simple tool jo Windows ki basic apps open karta hai.
    app_name: App ka naam jaise 'notepad', 'calc', ya 'explorer'.
    """
    try:
        subprocess.Popen(app_name)
        return f"Success: Maine tumhare liye {app_name} open kar diya hai!"
    except Exception as e:
        return f"Error: {app_name} open nahi ho paya. Details: {e}"

@mcp.tool()
def create_text_file(filename: str, content: str) -> str:
    """
    Ek tool jo tumhare PC par nayi text file banata hai aur usme content save karta hai.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: {filename} file ban gayi aur usme text save ho gaya."
    except Exception as e:
        return f"Error: File save karne mein dikkat aayi - {e}"

if __name__ == "__main__":
    print("🤖 OmniContext MCP Server is ready...")
    mcp.run()