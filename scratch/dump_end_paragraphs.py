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
        
        controller = doc.getCurrentController()
        view_cursor = controller.getViewCursor()
        
        text = doc.Text
        enum = text.createEnumeration()
        
        paragraphs = []
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                paragraphs.append(el)
                
        total = len(paragraphs)
        print(f"Total paragraphs: {total}")
        
        # Dump the last 30 paragraphs
        start_idx = max(0, total - 40)
        for idx in range(start_idx, total):
            el = paragraphs[idx]
            txt = el.getString().strip()
            style = el.getPropertyValue("ParaStyleName")
            view_cursor.gotoRange(el.getStart(), False)
            page_num = view_cursor.getPage()
            safe_txt = txt.encode('ascii', errors='replace').decode('ascii')
            print(f"[{idx:03d}] Page {page_num} ({style}): '{safe_txt}'")
            
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
