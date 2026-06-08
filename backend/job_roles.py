def get_search_roles(skills):

    roles = []

    skills = skills.lower()

    # AI / ML

    if (
        "machine learning" in skills
        or "tensorflow" in skills
        or "pytorch" in skills
        or "shap" in skills
    ):

        roles.append(
            "Machine Learning"
        )

        roles.append(
            "Data Science"
        )

    # LLM / GenAI

    if (
        "langchain" in skills
        or "ollama" in skills
        or "llama" in skills
        or "faiss" in skills
    ):

        roles.append(
            "Artificial Intelligence"
        )

    # Frontend

    if (
        "html" in skills
        or "css" in skills
        or "javascript" in skills
        or "react" in skills
    ):

        roles.append(
            "Web Development"
        )

        roles.append(
            "ReactJS Development"
        )

    # Backend

    if (
        "node.js" in skills
        or "express.js" in skills
        or "mongodb" in skills
    ):

        roles.append(
            "Backend Development"
        )

    # Full Stack

    if (
        (
            "react" in skills
            or "html" in skills
            or "javascript" in skills
        )
        and
        (
            "node.js" in skills
            or "express.js" in skills
            or "mongodb" in skills
        )
    ):

        roles.append(
            "Full Stack Development"
        )

    # Python

    if "python" in skills:

        roles.append(
            "Python Development"
        )

    # Java

    if "java" in skills:

        roles.append(
            "Java Development"
        )

    # Cloud

    if (
        "aws" in skills
        or "cloud" in skills
    ):

        roles.append(
            "Cloud Computing"
        )

    roles = list(
        dict.fromkeys(roles)
    )

    return roles[:10]