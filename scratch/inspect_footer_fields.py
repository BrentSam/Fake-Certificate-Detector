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
        
        style_families = doc.StyleFamilies
        page_styles = style_families.getByName("PageStyles")
        standard_style = page_styles.getByName("Standard")
        
        footer_text = standard_style.getPropertyValue("FooterText")
        
        # In LibreOffice Writer, we can access text fields from the document's TextFieldMasters or the text range itself
        print("Footer Text Content:", repr(footer_text.getString()))
        
        # Iterate through text content inside footer_text
        enum = footer_text.createEnumeration()
        while enum.hasMoreElements():
            el = enum.nextElement()
            print(f"Element class: {el.getImplementationName() if hasattr(el, 'getImplementationName') else type(el)}")
            # If it has text portions
            if hasattr(el, "createEnumeration"):
                portions = el.createEnumeration()
                while portions.hasMoreElements():
                    port_el = portions.nextElement()
                    p_type = port_el.TextPortionType
                    print(f" - Portion Type: {p_type} | Text: {repr(port_el.getString())}")
                    if p_type == "TextField":
                        field = port_el.TextField
                        print(f"   * TextField Service: {field.SupportedServiceNames}")
                        
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
