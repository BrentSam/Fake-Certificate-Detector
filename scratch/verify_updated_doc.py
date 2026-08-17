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
        
        file_path = os.path.abspath("docs/Brent Project Report_updated.odt")
        file_url = uno.systemPathToFileUrl(file_path)
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())
        
        # Check standard style footer
        style_families = doc.StyleFamilies
        page_styles = style_families.getByName("PageStyles")
        standard_style = page_styles.getByName("Standard")
        footer_on = standard_style.getPropertyValue("FooterIsOn")
        print(f"FooterIsOn in updated doc: {footer_on}")
        
        # Check footer text
        footer_text = standard_style.getPropertyValue("FooterText")
        print(f"Footer text content: '{footer_text.getString()}'")
        
        # Check paragraphs
        print("\nVerifying updated paragraphs in TOC area:")
        text = doc.Text
        enum = text.createEnumeration()
        
        count = 0
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                if 78 <= count <= 160:
                    txt = el.getString()
                    style = el.getPropertyValue("ParaStyleName")
                    tabs = el.getPropertyValue("ParaTabStops")
                    has_tab_stop = "YES" if tabs else "NO"
                    repr_txt = repr(txt)
                    print(f"[{count:03d}] Style: {style} | TabStop: {has_tab_stop} | Text: {repr_txt}")
                count += 1
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
