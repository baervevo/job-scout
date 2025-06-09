PROMPT = """
You are a JSON-extraction engine. Convert the following raw resume text into exactly the JSON schema below:
— Do not add any extra fields or prose.
— Do not change the structure or key names; output only valid JSON matching the schema.
- If there is no significant information for a field, return an empty list.
- All list values must be short, descriptive strings (keywords or short phrases only).
- Ignore all information about hobbies, links and personal data.
- Output ONLY the JSON object, matching the exact schema

Schema:
{{
  "skills": [string],
  "experience": [string],
  "education": [string],
  "certifications": [string]
}}

Resume:
{}


Note: Please output only a valid JSON matching the EXACT schema with no surrounding commentary.
"""