from typing import Dict, Any, List, Tuple
from app.utils.skills import normalize_skill, normalize_skill_list
from app.services.embedding_service import embedding_service
from app.services.llm_provider import llm_provider

class ScoringWeights:
    SKILL_WEIGHT: float = 0.30
    ROLE_WEIGHT: float = 0.20
    DOMAIN_WEIGHT: float = 0.15
    EXPERIENCE_WEIGHT: float = 0.15
    EDUCATION_WEIGHT: float = 0.10
    LOCATION_WEIGHT: float = 0.05
    PREFERENCE_WEIGHT: float = 0.05

class ScoringEngine:
    def __init__(self, weights: ScoringWeights = ScoringWeights()):
        self.weights = weights

    def calculate_skill_alignment(
        self, candidate_skills: List[str], job_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates skill match percentage, returning (score_0_to_1, strong_matches, missing_skills).
        """
        c_set = {normalize_skill(s).lower(): normalize_skill(s) for s in candidate_skills if s}
        j_set = {normalize_skill(s).lower(): normalize_skill(s) for s in job_skills if s}
        
        if not j_set:
            # If job didn't specify skills, provide neutral baseline
            return (0.75, list(c_set.values())[:3], [])
            
        matching_keys = set(c_set.keys()).intersection(set(j_set.keys()))
        missing_keys = set(j_set.keys()) - set(c_set.keys())
        
        # Jaccard / Overlap ratio against job required skills
        skill_score = len(matching_keys) / len(j_set)
        
        strong_matches = [j_set[k] for k in matching_keys]
        missing_skills = [j_set[k] for k in missing_keys]
        
        return (skill_score, strong_matches, missing_skills)

    def calculate_role_alignment(self, candidate_roles: List[str], job_title: str) -> float:
        if not candidate_roles or not job_title:
            return 0.5
        j_lower = job_title.lower()
        for r in candidate_roles:
            r_lower = r.lower()
            if r_lower in j_lower or j_lower in r_lower:
                return 1.0
            # Token overlap check
            c_words = set(r_lower.split())
            j_words = set(j_lower.split())
            if c_words.intersection(j_words):
                return 0.8
        return 0.3

    def calculate_domain_alignment(
        self, candidate_domains: List[str], job_domain: str, job_secondary_domains: List[str]
    ) -> float:
        if not candidate_domains or not job_domain:
            return 0.5
        c_domains_lower = [d.lower() for d in candidate_domains]
        if job_domain.lower() in c_domains_lower:
            return 1.0
        for s in job_secondary_domains:
            if s.lower() in c_domains_lower:
                return 0.8
        return 0.2

    def calculate_experience_alignment(
        self, candidate_exp_level: str, candidate_years: float, job_exp_level: str, job_min_y: float, job_max_y: float
    ) -> float:
        c_level = (candidate_exp_level or "fresher").lower()
        j_level = (job_exp_level or "fresher").lower()
        
        # Fresher applying to fresher / entry-level
        if c_level in ["fresher", "entry_level"] and j_level in ["fresher", "entry_level"]:
            return 1.0
        if c_level == j_level:
            return 1.0
            
        # Numerical years check
        if candidate_years >= job_min_y and candidate_years <= (job_max_y + 1.0):
            return 1.0
        elif candidate_years < job_min_y:
            gap = job_min_y - candidate_years
            return max(0.1, 1.0 - (gap * 0.25))
        else:
            # Overqualified
            return 0.75

    def calculate_education_alignment(self, candidate_education: List[Dict[str, Any]], job_desc: str) -> float:
        if not candidate_education:
            return 0.7  # neutral
        deg_names = [e.get("degree", "").lower() for e in candidate_education]
        if any(d in deg_names for d in ["b.tech", "b.e", "m.tech", "mca", "bca", "b.sc", "m.sc"]):
            return 1.0
        return 0.8

    def calculate_location_alignment(
        self, preferred_locations: List[str], remote_pref: str, job_location: str, job_loc_type: str
    ) -> float:
        if job_loc_type == "remote" or remote_pref == "remote":
            return 1.0
        if remote_pref == "any":
            return 0.9
        if not preferred_locations:
            return 0.8
            
        j_loc_lower = job_location.lower()
        for loc in preferred_locations:
            if loc.lower() in j_loc_lower:
                return 1.0
        return 0.4

    def calculate_preference_alignment(
        self, preferred_job_types: List[str], job_employment_type: str
    ) -> float:
        if not preferred_job_types:
            return 0.8
        types_lower = [t.lower() for t in preferred_job_types]
        if job_employment_type.lower() in types_lower:
            return 1.0
        return 0.4

    def score_match(
        self, candidate: Dict[str, Any], job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate full deterministic match score and generate transparent explanation.
        """
        # 1. Skill Score
        c_skills = candidate.get("skills", [])
        j_skills = job.get("skills", [])
        skill_score, strong_matches, missing_skills = self.calculate_skill_alignment(c_skills, j_skills)

        # 2. Role Score
        c_roles = candidate.get("recommended_roles", [])
        j_title = job.get("title", "")
        role_score = self.calculate_role_alignment(c_roles, j_title)

        # 3. Domain Score
        c_domains = candidate.get("domains", [])
        j_domain = job.get("domain", "")
        j_sec_domains = job.get("secondary_domains", [])
        domain_score = self.calculate_domain_alignment(c_domains, j_domain, j_sec_domains)

        # 4. Experience Score
        c_exp_level = candidate.get("experience_level", "fresher")
        c_years = float(candidate.get("years_of_experience", 0.0))
        j_exp_level = job.get("experience_level", "fresher")
        j_min_y = float(job.get("min_experience_years", 0.0))
        j_max_y = float(job.get("max_experience_years", 1.0))
        exp_score = self.calculate_experience_alignment(c_exp_level, c_years, j_exp_level, j_min_y, j_max_y)

        # 5. Education Score
        c_edu = candidate.get("education", [])
        j_desc = job.get("description", "")
        edu_score = self.calculate_education_alignment(c_edu, j_desc)

        # 6. Location Score
        c_locs = candidate.get("preferred_locations", [])
        c_remote_pref = candidate.get("remote_preference", "any")
        j_loc = job.get("location", "Remote")
        j_loc_type = job.get("location_type", "remote")
        loc_score = self.calculate_location_alignment(c_locs, c_remote_pref, j_loc, j_loc_type)

        # 7. Preference Score
        c_types = candidate.get("preferred_job_types", ["internship", "full_time"])
        j_emp_type = job.get("employment_type", "full_time")
        pref_score = self.calculate_preference_alignment(c_types, j_emp_type)

        # Semantic Similarity
        c_text = f"{' '.join(c_skills)} {' '.join(c_domains)} {' '.join(c_roles)}"
        j_text = f"{j_title} {' '.join(j_skills)} {j_domain} {j_desc[:300]}"
        semantic_sim = embedding_service.compute_text_similarity(c_text, j_text)

        # Structured Weighted Score (0.0 to 1.0)
        structured_score = (
            self.weights.SKILL_WEIGHT * skill_score +
            self.weights.ROLE_WEIGHT * role_score +
            self.weights.DOMAIN_WEIGHT * domain_score +
            self.weights.EXPERIENCE_WEIGHT * exp_score +
            self.weights.EDUCATION_WEIGHT * edu_score +
            self.weights.LOCATION_WEIGHT * loc_score +
            self.weights.PREFERENCE_WEIGHT * pref_score
        )

        # Combined Final Score: 70% structured + 30% semantic
        final_normalized_score = int(round((0.70 * structured_score + 0.30 * max(semantic_sim, 0.2)) * 100))
        # Ensure score stays bounded [10, 99]
        final_score = max(10, min(99, final_normalized_score))

        # Assign tier
        if final_score >= 90:
            tier = "Excellent Match"
        elif final_score >= 80:
            tier = "Strong Match"
        elif final_score >= 70:
            tier = "Good Match"
        elif final_score >= 60:
            tier = "Moderate Match"
        else:
            tier = "Low Match"

        # Generate transparent explanation
        matched_str = ", ".join(strong_matches[:4]) if strong_matches else "relevant profile background"
        missing_str = ", ".join(missing_skills[:3]) if missing_skills else "none"
        
        why_text = (
            f"Your profile matches the {j_domain or 'technical'} domain requirements and role expectations. "
            f"Key matching skills: {matched_str}. "
        )
        if missing_skills:
            why_text += f"Key skills to acquire: {missing_str}."
        else:
            why_text += "No critical missing skills were identified."

        return {
            "score": final_score,
            "match_tier": tier,
            "strong_matches": strong_matches,
            "missing_skills": missing_skills,
            "why_matched": why_text,
            "breakdown": {
                "skill_score": round(skill_score * 100, 1),
                "role_score": round(role_score * 100, 1),
                "domain_score": round(domain_score * 100, 1),
                "experience_score": round(exp_score * 100, 1),
                "education_score": round(edu_score * 100, 1),
                "location_score": round(loc_score * 100, 1),
                "preference_score": round(pref_score * 100, 1),
                "semantic_similarity": round(semantic_sim * 100, 1)
            }
        }

scoring_engine = ScoringEngine()
