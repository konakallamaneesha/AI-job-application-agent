import ollama

def match_job(resume_skills, job_details):

    prompt = f"""
Resume Skills:
{resume_skills}

Job Details:
{job_details}

Return ONLY this format:

Match Score: <number>

Matching Skills:
skill1, skill2

Missing Skills:
skill1, skill2

Do not explain.
Do not add names.
Do not add paragraphs.
Do not create information.
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]