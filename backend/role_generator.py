import requests


def generate_roles(skills):

    prompt = f"""
Given these resume skills:

{skills}

Generate ONLY 5 suitable internship/job roles.

Rules:
- Return only role names.
- No company names.
- No explanations.
- No numbering.
- One role per line.

Example:

Frontend Developer
React Developer
Full Stack Developer
Backend Developer
Software Engineer
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        data = response.json()

        if "response" not in data:
            return []

        output = data["response"]

        roles = []

        for line in output.split("\n"):

            line = line.strip()

            if not line:
                continue

            if (
                "as requested" in line.lower()
                or "output contains" in line.lower()
                or "here are" in line.lower()
            ):
                break

            for prefix in [
                "1.",
                "2.",
                "3.",
                "4.",
                "5.",
                "-",
                "*"
            ]:

                if line.startswith(prefix):

                    line = line.replace(
                        prefix,
                        ""
                    ).strip()

            line = (
                line.replace('"', "")
                    .replace("'", "")
                    .strip()
            )

            if line:
                roles.append(line)

        return roles[:5]

    except Exception as e:

        print(
            f"Ollama Error: {e}"
        )

        return []