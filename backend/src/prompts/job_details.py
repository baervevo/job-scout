PROMPT = """
You are a JSON-extraction engine. Convert the following raw job description text into exactly the JSON schema below:
— Do not add any extra fields or prose.
— Do not change the structure or key names; output only valid JSON matching the schema.
- Use only the data provided in the job description.

Schema:
{{
    "required_qualifications": "List[str]",
    "preferred_qualifications": "List[str]",
    "experience": "List[str]",
    "education": "List[str]"
}}

Job Description:
{}

Note: Please output only a valid JSON matching the EXACT schema with no surrounding commentary.
"""
