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
        
        # Access document statistics
        try:
            document_properties = doc.getDocumentProperties()
            print("Document Title:", document_properties.Title)
        except Exception as e:
            print("Error getting DocumentProperties:", e)
            
        # In LibreOffice Writer, we can get page count via the document model's properties or controller
        try:
            # Page count can be retrieved from document properties or statistics
            # Let's inspect doc.DocumentProperties or doc.getUniqueMetadata()
            # Actually, doc has a PropertySet or we can use the cursor
            # Or we can query the page count from the controller
            controller = doc.getCurrentController()
            page_count = getattr(controller, "PageCount", "N/A")
            print(f"Page Count (Controller property): {page_count}")
        except Exception as e:
            print("Error getting PageCount from controller:", e)
            
        try:
            # Let's inspect document statistics property
            # For Writer, doc has a 'DocumentStatistics' property which is an array of NamedValue
            stats = doc.DocumentStatistics
            print("Document Statistics:")
            for val in stats:
                print(f" - {val.Name}: {val.Value}")
        except Exception as e:
            print("Error getting DocumentStatistics:", e)
        
        # Let's search for Table of Contents index.
        try:
            document_indexes = doc.getDocumentIndexes()
            print(f"Number of indexes: {document_indexes.getCount()}")
            for i in range(document_indexes.getCount()):
                idx = document_indexes.getByIndex(i)
                # Let's check service name and title
                serv_name = idx.getImplementationName() if hasattr(idx, "getImplementationName") else idx.ServiceName
                print(f"Index {i}: {serv_name} - Title: '{idx.Title}'")
        except Exception as e:
            print("Error getting indexes:", e)
            
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
