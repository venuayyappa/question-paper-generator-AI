# gen_ai.py
import os
import google.generativeai as genai

class QuestionPaperGenerator:
    def __init__(self):
        # Load API key securely from environment
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    def generate_question_paper(
        self,
        subject_name,
        course_code,
        exam_type,
        semester,
        instructions,
        topics,
        num_mcq,
        num_short,
        num_long,
        difficulty_pattern,
        total_marks,
    ):
        topics_text = "\n".join(f"- {t}" for t in topics)

        prompt = f"""
You are a professional university exam question setter.
Generate a properly formatted question paper followed by an answer key.

FORMAT EXACTLY:

### QUESTION PAPER
<Complete formatted exam paper>

### ANSWER KEY
<Number-wise answers>

Details:
Subject: {subject_name}
Course Code: {course_code}
Semester: {semester}
Exam Type: {exam_type}
Total Marks: {total_marks}

Instructions:
{instructions}

Topics to cover:
{topics_text}

Questions required:
MCQs: {num_mcq}
Short Answer: {num_short}
Long Answer: {num_long}

Difficulty: {difficulty_pattern}
"""

        response = self.model.generate_content(prompt)
        content = response.text

        if "### ANSWER KEY" in content:
            q, a = content.split("### ANSWER KEY", 1)
            return q.replace("### QUESTION PAPER", "").strip(), a.strip()
        else:
            return content.strip(), "Answer key not generated."
