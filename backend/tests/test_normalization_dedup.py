import pytest
from app.utils.skills import normalize_skill, normalize_skill_list
from app.services.normalization_service import job_normalizer
from app.services.deduplication_service import deduplication_service

def test_skill_normalization_aliases():
    assert normalize_skill("sklearn") == "scikit-learn"
    assert normalize_skill("scikit learn") == "scikit-learn"
    assert normalize_skill("scikit-learn") == "scikit-learn"
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("ts") == "TypeScript"
    assert normalize_skill("node") == "Node.js"
    assert normalize_skill("tf") == "TensorFlow"
    assert normalize_skill("k8s") == "Kubernetes"

    # List deduplication and normalization
    raw_list = ["sklearn", "scikit-learn", "js", "JavaScript", "Python"]
    normalized = normalize_skill_list(raw_list)
    assert normalized == ["scikit-learn", "JavaScript", "Python"]

def test_job_normalizer_experience():
    # Fresher cases
    lvl, min_y, max_y = job_normalizer.normalize_experience("0-1 years", "ML Intern", "College grads")
    assert lvl == "fresher"
    assert min_y == 0.0

    # Senior case
    lvl_sr, min_sr, max_sr = job_normalizer.normalize_experience("5+ years of experience", "Senior Engineer")
    assert lvl_sr == "senior"
    assert min_sr >= 5.0

def test_deterministic_deduplication():
    fp1 = deduplication_service.generate_deterministic_fingerprint(
        "Google Inc.", "Senior Software Engineer", "Mountain View, CA"
    )
    fp2 = deduplication_service.generate_deterministic_fingerprint(
        "google", "senior software engineer", "mountain view ca"
    )
    assert fp1 == fp2, "Fingerprints for normalized identical jobs must match exactly."

    existing_jobs = [{
        "id": "job_123",
        "fingerprint": fp1,
        "application_url": "https://careers.google.com/jobs/123",
        "company": "Google",
        "title": "Senior Software Engineer"
    }]

    new_job = {
        "company": "google",
        "title": "senior software engineer",
        "location": "mountain view ca",
        "application_url": "https://careers.google.com/jobs/123"
    }

    is_dup, matched_id = deduplication_service.check_is_duplicate(new_job, existing_jobs)
    assert is_dup is True
    assert matched_id == "job_123"
