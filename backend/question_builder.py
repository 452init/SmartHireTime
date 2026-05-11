import json


def build_interview_question_prompt(job_title):
    return f"""
Create exactly 3 thoughtful interview questions for a "{job_title}" role.

The questions should:
- Be specific to the role
- Test real judgment, experience, and communication
- Avoid generic interview questions
- Be concise enough for a hiring manager to read quickly

Return this JSON shape:
{{
  "questions": [
    "Question one",
    "Question two",
    "Question three"
  ]
}}
"""


def parse_questions(ai_json_text):
    parsed = json.loads(ai_json_text)
    questions = parsed.get("questions")

    if not isinstance(questions, list):
        raise ValueError("AI response did not include a questions array.")

    cleaned_questions = [
        str(question).strip() for question in questions if str(question).strip()
    ]
    return cleaned_questions[:3]
