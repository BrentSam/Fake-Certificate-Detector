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
        desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
        
        file_path = os.path.abspath("docs/Brent Project Report.odt")
        file_url = uno.systemPathToFileUrl(file_path)
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())
        
        text = doc.Text
        enum = text.createEnumeration()
        
        count = 0
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                tabs = el.getPropertyValue("ParaTabStops")
                # Find a paragraph that actually has tab stops, or print the default
                if tabs:
                    print(f"Para {count} | ParaTabStops type: {type(tabs)} | Length: {len(tabs)}")
                    for i, t in enumerate(tabs):
                        print(f" - TabStop {i}: Position={t.Position}, Alignment={t.Alignment}, DecimalChar={repr(t.DecimalChar)}, FillChar={repr(t.FillChar)}")
                else:
                    if count < 5:
                        print(f"Para {count} | ParaTabStops is empty/None/empty tuple: {repr(tabs)}")
                count += 1
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
