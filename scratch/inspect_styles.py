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
        
        # Access style families
        style_families = doc.StyleFamilies
        print("Style Families:")
        for name in style_families.getElementNames():
            print(f" - {name}")
            
        page_styles = style_families.getByName("PageStyles")
        print("\nPage Styles:")
        for name in page_styles.getElementNames():
            style = page_styles.getByName(name)
            # Check if this page style is in use or properties
            is_used = getattr(style, "IsInUse", "N/A")
            footer_on = getattr(style, "FooterOn", "N/A")
            header_on = getattr(style, "HeaderOn", "N/A")
            print(f" - {name} (In Use: {is_used}, FooterOn: {footer_on}, HeaderOn: {header_on})")
            
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
