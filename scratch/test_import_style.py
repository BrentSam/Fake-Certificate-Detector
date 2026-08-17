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
        
        # Test importing from com.sun.star.style
        import com.sun.star.style
        print("Imported com.sun.star.style successfully!")
        
        items = dir(com.sun.star.style)
        print(f"Number of items in com.sun.star.style: {len(items)}")
        
        # Look for things containing Tab or Align or Adjust
        matching = [item for item in items if "Tab" in item or "Align" in item or "Adjust" in item]
        print("Matching items:")
        for item in matching:
            print(f" - {item}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
