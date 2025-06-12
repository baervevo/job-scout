"""
Prompt for extracting relevant keywords from resumes
"""
PROMPT = """
[INST] <<SYS>>
You are a keyword extraction engine. Convert the following raw resume text into 30 keywords:
- IGNORE all information about hobbies, links, personal data, section headers.
- Output ONLY the keywords related to the candidate's skills, experience, education, and certifications.
- Focus on the tech skills, programming languages, frameworks, tools.
<</SYS>>
Resume:
{}
[/INST]
"""
