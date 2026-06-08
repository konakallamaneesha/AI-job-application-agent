from backend.job_matcher import match_job

resume_skills = """
Python, Java, SQL, HTML, CSS,
JavaScript, React.js, Node.js,
Express.js, MongoDB
"""

job_details = """
Frontend Developer
Teamified
Remote in India
React.js
JavaScript
HTML
CSS
"""

result = match_job(
    resume_skills,
    job_details
)

print(result)