import re
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent, AgentRunResult
from app.utils.skills import (
    DOMAIN_TAXONOMY, DOMAIN_KEYWORDS, normalize_skill_list, normalize_skill, get_all_known_skills
)
from app.services.llm_provider import llm_provider
from app.database.mongo import get_database
from app.core.logging import logger

class JobClassificationAgent(BaseAgent):
    agent_name = "Classifier Agent"

    def classify_domain_deterministic(self, title: str, description: str, skills: List[str]) -> Dict[str, Any]:
        """Fast rule & keyword domain scoring."""
        text = f"{title} {title} {description}".lower()
        skills_lower = [s.lower() for s in skills]
        
        domain_scores: Dict[str, int] = {d: 0 for d in DOMAIN_TAXONOMY}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                # Skill match gives high weight
                if kw in skills_lower:
                    domain_scores[domain] += 5
                # Title match gives highest weight
                if kw in title.lower():
                    domain_scores[domain] += 6
                # Description mention gives base weight
                if kw in text:
                    domain_scores[domain] += 1
                    
        # Sort domains
        sorted_domains = sorted(
            [d for d, sc in domain_scores.items() if sc > 0],
            key=lambda d: domain_scores[d],
            reverse=True
        )
        
        if sorted_domains:
            primary = sorted_domains[0]
            secondaries = sorted_domains[1:3]
            top_score = domain_scores[primary]
            confidence = min(0.95, 0.65 + (top_score * 0.05))
            return {
                "domain": primary,
                "secondary_domains": secondaries,
                "confidence": round(confidence, 2),
                "classification_method": "deterministic_rule"
            }
        
        return {
            "domain": "Software Development",
            "secondary_domains": [],
            "confidence": 0.50,
            "classification_method": "default_fallback"
        }

    def extract_skills_from_text(self, text: str) -> List[str]:
        known = get_all_known_skills()
        found = set()
        text_lower = text.lower()
        for s in known:
            pattern = r'(?:\b|(?<=[\s,./\-_]))' + re.escape(s) + r'(?:\b|(?=[\s,./\-_]))'
            if re.search(pattern, text_lower):
                found.add(normalize_skill(s))
        return normalize_skill_list(list(found))

    async def classify_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        title = job.get("title", "")
        desc = job.get("description", "")
        skills = job.get("skills", [])
        
        # If skills list is empty, extract from description
        if not skills and desc:
            skills = self.extract_skills_from_text(f"{title} {desc}")
            
        classification = self.classify_domain_deterministic(title, desc, skills)
        
        # If confidence is low and description is rich, try LLM fallback
        if classification["confidence"] < 0.60:
            llm_res = await llm_provider.classify_job(title, desc, skills)
            if llm_res.get("domain") and llm_res["domain"] in DOMAIN_TAXONOMY:
                classification["domain"] = llm_res["domain"]
                classification["secondary_domains"] = llm_res.get("secondary_domains", [])
                classification["confidence"] = llm_res.get("confidence", 0.85)
                classification["classification_method"] = "hybrid_llm"
                
        # Required vs preferred skills split
        required = skills[:4] if len(skills) > 4 else skills
        preferred = skills[4:] if len(skills) > 4 else []
        
        return {
            "domain": classification["domain"],
            "secondary_domains": classification["secondary_domains"],
            "confidence": classification["confidence"],
            "classification_method": classification["classification_method"],
            "skills": skills,
            "required_skills": required,
            "preferred_skills": preferred
        }

    async def run(self, limit: int = 50) -> AgentRunResult:
        result = AgentRunResult(self.agent_name)
        db = get_database()
        if db is None:
            result.error_summary = "Database not connected"
            result.finish("failed")
            return result

        try:
            # Find pending or unclassified jobs
            cursor = db.jobs.find(
                {"$or": [{"classification_method": "deterministic"}, {"confidence": {"$exists": False}}]}
            ).limit(limit)
            jobs = await cursor.to_list(length=limit)
            
            classified_count = 0
            for j in jobs:
                updates = await self.classify_job(j)
                await db.jobs.update_one(
                    {"_id": j["_id"]},
                    {"$set": updates}
                )
                classified_count += 1
                
            result.records_processed = classified_count
            result.details = {"classified_count": classified_count}
            result.finish("completed")
        except Exception as e:
            result.records_failed = 1
            result.error_summary = str(e)
            result.finish("failed")
            
        return result

job_classifier_agent = JobClassificationAgent()
