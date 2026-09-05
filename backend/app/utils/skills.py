from typing import Dict, List, Set, Any

# Standard canonical domain taxonomy
DOMAIN_TAXONOMY: List[str] = [
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
    "Data Engineering",
    "Software Development",
    "Backend Development",
    "Frontend Development",
    "Full Stack Development",
    "DevOps",
    "Cloud Computing",
    "Cyber Security",
    "Software Testing / QA",
    "Mobile Development",
    "Salesforce",
    "Database / DBA",
    "Business Analysis",
    "Product Management",
    "UI/UX",
    "Sales",
    "Marketing",
    "Finance",
    "Human Resources",
    "Other"
]

# Canonical skill list categorized
CANONICAL_SKILLS: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL", "HTML", "CSS"
    ],
    "Frameworks & Web": [
        "React", "Node.js", "Express.js", "Next.js", "Vue.js", "Angular",
        "FastAPI", "Flask", "Django", "Spring Boot", "ASP.NET", "Ruby on Rails",
        "Tailwind CSS", "Bootstrap", "GraphQL", "REST APIs"
    ],
    "AI & Data": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "Data Science",
        "TensorFlow", "PyTorch", "scikit-learn", "Keras", "NumPy", "Pandas",
        "NLP", "Computer Vision", "LLMs", "LangChain", "Hugging Face", "OpenCV",
        "Spark", "Hadoop", "Airflow", "Tableau", "Power BI"
    ],
    "Databases": [
        "MongoDB", "PostgreSQL", "MySQL", "Redis", "SQLite", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j", "Firebase"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub Actions",
        "CI/CD", "Terraform", "Linux", "Nginx", "Ansible", "Jenkins"
    ],
    "Testing & QA": [
        "Selenium", "Cypress", "Jest", "Pytest", "JUnit", "Postman", "Playwright"
    ],
    "Product & Design": [
        "Figma", "Adobe XD", "UI/UX Design", "Wireframing", "Product Management",
        "Agile", "Scrum", "Jira"
    ]
}

# Skill alias normalization mapping (case-insensitive keys to canonical representation)
SKILL_ALIASES: Dict[str, str] = {
    # AI / ML
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit_learn": "scikit-learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "dl": "Deep Learning",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "llm": "LLMs",
    "llms": "LLMs",
    "cv": "Computer Vision",
    "nlp": "NLP",
    "natural language processing": "NLP",

    # Web & Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "py": "Python",
    "python3": "Python",
    "cpp": "C++",
    "c plus plus": "C++",
    "csharp": "C#",
    "c sharp": "C#",
    "golang": "Go",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "k8s": "Kubernetes",
    "amazon web services": "AWS",
    "google cloud platform": "GCP",
    "google cloud": "GCP",
    "microsoft azure": "Azure",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "spring": "Spring Boot",
    "springboot": "Spring Boot"
}

# Domain keyword mapping for deterministic domain classification
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "Artificial Intelligence": [
        "artificial intelligence", "ai engineer", "genai", "generative ai", "llm",
        "agentic", "neural networks", "prompt engineering", "langchain"
    ],
    "Machine Learning": [
        "machine learning", "ml engineer", "scikit-learn", "tensorflow", "pytorch",
        "model training", "deep learning", "predictive modeling", "pandas", "numpy"
    ],
    "Data Science": [
        "data science", "data scientist", "statistical analysis", "analytics",
        "data mining", "predictive analytics", "jupyter", "r programming", "eda"
    ],
    "Data Engineering": [
        "data engineer", "etl", "data pipeline", "airflow", "spark", "hadoop",
        "kafka", "data warehouse", "snowflake", "bigquery", "databricks"
    ],
    "Frontend Development": [
        "frontend", "front-end", "react", "vue", "angular", "css", "html5",
        "javascript", "typescript", "tailwind", "ui developer", "web developer"
    ],
    "Backend Development": [
        "backend", "back-end", "fastapi", "django", "flask", "node.js", "express.js",
        "spring boot", "microservices", "rest api", "graphql", "server-side"
    ],
    "Full Stack Development": [
        "full stack", "fullstack", "mern", "mean", "lamp", "full-stack developer"
    ],
    "DevOps": [
        "devops", "ci/cd", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "infrastructure as code", "helm", "github actions"
    ],
    "Cloud Computing": [
        "cloud computing", "aws", "azure", "gcp", "cloud architect", "cloud engineer",
        "serverless", "lambda", "s3", "ec2"
    ],
    "Cyber Security": [
        "cyber security", "infosec", "penetration testing", "vulnerability",
        "soc analyst", "ethical hacking", "siem", "network security"
    ],
    "Software Testing / QA": [
        "qa", "quality assurance", "test engineer", "automation testing", "selenium",
        "cypress", "pytest", "unit testing", "manual testing", "playwright"
    ],
    "Mobile Development": [
        "android", "ios", "react native", "flutter", "swift", "kotlin", "mobile app"
    ],
    "Salesforce": [
        "salesforce", "apex", "soql", "visualforce", "lightning web components", "crm"
    ],
    "Database / DBA": [
        "dba", "database administrator", "database engineer", "sql server", "oracle dba",
        "mongodb admin", "database tuning"
    ],
    "Business Analysis": [
        "business analyst", "requirements gathering", "stakeholder", "brd", "bi", "user stories"
    ],
    "Product Management": [
        "product manager", "product owner", "roadmap", "feature prioritization", "mvp", "kpis"
    ],
    "UI/UX": [
        "ui/ux", "ux designer", "ui designer", "figma", "wireframing", "user research", "prototyping"
    ],
    "Software Development": [
        "software engineer", "software developer", "programmer", "sde", "coding"
    ]
}

def normalize_skill(skill: Any) -> str:
    """Normalize a single skill string to canonical form."""
    if skill is None:
        return ""
    if isinstance(skill, (list, tuple, set)):
        # If a sequence was passed, join or take first
        sub_skills = [normalize_skill(x) for x in skill if x]
        return sub_skills[0] if sub_skills else ""
    if not isinstance(skill, str):
        skill = str(skill)

    cleaned = skill.strip()
    lower = cleaned.lower()
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower]
    
    # Check canonical skills by exact match ignoring case
    for category, skill_list in CANONICAL_SKILLS.items():
        for s in skill_list:
            if s.lower() == lower:
                return s
    
    # Return original stripped if not in dictionary
    return cleaned

def normalize_skill_list(skills: Any) -> List[str]:
    """Normalize and deduplicate a list of skill strings while preserving order."""
    if not skills:
        return []
    if isinstance(skills, str):
        # Could be comma-separated
        skills = skills.split(",")
    elif not isinstance(skills, (list, tuple, set)):
        skills = [skills]

    seen: Set[str] = set()
    result: List[str] = []
    for s in skills:
        if isinstance(s, (list, tuple, set)):
            for sub in s:
                norm = normalize_skill(sub)
                if norm and norm.lower() not in seen:
                    seen.add(norm.lower())
                    result.append(norm)
        else:
            norm = normalize_skill(s)
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                result.append(norm)
    return result

def get_all_known_skills() -> Set[str]:
    """Return flat set of all canonical skills and aliases."""
    skills = set(SKILL_ALIASES.keys())
    for category, skill_list in CANONICAL_SKILLS.items():
        for s in skill_list:
            skills.add(s.lower())
    return skills
