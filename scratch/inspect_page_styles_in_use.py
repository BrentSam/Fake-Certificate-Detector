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
        
        count = 0
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                txt = el.getString().strip()
                view_cursor.gotoRange(el.getStart(), False)
                page_num = view_cursor.getPage()
                # Get style of this paragraph
                style_name = el.getPropertyValue("ParaStyleName")
                # Get the page style of this paragraph
                # Wait, paragraph page style name is retrieved via PageStyleName
                page_style_name = el.getPropertyValue("PageStyleName") if hasattr(el, "PageStyleName") else None
                # Or we can query the page style at the cursor position
                cursor_page_style = view_cursor.PageStyleName
                
                if page_num <= 15 or page_num >= 65:
                    if txt:
                        print(f"Para {count:03d} | Page {page_num} | Style: {style_name} | Para PageStyle: {page_style_name} | ViewCursor PageStyle: {cursor_page_style} | Text: '{txt[:30]}...'")
                count += 1
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
