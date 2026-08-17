import uno
import time
import subprocess
import os

def main():
    port = 2002
    cmd = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        "--headless",
        f"--accept=socket,host=127.0.0.1,port={port};urp;"
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(3)
    
    try:
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", localContext
        )
        context = resolver.resolve(f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext")
        
        # Test creating enums
        print("Testing uno.Enum...")
        
        center_adjust = uno.Enum("com.sun.star.style.ParagraphAdjust", "CENTER")
        print("Successfully created ParagraphAdjust.CENTER:", center_adjust)
        
        right_tab_align = uno.Enum("com.sun.star.style.TabAlign", "RIGHT")
        print("Successfully created TabAlign.RIGHT:", right_tab_align)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
