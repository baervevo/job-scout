PROMPT = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You will be given two lists:

1. A list of keywords extracted from a candidate's resume.
2. A list of keywords extracted from a job offer requirements.

Please analyze which job keywords are NOT mentioned in the resume keywords.
Return a list of the most important keywords that are present in the job requirements but missing from the resume:

- All keywords should contain one or two words only.
- Every keyword must be on a new line.
- Do not include any surrounding commentary or explanations.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Resume Keywords:
{}

Job Requirements:
{}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
