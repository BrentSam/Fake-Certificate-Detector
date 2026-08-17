import uno
import time
import subprocess
import os
import re
import sys

def clean_text(text):
    return text.strip().replace('\uFFFD', ' ').replace('\u2013', '-').replace('\u2014', '-')

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

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
        
        # Load classes and enums dynamically using PyUNO APIs
        TabStop = uno.getClass("com.sun.star.style.TabStop")
        TabAlign_RIGHT = uno.Enum("com.sun.star.style.TabAlign", "RIGHT")
        ParagraphAdjust_CENTER = uno.Enum("com.sun.star.style.ParagraphAdjust", "CENTER")
        
        file_path = os.path.abspath("docs/Brent Project Report.odt")
        file_url = uno.systemPathToFileUrl(file_path)
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())
        
        controller = doc.getCurrentController()
        view_cursor = controller.getViewCursor()
        
        text = doc.Text
        
        # Step 1: Scan and map headings, figures, tables in body
        print("Scanning document body to map pages...")
        enum = text.createEnumeration()
        
        paragraphs = []
        while enum.hasMoreElements():
            el = enum.nextElement()
            if el.supportsService("com.sun.star.text.Paragraph"):
                paragraphs.append(el)
                
        # Find Chapter 1 start index
        chapter_1_idx = -1
        for idx, el in enumerate(paragraphs):
            txt = clean_text(el.getString())
            if txt == "CHAPTER 1":
                chapter_1_idx = idx
                print(f"Found Chapter 1 start at paragraph index {idx}")
                break
                
        if chapter_1_idx == -1:
            print("Error: Could not find CHAPTER 1 paragraph in the body!")
            doc.close(True)
            return
            
        subheading_map = {}
        figure_map = {}
        table_map = {}
        
        # Scan body (from chapter_1_idx to end)
        for idx in range(chapter_1_idx, len(paragraphs)):
            el = paragraphs[idx]
            txt = clean_text(el.getString())
            if not txt:
                continue
                
            # Check subheadings like "1.1  Background and Motivation"
            subheading_match = re.match(r"^(\d+\.\d+)\s+.*", txt)
            if subheading_match:
                prefix = subheading_match.group(1)
                view_cursor.gotoRange(el.getStart(), False)
                page = view_cursor.getPage()
                if prefix not in subheading_map:
                    subheading_map[prefix] = page
                    print(f"Subheading Map: {prefix} -> Page {page} ('{txt[:40]}...')")
                    
            # Check figures like "Figure 6.1: User Registration"
            figure_match = re.match(r"^(Figure\s+\d+\.\d+)\s*:?\s+.*", txt, re.IGNORECASE)
            if figure_match:
                prefix = figure_match.group(1).replace("  ", " ") # standardize spaces
                view_cursor.gotoRange(el.getStart(), False)
                page = view_cursor.getPage()
                if prefix not in figure_map:
                    figure_map[prefix] = page
                    print(f"Figure Map: {prefix} -> Page {page} ('{txt[:40]}...')")
                    
            # Check tables like "Table 3.1: Hardware Requirements"
            table_match = re.match(r"^(Table\s+\d+\.\d+)\s*:?\s+.*", txt, re.IGNORECASE)
            if table_match:
                prefix = table_match.group(1).replace("  ", " ") # standardize spaces
                view_cursor.gotoRange(el.getStart(), False)
                page = view_cursor.getPage()
                if prefix not in table_map:
                    table_map[prefix] = page
                    print(f"Table Map: {prefix} -> Page {page} ('{txt[:40]}...')")

        # Manual mappings for major headings & appendices
        manual_mappings = {
            "chapter 1:  introduction": 13,
            "chapter 2:  project overview": 20,
            "chapter 3:  system model": 24,
            "chapter 4:  methodology": 30,
            "chapter 5:  implementation": 36,
            "chapter 6:  results and discussion": 47,
            "chapter 7:  conclusion and future work": 58,
            "chapter 8:  testing and quality assurance": 63,
            "chapter 9:  bibliography": 67,
            "references": 67,
            "appendix a:  application entry point and configuration": 68,
            "appendix b:  requirements and dependencies": 68,
            "appendix c:  installation and execution guide": 68,
            "appendix d:  glossary of terms": 68,
        }

        # Step 2: Configure Page numbering in Footer of PageStyle "Standard"
        print("Configuring page numbers in page style standard footer...")
        style_families = doc.StyleFamilies
        page_styles = style_families.getByName("PageStyles")
        standard_style = page_styles.getByName("Standard")
        
        # Enable footer using the correct property: FooterIsOn
        standard_style.setPropertyValue("FooterIsOn", True)
        
        # Get footer text and cursor
        footer_text = standard_style.getPropertyValue("FooterText")
        footer_cursor = footer_text.createTextCursor()
        
        # Clear footer content and insert page number field
        footer_text.setString("")
        page_num_field = doc.createInstance("com.sun.star.text.textfield.PageNumber")
        footer_text.insertTextContent(footer_cursor, page_num_field, False)
        
        # Center align the footer paragraph
        footer_cursor.gotoStart(False)
        footer_cursor.setPropertyValue("ParaAdjust", ParagraphAdjust_CENTER)
        
        # Step 3: Update Table of Contents, Figures, Tables in Front Matter
        print("Updating Table of Contents, Figures, and Tables in front matter...")
        
        # Create TabStop structure
        tab = TabStop()
        tab.Position = 15250 # printable width in 1/100th mm
        tab.Alignment = TabAlign_RIGHT
        tab.FillChar = uno.Char('.')
        tab.DecimalChar = uno.Char('.')
        
        # Wrap in uno.Any sequence
        tab_stops_any = uno.Any("[]com.sun.star.style.TabStop", (tab,))
        
        # Iterate through front matter paragraphs (before Chapter 1)
        for idx in range(chapter_1_idx):
            el = paragraphs[idx]
            txt = el.getString()
            cleaned_txt = clean_text(txt)
            if not cleaned_txt:
                continue
                
            matched_page = None
            orig_txt = txt.rstrip() # keep leading whitespace indent
            
            # 1. Check if it's a manual heading mapping
            lookup_key = cleaned_txt.lower()
            if lookup_key in manual_mappings:
                matched_page = manual_mappings[lookup_key]
                print(f"TOC Heading Match: '{orig_txt}' -> Page {matched_page}")
                
            # 2. Check if it's a sub-heading like "        1.1  Background and Motivation"
            if matched_page is None:
                sub_match = re.match(r"^\s*(\d+\.\d+)\s+.*", orig_txt)
                if sub_match:
                    prefix = sub_match.group(1)
                    if prefix in subheading_map:
                        matched_page = subheading_map[prefix]
                        print(f"TOC Subheading Match: '{orig_txt}' -> Page {matched_page}")
                        
            # 3. Check if it's a figure entry like "Figure 6.1:  User Registration (Sign Up) Page"
            if matched_page is None:
                fig_match = re.match(r"^\s*(Figure\s+\d+\.\d+)\s*:?\s+.*", orig_txt, re.IGNORECASE)
                if fig_match:
                    prefix = fig_match.group(1).replace("  ", " ") # standardize spaces
                    if prefix in figure_map:
                        matched_page = figure_map[prefix]
                        print(f"TOC Figure Match: '{orig_txt}' -> Page {matched_page}")
                        
            # 4. Check if it's a table entry like "Table 3.1:  Hardware Requirements"
            if matched_page is None:
                tbl_match = re.match(r"^\s*(Table\s+\d+\.\d+)\s*:?\s+.*", orig_txt, re.IGNORECASE)
                if tbl_match:
                    prefix = tbl_match.group(1).replace("  ", " ") # standardize spaces
                    if prefix in table_map:
                        matched_page = table_map[prefix]
                        print(f"TOC Table Match: '{orig_txt}' -> Page {matched_page}")
            
            # If we matched a page number, update the paragraph text and add the right tab stop
            if matched_page is not None:
                new_text = f"{orig_txt}\t{matched_page}"
                el.setString(new_text)
                uno.invoke(el, "setPropertyValue", ("ParaTabStops", tab_stops_any))
                
        # Save document
        save_path = os.path.abspath("docs/Brent Project Report_updated.odt")
        save_url = uno.systemPathToFileUrl(save_path)
        print(f"Saving updated document to {save_path}...")
        doc.storeToURL(save_url, ())
        doc.close(True)
        print("Success! Document saved successfully.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error occurred: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
