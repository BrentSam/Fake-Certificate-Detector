import uno
import time
import subprocess
import os
import re

def clean_text(text):
    return text.strip().replace('\uFFFD', ' ').replace('\u2013', '-').replace('\u2014', '-')

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
        
        headings = []
        
        # Regex patterns to detect headings/figures/tables
        patterns = [
            r"^Chapter\s+\d+:\s+.*",
            r"^\d+\.\d+\s+.*",
            r"^References",
            r"^Bibliography",
            r"^Appendix\s+[A-D]:\s+.*",
            r"^Figure\s+\d+\.\d+:\s+.*",
            r"^Table\s+\d+\.\d+:\s+.*"
        ]
        combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)
        
        count = 0
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                raw_txt = el.getString()
                cleaned = clean_text(raw_txt)
                if not cleaned:
                    continue
                
                # Check if it matches any pattern
                # Avoid matching TOC lines themselves!
                # Wait, TOC lines are also paragraphs. How to distinguish them?
                # Usually TOC lines have page numbers or dots, and they appear early in the document.
                # Let's check paragraph style. Heading styles are usually Heading 1, Heading 2, etc.,
                # while TOC lines are standard or Index style.
                # Let's print style and text of matches.
                style = el.getPropertyValue("ParaStyleName")
                
                if combined_pattern.match(cleaned):
                    try:
                        view_cursor.gotoRange(el.getStart(), False)
                        page_num = view_cursor.getPage()
                        headings.append((count, style, cleaned, page_num))
                        print(f"[{count:03d}] Page {page_num} ({style}): '{cleaned}'")
                    except Exception as e:
                        print(f"Error on para {count}: {e}")
                count += 1
                
        doc.close(True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
