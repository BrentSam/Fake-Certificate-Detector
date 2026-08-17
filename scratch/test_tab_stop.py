import uno
import time
import subprocess
import os
import traceback

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
        
        doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
        text = doc.Text
        cursor = text.createTextCursor()
        text.insertString(cursor, "Hello World", False)
        
        # Get paragraph
        enum = text.createEnumeration()
        para = enum.nextElement()
        
        TabAlign_RIGHT = uno.Enum("com.sun.star.style.TabAlign", "RIGHT")
        
        print("Testing TabStop with uno.createUnoStruct...")
        try:
            tab = uno.createUnoStruct("com.sun.star.style.TabStop")
            tab.Position = 15000
            tab.Alignment = TabAlign_RIGHT
            
            # Let's print properties of TabStop
            print(f"tab.Position: {tab.Position}, type: {type(tab.Position)}")
            print(f"tab.Alignment: {tab.Alignment}, type: {type(tab.Alignment)}")
            print(f"tab.DecimalChar: {repr(tab.DecimalChar)}, type: {type(tab.DecimalChar)}")
            print(f"tab.FillChar: {repr(tab.FillChar)}, type: {type(tab.FillChar)}")
            
            # Let's set it as a tuple
            para.setPropertyValue("ParaTabStops", (tab,))
            print("Test Succeeded!")
        except Exception as e:
            print("Test Failed:")
            traceback.print_exc()

        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
