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
        
        style_families = doc.StyleFamilies
        page_styles = style_families.getByName("PageStyles")
        standard_style = page_styles.getByName("Standard")
        
        width = standard_style.getPropertyValue("Width")
        left_margin = standard_style.getPropertyValue("LeftMargin")
        right_margin = standard_style.getPropertyValue("RightMargin")
        printable_width = width - left_margin - right_margin
        
        print(f"Page Width: {width}")
        print(f"Left Margin: {left_margin}")
        print(f"Right Margin: {right_margin}")
        print(f"Printable Width: {printable_width}")
        
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
