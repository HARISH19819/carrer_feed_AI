import re
from typing import List, Optional, Tuple, Any

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,12}')

DEGREE_PATTERNS = [
    (r'\b(b\.?tech|bachelor of technology|b\.?e\.?|bachelor of engineering)\b', 'B.Tech'),
    (r'\b(m\.?tech|master of technology|m\.?e\.?|master of engineering)\b', 'M.Tech'),
    (r'\b(b\.?sc|bachelor of science)\b', 'B.Sc'),
    (r'\b(m\.?sc|master of science)\b', 'M.Sc'),
    (r'\b(bca|bachelor of computer applications)\b', 'BCA'),
    (r'\b(mca|master of computer applications)\b', 'MCA'),
    (r'\b(ph\.?d|doctor of philosophy)\b', 'Ph.D'),
    (r'\b(bba|mba|bachelor of business|master of business)\b', 'MBA')
]

EXPERIENCE_YEARS_PATTERNS = [
    re.compile(r'(\d+)(?:\s*(?:-|to)\s*(\d+))?\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', re.IGNORECASE),
    re.compile(r'experience\s*:\s*(\d+)(?:\s*(?:-|to)\s*(\d+))?\s*(?:\+)?\s*(?:years?|yrs?)', re.IGNORECASE),
    re.compile(r'(\d+)\+\s*(?:years?|yrs?)', re.IGNORECASE)
]

def clean_text(text: Any) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if text is None:
        return ""
    if isinstance(text, list):
        text = " ".join(str(x) for x in text if x)
    elif not isinstance(text, str):
        text = str(text)
    # Replace unicode spaces/newlines
    text = re.sub(r'[\r\t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ ]{2,}', ' ', text)
    return text.strip()

def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    match = PHONE_REGEX.search(text)
    return match.group(0).strip() if match else None

def extract_degrees(text: str) -> List[str]:
    found = []
    text_lower = text.lower()
    for pattern, name in DEGREE_PATTERNS:
        if re.search(pattern, text_lower):
            if name not in found:
                found.append(name)
    return found

def extract_years_of_experience(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Return (min_years, max_years)."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["fresher", "entry level", "college graduate", "0 years", "no experience"]):
        return (0.0, 1.0)
        
    for pat in EXPERIENCE_YEARS_PATTERNS:
        match = pat.search(text)
        if match:
            g = match.groups()
            min_y = float(g[0]) if g[0] else 0.0
            max_y = float(g[1]) if len(g) > 1 and g[1] else min_y
            return (min_y, max_y)
            
    return (None, None)
