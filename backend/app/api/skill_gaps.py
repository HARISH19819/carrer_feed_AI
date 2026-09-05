from fastapi import APIRouter, HTTPException, Depends
from collections import Counter
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.utils.skills import normalize_skill

router = APIRouter(prefix="/skill-gaps", tags=["Skill Gaps"])

SKILL_IMPORTANCE_EXPLANATIONS = {
    "Docker": "Containerization standard used across modern cloud deployments and microservices.",
    "AWS": "Most requested cloud platform across engineering, DevOps, and ML deployment roles.",
    "Kubernetes": "Orchestrates scalable distributed services; opens doors to senior cloud and DevOps positions.",
    "CI/CD": "Essential automated testing and deployment workflow required by tech teams.",
    "PostgreSQL": "Gold-standard relational database with advanced indexing and JSON support.",
    "MongoDB": "Flexible document database used heavily in modern full-stack web architectures.",
    "FastAPI": "High-performance Python web framework favored for asynchronous AI and microservice APIs.",
    "React": "Leading frontend UI framework commanding high demand in tech and product companies.",
    "TypeScript": "Type-safe JavaScript superset preventing runtime bugs in enterprise applications.",
    "PyTorch": "Primary deep learning framework powering modern LLM and neural network research.",
    "TensorFlow": "Production ML framework widely utilized for on-device and enterprise inference.",
    "Git": "Universal version control system required in all software collaboration.",
    "Linux": "Fundamental server operating system for backend, cloud, and AI engineering.",
    "Redis": "In-memory cache and message broker crucial for high-scale backend throughput."
}

@router.get("")
async def get_skill_gaps(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]

    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile required to assess skill gaps.")

    candidate_skills = {s.lower() for s in profile.get("skills", [])}

    # Fetch top matches for user
    cursor = db.matches.find({"user_id": user_id}).sort("score", -1).limit(30)
    matches = await cursor.to_list(length=30)

    # Tally missing skills across matching jobs
    missing_counter = Counter()
    total_relevant_jobs = len(matches)

    for m in matches:
        for sk in m.get("missing_skills", []):
            norm = normalize_skill(sk)
            if norm.lower() not in candidate_skills:
                missing_counter[norm] += 1

    gap_items = []
    for skill_name, count in missing_counter.most_common(10):
        demand_pct = round((count / max(total_relevant_jobs, 1)) * 100)
        
        if demand_pct >= 50:
            importance = "Critical"
        elif demand_pct >= 25:
            importance = "High Impact"
        else:
            importance = "Recommended"

        reason = SKILL_IMPORTANCE_EXPLANATIONS.get(
            skill_name,
            f"Frequently requested in {count} job opportunities matching your target career domain."
        )

        gap_items.append({
            "skill": skill_name,
            "jobs_requiring": count,
            "demand_percentage": demand_pct,
            "importance": importance,
            "in_profile": False,
            "why_learn_this": reason
        })

    return {
        "candidate_skills_count": len(candidate_skills),
        "total_matches_analyzed": total_relevant_jobs,
        "skill_gaps": gap_items,
        "top_recommended_next": gap_items[0]["skill"] if gap_items else "Git"
    }
