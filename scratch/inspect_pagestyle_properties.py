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
        
        # Print all properties
        print("PageStyle properties:")
        properties = standard_style.getPropertySetInfo().getProperties()
        matching_props = []
        for prop in properties:
            name = prop.Name
            matching_props.append(name)
            
        matching_props.sort()
        for name in matching_props:
            if "foot" in name.lower() or "header" in name.lower() or "page" in name.lower():
                val = standard_style.getPropertyValue(name)
                print(f" - {name} = {val}")
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
