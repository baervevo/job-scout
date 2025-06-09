PROMPT = """
You are a keyword extraction engine. Convert the following raw resume text into 30 keywords:
- IGNORE all information about hobbies, links and personal data.
- Output ONLY the keywords related to the candidate's skills, experience, education, and certifications.
- Focus on the tech skills, programming languages, frameworks, tools, and relevant qualifications.
- Do not include any personal information, section headers, or irrelevant details.
- DO NOT enumerate the keywords, just provide them as a continuous string.

Resume:
{}

Note: Please output only the keywords with no surrounding commentary. DO NOT include any additional text or explanations. DO NOT enumerate the keywords!
"""
