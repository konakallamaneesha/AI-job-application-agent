import re


def extract_skills(resume_text):

    known_skills = [

        # Languages
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",

        # Frontend
        "HTML",
        "CSS",
        "JavaScript",
        "React",

        # Backend
        "Node.js",
        "Express.js",

        # Database
        "MongoDB",
        "MySQL",
        "PostgreSQL",

        # Cloud
        "AWS",
        "AWS Basics",

        # AI / ML
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "LangChain",
        "FAISS",
        "Ollama",
        "Llama",
        "SHAP",

        # Tools
        "Git",
        "GitHub",
        "Streamlit",

        # Security
        "JWT",
        "bcrypt",
        "OTP Authentication",

        # Concepts
        "Data Structures and Algorithms",
        "Object-Oriented Programming",
        "MERN Stack"
    ]

    found_skills = []

    text = resume_text.lower()

    for skill in known_skills:

        if skill.lower() in text:

            found_skills.append(skill)

    return ", ".join(found_skills)