import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.logging import logger

class EmbeddingService:
    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version
        self.model_name = "scikit-learn-tfidf-semantic"
        # Shared vocabulary vectorizer trained on tech / career corpus
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self._is_fitted = False
        self._init_base_corpus()

    def _init_base_corpus(self):
        """Pre-fit on a representative career skills and job description corpus."""
        base_corpus = [
            "python machine learning data science pandas numpy scikit-learn tensorflow deep learning pytorch",
            "frontend react javascript typescript nextjs html css tailwind web development ui ux",
            "backend developer fastapi django nodejs express microservices rest api postgresql sql mongodb",
            "devops cloud aws docker kubernetes terraform ci cd linux automation bash git",
            "data engineer etl pipeline spark airflow hadoop bigquery sql data warehouse",
            "quality assurance qa automation testing selenium pytest jest cypress manual test",
            "cybersecurity infosec ethical hacking penetration testing network security soc",
            "product management agile scrum user stories roadmap kpis feature backlog",
            "sales marketing business analysis communication stakeholder management client presentation",
            "mobile development android ios flutter react native swift kotlin"
        ]
        self.vectorizer.fit(base_corpus)
        self._is_fitted = True

    def fit_corpus(self, texts: List[str]):
        """Expand vectorizer vocabulary if additional corpus is provided."""
        if texts:
            try:
                self.vectorizer.fit(texts)
                self._is_fitted = True
            except Exception as e:
                logger.warning(f"Failed to fit vectorizer corpus: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate normalized semantic embedding vector from text."""
        if not text:
            return [0.0] * 50
        if not self._is_fitted:
            self._init_base_corpus()
            
        vec = self.vectorizer.transform([text]).toarray()[0]
        # Return as standard float list
        return [float(x) for x in vec[:128]]  # store compact top-dimension vector

    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two embedding vectors (0.0 to 1.0)."""
        if not vec1 or not vec2:
            return 0.0
        
        # Ensure equal length
        min_len = min(len(vec1), len(vec2))
        if min_len == 0:
            return 0.0
            
        a = np.array(vec1[:min_len], dtype=np.float32)
        b = np.array(vec2[:min_len], dtype=np.float32)
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        sim = float(np.dot(a, b) / (norm_a * norm_b))
        # Bound between 0.0 and 1.0
        return max(0.0, min(1.0, sim))

    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """Convenience method to compute semantic similarity between two texts."""
        if not text1 or not text2:
            return 0.0
        try:
            vecs = self.vectorizer.transform([text1, text2]).toarray()
            sim = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
            return float(max(0.0, min(1.0, sim)))
        except Exception as e:
            logger.warning(f"Text similarity fallback: {e}")
            return 0.0

embedding_service = EmbeddingService()
