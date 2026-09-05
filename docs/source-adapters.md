# Source Adapter Architecture & Permitted Feeds

## Architecture Pattern
JobFusion AI follows an extensible **Source Adapter Pattern**. The core ingestion system does not hardcode website structures or API quirks. Every external integration implements `BaseSourceAdapter`:

```python
class BaseSourceAdapter(ABC):
    source_name: str
    adapter_key: str
    source_type: str  # api, rss, dataset
    base_url: str

    @abstractmethod
    async def fetch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass
```

## Permitted & Compliant Ingestion Sources
JobFusion AI strictly abides by robots.txt, terms of service, and public access permissions. It does **not** bypass CAPTCHAs, paywalls, or login walls.

1. **Remotive Public API (`RemotiveAdapter`)**:
   - URL: `https://remotive.com/api/remote-jobs`
   - Type: Compliant REST API.
   - Target: Software development, data science, and remote technical roles.
2. **Jobicy Remote API (`JobicyAdapter`)**:
   - URL: `https://jobicy.com/api/v2/remote-jobs`
   - Type: Public JSON feed for global opportunities.
3. **Curated Tech Dataset (`DatasetAdapter`)**:
   - Local verified benchmark dataset for instant testing, deterministic test runs, and offline development.

## Canonical Ingestion Schema
All source adapters normalize their records into the identical internal schema:
```json
{
  "title": "Machine Learning Engineer Intern",
  "company": "NeuralCraft AI Labs",
  "location": "Bangalore, India",
  "location_type": "hybrid",
  "employment_type": "internship",
  "experience_required": "0-1 years",
  "salary": "$25 - $35 / hr",
  "description": "...",
  "skills": ["Python", "TensorFlow", "Scikit-learn"],
  "source": "Remotive Public API",
  "source_url": "https://...",
  "application_url": "https://...",
  "posted_at": "2026-09-04T10:00:00Z",
  "status": "active"
}
```
