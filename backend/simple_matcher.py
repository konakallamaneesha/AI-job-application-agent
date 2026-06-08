import re

def calculate_match(
    resume_skills,
    jd_skills
):

    resume_text = resume_skills.lower()

    matched = []
    missing = []

    for skill in jd_skills:

        pattern = (
            r"\b"
            + re.escape(
                skill.lower()
            )
            + r"\b"
        )

        if re.search(
            pattern,
            resume_text
        ):

            matched.append(
                skill
            )

        else:

            missing.append(
                skill
            )

    score = 0

    if jd_skills:

        score = int(
            len(matched)
            /
            len(jd_skills)
            * 100
        )

    return {
        "score": score,
        "matched": matched,
        "missing": missing
    }