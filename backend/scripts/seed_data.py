import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.mongo import connect_to_mongo, close_mongo_connection, get_database
from app.database.indexes import create_indexes
from app.core.security import hash_password
from app.services.normalization_service import job_normalizer
from app.services.deduplication_service import deduplication_service
from app.agents.job_classifier_agent import job_classifier_agent
from app.agents.match_agent import match_agent
from app.agents.job_discovery_agent import job_discovery_agent
from app.core.logging import logger

DEMO_CANDIDATE_EMAIL = "candidate@jobfusion.ai"
DEMO_CANDIDATE_PASS = "Candidate123!"

DEMO_JOBS = [
    {
        "title": "Machine Learning Engineer Intern",
        "company": "CognitiveAI Innovations",
        "location": "Bangalore, India",
        "location_type": "hybrid",
        "employment_type": "internship",
        "experience_required": "0-1 years (Fresher eligible)",
        "salary": "$25 - $35 / hr",
        "description": "We are seeking a Machine Learning Intern to assist in designing, testing, and optimizing machine learning models. You will work with Python, TensorFlow, scikit-learn, and Pandas on real-world datasets.",
        "skills": ["Python", "TensorFlow", "Machine Learning", "Scikit-learn", "Docker", "AWS"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/cognitive-ml-intern",
        "application_url": "https://example.com/jobs/cognitive-ml-intern/apply",
        "is_demo": True
    },
    {
        "title": "Junior AI & Data Science Engineer",
        "company": "DeepPulse Systems",
        "location": "Remote",
        "location_type": "remote",
        "employment_type": "full_time",
        "experience_required": "0-1 years",
        "salary": "$70,000 - $85,000 / yr",
        "description": "Develop predictive models and clean data pipelines using Python, NumPy, Pandas, Scikit-learn, and PyTorch. Early-career candidates with strong mathematical fundamentals are welcome.",
        "skills": ["Python", "NumPy", "Pandas", "Scikit-learn", "Machine Learning", "PyTorch", "SQL"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/deeppulse-ai-eng",
        "application_url": "https://example.com/jobs/deeppulse-ai-eng/apply",
        "is_demo": True
    },
    {
        "title": "Full Stack Software Engineer",
        "company": "AuraGrid Cloud",
        "location": "Remote",
        "location_type": "remote",
        "employment_type": "full_time",
        "experience_required": "1-3 years",
        "salary": "$80,000 - $105,000 / yr",
        "description": "Build high-throughput web applications with React, TypeScript, Node.js, and MongoDB. Design clean REST APIs and maintain test coverage.",
        "skills": ["React", "TypeScript", "Node.js", "MongoDB", "REST APIs", "Tailwind CSS", "Git"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/auragrid-fullstack",
        "application_url": "https://example.com/jobs/auragrid-fullstack/apply",
        "is_demo": True
    },
    {
        "title": "DevOps & Cloud Associate",
        "company": "InfraStack Global",
        "location": "Remote",
        "location_type": "remote",
        "employment_type": "full_time",
        "experience_required": "0-2 years",
        "salary": "$75,000 - $95,000 / yr",
        "description": "Help automate cloud deployments on AWS and Azure. Containerize applications using Docker and manage Kubernetes pods. Linux expertise required.",
        "skills": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "GitHub Actions", "Python"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/infrastack-devops",
        "application_url": "https://example.com/jobs/infrastack-devops/apply",
        "is_demo": True
    },
    {
        "title": "Frontend Engineer (React / Next.js)",
        "company": "PixelCraft Studio",
        "location": "Remote",
        "location_type": "remote",
        "employment_type": "full_time",
        "experience_required": "0-2 years",
        "salary": "$65,000 - $80,000 / yr",
        "description": "Create responsive, accessible user interfaces using Next.js, React, and modern CSS. Integrate frontend components with asynchronous REST services.",
        "skills": ["React", "Next.js", "JavaScript", "TypeScript", "HTML", "CSS", "Figma"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/pixelcraft-frontend",
        "application_url": "https://example.com/jobs/pixelcraft-frontend/apply",
        "is_demo": True
    },
    {
        "title": "Data Analyst Trainee",
        "company": "QuantumMetric Labs",
        "location": "Mumbai, India",
        "location_type": "onsite",
        "employment_type": "full_time",
        "experience_required": "0-1 years (Fresher)",
        "salary": "INR 6,00,000 - 8,50,000 / yr",
        "description": "Perform exploratory data analysis and build business intelligence dashboards using Tableau, Power BI, SQL, and Python Pandas.",
        "skills": ["Python", "Pandas", "SQL", "Tableau", "Power BI", "Data Science"],
        "source": "Compliant Verified Feed",
        "source_url": "https://example.com/jobs/quantummetric-analyst",
        "application_url": "https://example.com/jobs/quantummetric-analyst/apply",
        "is_demo": True
    }
]

async def seed_data():
    logger.info("Starting database seeding...")
    await connect_to_mongo()
    await create_indexes()
    db = get_database()

    # 1. Seed Demo Candidate User
    candidate_user = await db.users.find_one({"email": DEMO_CANDIDATE_EMAIL.lower()})
    now = datetime.now(timezone.utc)
    if not candidate_user:
        logger.info(f"Creating demo candidate user: {DEMO_CANDIDATE_EMAIL}")
        res = await db.users.insert_one({
            "name": "Arjun Sharma",
            "email": DEMO_CANDIDATE_EMAIL.lower(),
            "hashed_password": hash_password(DEMO_CANDIDATE_PASS),
            "role": "student",
            "created_at": now,
            "updated_at": now
        })
        user_id = str(res.inserted_id)
    else:
        user_id = str(candidate_user["_id"])

    # 2. Seed Candidate Profile
    profile_data = {
        "user_id": user_id,
        "name": "Arjun Sharma",
        "email": DEMO_CANDIDATE_EMAIL.lower(),
        "phone": "+91 98765 43210",
        "education": [
            {
                "degree": "B.Tech",
                "field": "Artificial Intelligence and Data Science",
                "institution": "National Institute of Technology",
                "graduation_year": 2027
            }
        ],
        "experience_level": "fresher",
        "years_of_experience": 0.0,
        "skills": [
            "Python",
            "NumPy",
            "Pandas",
            "scikit-learn",
            "TensorFlow",
            "MongoDB",
            "Machine Learning",
            "Git"
        ],
        "domains": [
            "Machine Learning",
            "Artificial Intelligence",
            "Data Science"
        ],
        "recommended_roles": [
            "Machine Learning Engineer",
            "AI Engineer",
            "ML Intern",
            "Data Scientist"
        ],
        "preferred_locations": ["Remote", "Bangalore"],
        "preferred_job_types": ["internship", "full_time"],
        "remote_preference": "remote",
        "minimum_match_score": 50,
        "completeness_score": 92,
        "projects": [
            {
                "title": "Predictive Health Analysis Model",
                "description": "Built neural network pipeline predicting patient outcomes with 89% precision.",
                "technologies": ["Python", "TensorFlow", "Pandas", "scikit-learn"]
            }
        ],
        "certifications": ["Deep Learning Specialization - Coursera"],
        "work_experiences": [],
        "created_at": now,
        "updated_at": now
    }
    await db.candidate_profiles.update_one(
        {"user_id": user_id},
        {"$set": profile_data},
        upsert=True
    )
    logger.info("Candidate profile seeded.")

    # 3. Discover Real-time Jobs from Live Public APIs
    scan_res = await job_discovery_agent.run(limit_per_source=25)
    await job_classifier_agent.run()
    logger.info(f"Discovered and classified {scan_res.records_processed} live opportunities.")

    # 4. Generate Personalized Matches for Candidate
    matches = await match_agent.match_user_with_jobs(user_id, profile_data)
    logger.info(f"Generated {len(matches)} personalized recommendations for demo candidate.")

    await close_mongo_connection()
    logger.info("Seeding process completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
