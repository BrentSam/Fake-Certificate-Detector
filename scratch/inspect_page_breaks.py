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
                txt = el.getString().strip()
                page_desc = el.getPropertyValue("PageDescName")
                break_type = el.getPropertyValue("BreakType")
                
                # BreakType 0 means NONE, 1 means COLUMN_BEFORE, 2 means COLUMN_AFTER, 3 means PAGE_BEFORE, 4 means PAGE_AFTER
                if page_desc or break_type != 0:
                    print(f"Para {count:03d} | PageDescName: {page_desc} | BreakType: {break_type} | Text: '{txt[:40]}...'")
                count += 1
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
