# app.py
import streamlit as st
from io import BytesIO
from docx import Document

# We import inside the button click later to avoid crashing the whole app if there's an AI error.

st.set_page_config(page_title="AI Question Paper Generator", layout="wide")

st.title("🧠 Automatic Question Paper Generator using Generative AI")

st.markdown(
    """
This tool uses **Google Gemini (Generative AI)** to generate university-style question papers  
based on your subject, topics, and exam pattern.
"""
)

# ---- Sidebar ----
st.sidebar.header("⚙️ Configuration")

subject_name = st.sidebar.text_input("Subject Name", "Data Structures")
course_code = st.sidebar.text_input("Course Code", "CS701")
semester = st.sidebar.text_input("Semester", "7th")
exam_type = st.sidebar.selectbox(
    "Exam Type", ["Internal Test", "Mid-Semester", "End-Semester", "Lab Test"]
)
total_marks = st.sidebar.number_input("Total Marks (approximate)", 10, 200, 50)

difficulty_pattern = st.sidebar.selectbox(
    "Difficulty Pattern",
    [
        "Mixed: Balanced Easy, Medium, Hard",
        "Mostly Easy (for internal tests)",
        "Mostly Medium",
        "Challenging: Mostly Hard",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Question Pattern")

num_mcq = st.sidebar.number_input("Number of MCQs (1 mark each)", 0, 50, 5)
num_short = st.sidebar.number_input("Number of Short Answer Questions", 0, 30, 5)
num_long = st.sidebar.number_input("Number of Long/Descriptive Questions", 0, 20, 3)

st.sidebar.markdown("---")
st.sidebar.info(
    "Make sure your **Gemini API key** is correctly pasted in `gen_ai.py`."
)

# ---- Main input area ----
st.subheader("📚 Syllabus Topics / Units")
st.markdown("Enter each topic or unit on a new line:")

topics_input = st.text_area(
    "Topics",
    value=(
        "Unit 1: Introduction to Data Structures\n"
        "Stacks and Queues\n"
        "Linked Lists\n"
        "Trees and Binary Search Trees\n"
        "Graphs and Traversal Algorithms"
    ),
    height=150,
)
topics = [t.strip() for t in topics_input.splitlines() if t.strip()]

st.subheader("📝 General Instructions for Question Paper")
instructions = st.text_area(
    "Exam Instructions (will appear at top of paper)",
    value=(
        "1. Answer all questions.\n"
        "2. Figures to the right indicate full marks.\n"
        "3. Assume suitable data wherever necessary.\n"
        "4. Draw neat diagrams wherever appropriate."
    ),
    height=120,
)

st.markdown("---")

col1, _ = st.columns([1, 3])
with col1:
    generate_btn = st.button("🚀 Generate Question Paper", type="primary")

question_paper_text = ""
answer_key_text = ""
docx_bytes: BytesIO | None = None

from utils import build_docx

if generate_btn:
    if not topics:
        st.error("Please enter at least one topic or unit.")
    elif num_mcq == 0 and num_short == 0 and num_long == 0:
        st.error("Please set at least one non-zero question count.")
    else:
        from gen_ai import QuestionPaperGenerator  # imported here to avoid startup issues
        with st.spinner("Generating question paper using Gemini... ⏳"):
            try:
                gen = QuestionPaperGenerator()
                question_paper_text, answer_key_text = gen.generate_question_paper(
                    subject_name=subject_name,
                    course_code=course_code,
                    exam_type=exam_type,
                    semester=semester,
                    instructions=instructions,
                    topics=topics,
                    num_mcq=int(num_mcq),
                    num_short=int(num_short),
                    num_long=int(num_long),
                    difficulty_pattern=difficulty_pattern,
                    total_marks=int(total_marks),
                )
                st.success("Question paper generated successfully!")
            except Exception as e:
                st.error(f"Error while generating question paper: {e}")

if question_paper_text:
    tab1, tab2 = st.tabs(["📄 Question Paper", "✅ Answer Key"])
    with tab1:
        st.markdown("### 📝 Generated Question Paper")
        st.text(question_paper_text)
    with tab2:
        st.markdown("### ✅ Generated Answer Key")
        st.text(answer_key_text)

    docx_bytes = build_docx(
        subject_name=subject_name,
        course_code=course_code,
        exam_type=exam_type,
        semester=semester,
        total_marks=int(total_marks),
        question_paper=question_paper_text,
        answer_key=answer_key_text,
        instructions=instructions,
    )

    st.markdown("---")
    st.subheader("📥 Download")
    st.download_button(
        label="Download as .docx",
        data=docx_bytes,
        file_name=f"{subject_name.replace(' ', '_')}_question_paper.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
