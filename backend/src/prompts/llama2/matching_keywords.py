"""
Prompt for identifying unmatched job requirements in a candidate's resume. Outputs a JSON object with unmatched requirements and a summary.
"""
PROMPT = """
[INST] <<SYS>>
You will be given two lists:

1. A list of keywords extracted from a candidate's resume.
2. A list of keywords extracted from a job offer requirements.

Please analyze which job keywords are NOT mentioned in the resume keywords.
Return a list of the most important keywords that are present in the job requirements but missing from the resume:

- All keywords should contain one or two words only.
- Every keyword must in a new line.
- Do not include any surrounding commentary or explanations.
<</SYS>>

Resume Keywords:
{}

Job Requirements:
{}
[/INST]
"""
