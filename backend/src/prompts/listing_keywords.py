"""
Prompt for extracting relevant keywords from job listings
"""
PROMPT = """
You are a keyword extraction engine. Convert the following raw resume text into 10 keywords:
- Output ONLY the keywords related to necessary skills, experience, education, and certifications.
- Focus on the tech skills, programming languages, frameworks, tools, and relevant qualifications.
- Do not include any contact information, section headers, or irrelevant details.
- DO NOT enumerate the keywords, just provide them as a continuous string.

Resume:
{}

Note: Please output only the keywords with no surrounding commentary. DO NOT include any additional text or explanations. DO NOT enumerate the keywords!
"""
