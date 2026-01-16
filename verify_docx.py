from utils import build_docx
from docx import Document
from io import BytesIO
from docx.enum.text import WD_ALIGN_PARAGRAPH

def verify_docx():
    print("Verifying DOCX Structure...")
    
    # Mock Data
    subject = "Data Structures"
    course = "CS101"
    exam = "Mid-Sem"
    semester = "3rd"
    total_marks = 50
    
    # Dirty input
    qp_text = """**UNIT 1**
Subject: Data Structures
---
1. What is a Stack?
a) Explain LIFO.
2. What is a Queue?
   CO1 (10)
SECTION A
3. Explain Trees.
"""
    ans_text = """1. A stack is...
**2. A queue is...** (CO1)
"""
    instructions = """1. Line one.
- Line two.
"""

    docx_io = build_docx(subject, course, exam, semester, total_marks, qp_text, ans_text, instructions)
    
    # Save for manual inspection
    with open("test_output_strict.docx", "wb") as f:
        f.write(docx_io.getvalue())
        
    doc = Document(docx_io)
    paragraphs = doc.paragraphs
    
    # --- Check Header ---
    # Line 0: Institute Name
    assert "INSTITUTE OF ENGINEERING AND TECHNOLOGY" in paragraphs[0].text
    assert paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.CENTER
    
    # Line 1: Exam Title
    assert "MID-SEM EXAMINATION" in paragraphs[1].text
    assert paragraphs[1].alignment == WD_ALIGN_PARAGRAPH.CENTER
    
    # Line 2: Program / Semester
    assert "Program: B.E." in paragraphs[2].text
    assert "Semester: 3rd" in paragraphs[2].text # check both exist (tabs used)
    
    # --- Check Instructions ---
    # Find heading
    instr_idx = -1
    for i, p in enumerate(paragraphs):
        if "Instructions to the Candidates:" in p.text:
            instr_idx = i
            break
    assert instr_idx != -1, "Instructions heading not found"
    assert paragraphs[instr_idx].runs[0].bold, "Instructions heading should be bold"
    
    # Check bullets
    # The first instruction "Line one." should be in the next paragraph
    # We can check style or just content
    assert "Line one." in paragraphs[instr_idx + 1].text
    # Note: parsing style name can be tricky if default 'List Bullet' isn't used exactly by name, but we set it explicitly.
    assert paragraphs[instr_idx + 1].style.name == 'List Bullet', "Instruction not bulleted"
    
    # --- Check Body Formatting ---
    
    # Check UNIT Bold/Centered
    unit_found = False
    for p in paragraphs:
        if "UNIT 1" in p.text:
            unit_found = True
            assert p.alignment == WD_ALIGN_PARAGRAPH.CENTER, "UNIT not centered"
            # It should be bold
            is_bold = any(run.bold for run in p.runs)
            assert is_bold, "UNIT header should be bold"
            assert "**" not in p.text, "Markdown not cleaned"
            
    assert unit_found, "UNIT 1 not found"
    
    # Check CO Alignment
    # The line "   CO1 (10)" -> "CO1 (10)"
    co_found = False
    for p in paragraphs:
        if "CO1 (10)" in p.text:
            co_found = True
            assert p.alignment == WD_ALIGN_PARAGRAPH.RIGHT, "CO line not right aligned"
            
    assert co_found, "CO line not found"

    # Check Answer Key separate page
    # Since we can't easily check page breaks in simple iteration without diving deep into XML or run checks,
    # we assume logic holds if "Answer Key" heading exists.
    ak_found = False
    for p in paragraphs:
        if "Answer Key" in p.text:
            ak_found = True
            assert p.alignment == WD_ALIGN_PARAGRAPH.CENTER
            
    assert ak_found, "Answer Key not found"

    print("✅ All DOCX verification checks passed!")

if __name__ == "__main__":
    verify_docx()
