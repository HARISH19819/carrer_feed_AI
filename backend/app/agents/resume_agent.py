import io
import re
from typing import Dict, Any, List, Optional
import pymupdf  # PyMuPDF
import docx
from app.agents.base_agent import BaseAgent, AgentRunResult
from app.utils.text import (
    clean_text, extract_email, extract_phone, extract_degrees, extract_years_of_experience
)
from app.utils.skills import (
    normalize_skill, normalize_skill_list, get_all_known_skills, DOMAIN_KEYWORDS, DOMAIN_TAXONOMY
)
from app.services.llm_provider import llm_provider
from app.core.logging import logger

class ResumeProfileAgent(BaseAgent):
    agent_name = "Profile Agent"

    def extract_text_from_file(self, filename: str, content: bytes) -> str:
        """Extract plain text from PDF, DOCX, or TXT content."""
        ext = filename.lower().split(".")[-1]
        text = ""
        
        if ext == "pdf":
            try:
                doc = pymupdf.open(stream=content, filetype="pdf")
                pages_text = [page.get_text() for page in doc]
                text = "\n".join(pages_text)
            except Exception as e:
                logger.error(f"Failed to read PDF: {e}")
                raise ValueError("Could not read PDF document. The file may be password protected or corrupted.")
        elif ext in ["docx", "doc"]:
            try:
                file_stream = io.BytesIO(content)
                doc = docx.Document(file_stream)
                text = "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                logger.error(f"Failed to read DOCX: {e}")
                raise ValueError("Could not read DOCX document. Please verify the file format.")
        elif ext == "txt":
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1", errors="ignore")
        else:
            raise ValueError(f"Unsupported resume extension: .{ext}. Allowed: PDF, DOCX, TXT")

        cleaned = clean_text(text)
        if len(cleaned) < 30:
            raise ValueError("The uploaded document contains insufficient readable text.")
        return cleaned

    def extract_skills(self, text: str) -> List[str]:
        """Dictionary and regex-based skill extraction with canonical normalization."""
        known_skills = get_all_known_skills()
        found_skills = set()
        text_lower = text.lower()
        
        # Look for skills with word boundary
        for skill in known_skills:
            pattern = r'(?:\b|(?<=[\s,./\-_]))' + re.escape(skill) + r'(?:\b|(?=[\s,./\-_]))'
            if re.search(pattern, text_lower):
                found_skills.add(normalize_skill(skill))
                
        return normalize_skill_list(list(found_skills))

    def infer_domains(self, skills: List[str], text: str) -> List[str]:
        """Infer career domains based on extracted skills and context."""
        text_lower = text.lower()
        skills_lower = [s.lower() for s in skills]
        domain_scores: Dict[str, int] = {d: 0 for d in DOMAIN_TAXONOMY}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in skills_lower:
                    domain_scores[domain] += 3
                if kw in text_lower:
                    domain_scores[domain] += 1
                    
        # Filter domains with score > 0 and sort descending
        sorted_domains = sorted(
            [d for d, score in domain_scores.items() if score > 0],
            key=lambda d: domain_scores[d],
            reverse=True
        )
        
        return sorted_domains[:3] if sorted_domains else ["Software Development"]

    def infer_recommended_roles(self, domains: List[str], skills: List[str]) -> List[str]:
        """Generate targeted recommended job roles based on candidate profile."""
        roles: List[str] = []
        skills_set = {s.lower() for s in skills}
        
        if "Machine Learning" in domains or "Artificial Intelligence" in domains:
            roles.extend(["Machine Learning Engineer", "AI Engineer", "ML Intern", "Data Scientist"])
        if "Data Science" in domains or "Data Engineering" in domains:
            roles.extend(["Data Scientist", "Data Analyst", "Data Engineer Intern"])
        if "Frontend Development" in domains:
            roles.extend(["Frontend Developer", "React Developer", "UI Engineer", "Web Developer"])
        if "Backend Development" in domains:
            roles.extend(["Backend Developer", "Python Developer", "Software Engineer", "API Engineer"])
        if "Full Stack Development" in domains:
            roles.extend(["Full Stack Engineer", "Software Development Engineer", "Web Developer"])
        if "DevOps" in domains or "Cloud Computing" in domains:
            roles.extend(["DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer (SRE)"])
        if "Software Testing / QA" in domains:
            roles.extend(["QA Automation Engineer", "Software Test Engineer", "SDET"])
            
        if not roles:
            roles = ["Software Engineer", "Junior Developer", "Tech Intern"]
            
        # Deduplicate while preserving order
        unique_roles = []
        for r in roles:
            if r not in unique_roles:
                unique_roles.append(r)
        return unique_roles[:6]

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract degree, field, graduation year from resume text."""
        degrees = extract_degrees(text)
        primary_degree = degrees[0] if degrees else "B.Tech"
        
        # Check graduation year (e.g. 2023 - 2028)
        grad_year = None
        year_match = re.search(r'\b(201[89]|202[0-9])\b', text)
        if year_match:
            grad_year = int(year_match.group(1))
            
        # Infer field of study
        field = "Computer Science"
        text_lower = text.lower()
        if "artificial intelligence" in text_lower or "ai and data science" in text_lower:
            field = "Artificial Intelligence and Data Science"
        elif "information technology" in text_lower:
            field = "Information Technology"
        elif "data science" in text_lower:
            field = "Data Science"
        elif "electronics" in text_lower:
            field = "Electronics and Communication"
            
        return [{
            "degree": primary_degree,
            "field": field,
            "institution": "University / Institute",
            "graduation_year": grad_year or 2026
        }]

    def extract_name(self, text: str) -> Optional[str]:
        """Heuristic extraction of candidate's name from first non-empty lines."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines[:5]:
            # Avoid headers or contact lines
            if any(k in line.lower() for k in ["resume", "curriculum", "cv", "email", "phone", "http", "@"]):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(w.isalpha() for w in words):
                return line.title()
        return None

    def calculate_profile_strength(self, profile: Dict[str, Any]) -> int:
        """Calculate deterministic completeness score 0 - 100."""
        score = 0
        if profile.get("name"):
            score += 10
        if profile.get("email"):
            score += 10
        if profile.get("phone"):
            score += 5
        if profile.get("skills") and len(profile["skills"]) >= 3:
            score += 25
        elif profile.get("skills"):
            score += 15
        if profile.get("education"):
            score += 20
        if profile.get("domains"):
            score += 15
        if profile.get("recommended_roles"):
            score += 15
        return min(100, score)

    async def parse_resume_to_profile(self, filename: str, content: bytes) -> Dict[str, Any]:
        """End-to-end parse resume to structured candidate profile."""
        raw_text = self.extract_text_from_file(filename, content)
        
        name = self.extract_name(raw_text)
        email = extract_email(raw_text)
        phone = extract_phone(raw_text)
        education = self.extract_education(raw_text)
        
        min_y, max_y = extract_years_of_experience(raw_text)
        years_exp = min_y or 0.0
        exp_level = "fresher" if years_exp <= 1.0 else ("junior" if years_exp <= 3.0 else "mid_level")
        
        skills = self.extract_skills(raw_text)
        domains = self.infer_domains(skills, raw_text)
        roles = self.infer_recommended_roles(domains, skills)
        
        profile_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "education": education,
            "experience_level": exp_level,
            "years_of_experience": years_exp,
            "skills": skills,
            "domains": domains,
            "recommended_roles": roles,
            "preferred_locations": ["Remote"],
            "preferred_job_types": ["internship", "full_time"],
            "remote_preference": "any",
            "minimum_match_score": 60,
            "projects": [],
            "certifications": [],
            "work_experiences": []
        }
        
        strength = self.calculate_profile_strength(profile_data)
        profile_data["completeness_score"] = strength
        return profile_data

    async def run(self, filename: str, content: bytes) -> AgentRunResult:
        result = AgentRunResult(self.agent_name)
        try:
            profile = await self.parse_resume_to_profile(filename, content)
            result.records_processed = 1
            result.details = {"profile": profile}
            result.finish("completed")
        except Exception as e:
            result.records_failed = 1
            result.error_summary = str(e)
            result.finish("failed")
        return result

resume_profile_agent = ResumeProfileAgent()
