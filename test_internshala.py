from backend.job_search.internshala import (
    search_internshala,
    get_job_description
)

jobs = search_internshala("frontend")

print("=" * 50)

print(jobs[0]["title"])

skills = get_job_description(
    jobs[0]["url"]
)

print(skills)