import pytest
from app.agents.resume_agent import resume_profile_agent

def test_resume_text_skill_extraction():
    sample_resume = """
    Arjun Sharma
    Email: arjun.ai@example.com
    Phone: +91 9876543210
    Education: B.Tech in Artificial Intelligence and Data Science (2027)

    Technical Skills:
    Python, NumPy, Pandas, Scikit-learn, TensorFlow, MongoDB, Git.

    Projects:
    Predictive Model: Built a machine learning classifier with 92% accuracy using scikit-learn.
    """
    
    skills = resume_profile_agent.extract_skills(sample_resume)
    assert "Python" in skills
    assert "scikit-learn" in skills
    assert "TensorFlow" in skills
    assert "MongoDB" in skills
    assert "Pandas" in skills

    domains = resume_profile_agent.infer_domains(skills, sample_resume)
    assert "Machine Learning" in domains or "Artificial Intelligence" in domains

    roles = resume_profile_agent.infer_recommended_roles(domains, skills)
    assert any("Machine Learning" in r or "AI" in r for r in roles)

@pytest.mark.asyncio
async def test_parse_resume_to_profile():
    sample_text = (
        "Rahul Verma\n"
        "rahul.verma@example.com\n"
        "B.Tech in Computer Science 2026\n"
        "Experience: 0 years, fresher.\n"
        "Skills: React, TypeScript, JavaScript, Tailwind CSS, Node.js, HTML, CSS.\n"
    ).encode("utf-8")

    profile = await resume_profile_agent.parse_resume_to_profile("resume.txt", sample_text)
    assert profile["name"] == "Rahul Verma"
    assert profile["email"] == "rahul.verma@example.com"
    assert "React" in profile["skills"]
    assert "TypeScript" in profile["skills"]
    assert profile["experience_level"] == "fresher"
    assert profile["completeness_score"] >= 70
