import subprocess

from src.prompts.job_details import PROMPT

job_description = ('...Job Title  - Senior <b>Python Developer </b>with AWS Experience   Experience  - 5 to 7 '
                   'Years \r\n  Employment Type  - Full-Time (Remote)*\r\n  Company  - TechnicaX \r\n  Project  - '
                   'Customer-Facing Project \r\n About TechnicaX \r\n TechnicaX is a leading technology consulting '
                   'firm focused.')

prompt = PROMPT.format(job_description)

result = subprocess.run(
    ["ollama", "run", "llama2"],
    input=prompt,
    capture_output=True,
    text=True,
    encoding="utf-8"
)

print("Output:\n", result.stdout)
