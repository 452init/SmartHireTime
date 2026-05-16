import json


def build_interview_question_prompt(
    job_title, level="Mid-Level", category="Technical", question_count=3, focus_areas=None
):
    focus_areas = [str(area).strip() for area in (focus_areas or []) if str(area).strip()]
    focus_line = ""
    if focus_areas:
        focus_line = f"\nAlso consider these focus areas: {', '.join(focus_areas)}\n"

    return f"""
Create exactly {question_count} thoughtful interview questions for a "{job_title}" role.

The questions should:
- Be specific to the role
- Match a {level} seniority level
- Focus on {category} aspects of the role
- Test real judgment, experience, and communication
- Avoid generic interview questions
- Be concise enough for a hiring manager to read quickly
{focus_line}
Return this JSON shape:
{{
  "questions": [
    {{
      "question": "Question one",
      "difficulty": "Easy"
    }},
    {{
      "question": "Question two",
      "difficulty": "Medium"
    }}
  ]
}}

Each difficulty must be one of: "Easy", "Medium", "Hard".
"""


def parse_questions(ai_json_text, question_count=3):
    parsed = json.loads(ai_json_text)
    questions = parsed.get("questions")

    if not isinstance(questions, list):
        raise ValueError("AI response did not include a questions array.")

    cleaned_questions = []

    for question in questions:
        if isinstance(question, dict):
            text = str(question.get("question", "")).strip()
            difficulty = str(question.get("difficulty", "Medium")).strip()
        else:
            text = str(question).strip()
            difficulty = "Medium"

        if difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = "Medium"

        if text:
            cleaned_questions.append({"question": text, "difficulty": difficulty})

    return cleaned_questions[:question_count]
