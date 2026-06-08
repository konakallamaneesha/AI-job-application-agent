import ollama

def generate_job_roles(skills):

    prompt = f"""
Resume Skills:

{skills}

Generate ONLY 5 Internshala internship categories.

Examples:

Web Development
ReactJS Development
Backend Development
Full Stack Development
Python Development
Machine Learning
Data Science
Cyber Security

Rules:
- Use only common internship categories.
- Maximum 3 words.
- One category per line.
- No explanations.
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