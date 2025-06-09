PROMPT = """
You are an expert at analyzing resumes.

Task:  
From the input resume text, extract **only** important keywords and key phrases related to the candidate’s:  
- professional skills and technologies  
- job titles and work experience  
- educational degrees, certifications, and relevant courses  

Ignore all personal information (name, address, phone, email), section headers, hobbies, languages, divers license and other irrelevant details.  
Return the keywords and phrases as a simple, clean list without any explanation or extra text.

Resume:  
{}

Note: Please output only a string of keywords with no surrounding commentary. Do not add any explanations or additional text.
"""