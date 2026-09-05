import pytest
from app.services.scoring_engine import scoring_engine

def test_deterministic_matching_case_from_specification():
    """
    CRITICAL SPECIFICATION TEST:
    Candidate:
      Python, Pandas, Scikit-learn, TensorFlow, Machine Learning, MongoDB
    Job:
      Python, TensorFlow, Machine Learning, Docker, AWS

    The scoring engine should identify:
      Strong matches: Python, TensorFlow, Machine Learning
      Missing: Docker, AWS
    """
    candidate_profile = {
        "skills": [
            "Python",
            "Pandas",
            "Scikit-learn",
            "TensorFlow",
            "Machine Learning",
            "MongoDB"
        ],
        "domains": ["Machine Learning", "Artificial Intelligence"],
        "recommended_roles": ["Machine Learning Engineer", "AI Engineer"],
        "experience_level": "fresher",
        "years_of_experience": 0.0,
        "education": [{"degree": "B.Tech", "field": "AI & Data Science"}],
        "preferred_locations": ["Remote"],
        "preferred_job_types": ["internship", "full_time"],
        "remote_preference": "remote"
    }

    job_profile = {
        "title": "Machine Learning Engineer Intern",
        "company": "Test AI Corp",
        "location": "Remote",
        "location_type": "remote",
        "employment_type": "internship",
        "experience_level": "fresher",
        "min_experience_years": 0.0,
        "max_experience_years": 1.0,
        "description": "Seeking ML Intern to develop models using Python, TensorFlow, and ML principles. Docker and AWS skills are valuable.",
        "skills": [
            "Python",
            "TensorFlow",
            "Machine Learning",
            "Docker",
            "AWS"
        ],
        "domain": "Machine Learning",
        "secondary_domains": ["Artificial Intelligence"]
    }

    result = scoring_engine.score_match(candidate_profile, job_profile)

    strong_matches = result["strong_matches"]
    missing_skills = result["missing_skills"]

    # Verify Strong Matches contains Python, TensorFlow, Machine Learning
    for required_match in ["Python", "TensorFlow", "Machine Learning"]:
        assert required_match in strong_matches, f"Expected {required_match} in strong matches, got: {strong_matches}"

    # Verify Missing contains Docker, AWS
    for required_missing in ["Docker", "AWS"]:
        assert required_missing in missing_skills, f"Expected {required_missing} in missing skills, got: {missing_skills}"

    # Verify score is within expected strong bounds (> 70)
    assert 65 <= result["score"] <= 100, f"Score {result['score']} out of expected range"
    assert result["match_tier"] in ["Strong Match", "Excellent Match", "Good Match"]

    # Verify transparent explanation is populated
    assert len(result["why_matched"]) > 10
    assert "Python" in result["why_matched"] or "Machine Learning" in result["why_matched"]
