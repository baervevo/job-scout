PROMPT="""
You will be given two lists:

1. resume_keywords: A list of keywords extracted from a candidate's resume.
2. job_requirements: A list of keywords extracted from a job offer.
Please analyze which job keywords are NOT mentioned in the resume keywords.

Return your answer in JSON format with two fields:

{{
  "unmatched_requirements": [/* list of missing requirements */],
  "summary": "A concise summary describing what the resume may lack in relation to the job requirements."
}}

Here are the inputs:

Resume Keywords:
{}

Job Requirements:
{}
"""