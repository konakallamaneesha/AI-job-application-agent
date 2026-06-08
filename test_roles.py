from backend.role_generator import (
    generate_roles
)

skills = """
Python
TensorFlow
PyTorch
Machine Learning
NLP
Computer Vision
"""

roles = generate_roles(
    skills
)

print(roles)