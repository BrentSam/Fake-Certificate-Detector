import uno
import time
import subprocess
import os

def main():
    print("Starting LibreOffice...")
    port = 2002
    cmd = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        "--headless",
        f"--accept=socket,host=127.0.0.1,port={port};urp;"
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(3) # Wait for LibreOffice to start
    
    try:
        print("Connecting to LibreOffice...")
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", localContext
        )
        context = resolver.resolve(f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext")
        desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
        print("Connected successfully!")
        
        # Load the document
        file_path = os.path.abspath("docs/Brent Project Report.odt")
        print(f"Loading document: {file_path}")
        file_url = uno.systemPathToFileUrl(file_path)
        
        # Let's check if file exists
        if not os.path.exists(file_path):
            print(f"Error: file {file_path} does not exist!")
            return
            
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())
        print("Document loaded successfully!")
        doc.close(True)
        print("Document closed.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Terminating LibreOffice...")
        proc.terminate()
        proc.wait()
        print("LibreOffice terminated.")

if __name__ == "__main__":
    main()
