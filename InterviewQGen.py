	import re
import random

# A minimal list of common technical skills for demonstration purposes
SKILL_KEYWORDS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "SQL",
    "NoSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "REST APIs",
    "GraphQL",
    "Agile",
    "Scrum",
    "Machine Learning",
    "Deep Learning",
    "Data Analysis",
    "Linux",
    "Unix",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "Django",
    "Flask",
    "TensorFlow",
    "PyTorch"
]

def extract_skills(text):
    """Return a list of known skills found in the given job description text."""
    lowered = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        # Use word boundaries to avoid partial matches (e.g., "Java" in "JavaScript")
        pattern = r"\\b" + re.escape(skill.lower()) + r"\\b"
        if re.search(pattern, lowered):
            found.add(skill)
    return list(found)

def generate_questions(skills):
    """Create interview questions based on extracted skills using simple templates."""
    if not skills:
        return ["Can you describe your overall experience related to this role?"]
    templates = [
        "Can you describe your experience with {}?",
        "What challenges have you faced while working with {}?",
        "How do you stay current with developments in {}?",
        "Give an example of a project where you used {}.",
        "What best practices do you follow when using {}?"
    ]
    questions = []
    for skill in skills:
        tmpl = random.choice(templates)
        questions.append(tmpl.format(skill))
    return questions

def main():
    # Minimal inline job description for demonstration
    sample_job = (
        "We are seeking a Software Engineer with strong proficiency in Python, Docker, and AWS. "
        "The candidate should have experience building REST APIs, using Git for version control, "
        "and working in Agile development environments."
    )
    print("Job Description:\n")
    print(sample_job)
    skills = extract_skills(sample_job)
    print("\nExtracted Skills: " + (", ".join(skills) if skills else "None"))
    questions = generate_questions(skills)
    print("\nGenerated Interview Questions:")
    for idx, q in enumerate(questions, 1):
        print(f"{idx}. {q}")

if __name__ == "__main__":
    main()
