# JobFusion AI — System Architecture

## Overview
JobFusion AI is a unified career intelligence and personalized job recommendation platform. Rather than serving as a walled-garden job portal, it functions as an autonomous aggregation, domain classification, and personalized recommendation layer over permitted external job sources.

```mermaid
graph TD
    User([Job Seeker]) -->|Upload Resume| Frontend[React + Vite Frontend]
    Frontend -->|REST API + JWT| Backend[FastAPI Modular Monolith]
    Backend --> Orchestrator[Pipeline Orchestrator]
    
    subgraph MultiAgentSystem [Autonomous Multi-Agent System]
        Orchestrator --> Agent1[Agent 1: Resume / Profile Agent]
        Orchestrator --> Agent2[Agent 2: Job Discovery Agent]
        Agent2 --> Adapter1[Remotive API Adapter]
        Agent2 --> Adapter2[Jobicy API Adapter]
        Agent2 --> Adapter3[Curated Dataset Adapter]
        
        Adapter1 & Adapter2 & Adapter3 --> Normalizer[Job Normalizer Service]
        Normalizer --> Deduplicator[Multi-Stage Deduplication]
        Deduplicator --> Agent3[Agent 3: Classification Agent]
        Agent3 --> Embedder[Embedding Service TF-IDF / SBERT]
        
        Agent1 --> Profile[(Candidate Profile)]
        Embedder --> NormalizedJobs[(Normalized Jobs)]
        
        Profile & NormalizedJobs --> Agent4[Agent 4: Personalized Matching Engine]
    end

    Agent4 --> RankedMatches[(Ranked Recommendations)]
    RankedMatches --> Frontend
    Frontend -->|Apply on Source| ExternalSite([Original Employer Posting])
```

## Critical Engineering Principle
- **AI/ML** handles semantic understanding, resume interpretation, skill extraction, domain inference, semantic candidate-job similarity, and recommendation explanation.
- **Deterministic Software** handles authentication, authorization, database operations, validation, deduplication, filtering, sorting, pagination, application tracking, scoring formulas, and security.

## Core Multi-Agent Coordination
1. **Resume / Profile Agent**: Parses PDFs/DOCXs using PyMuPDF and python-docx, extracts normalized technical skills, infers primary and secondary domains, and derives recommended roles.
2. **Job Discovery Agent**: Queries permitted source adapters, standardizes data into the canonical schema, and logs discovery telemetry.
3. **Job Classification Agent**: Employs a hybrid scoring algorithm across 22 technical and business domains, classifies experience level (fresher to senior), location type, and employment type.
4. **Personalized Matching Agent**: Evaluates active opportunities against candidate profiles using a 7-dimension scoring engine and semantic cosine similarity.
5. **Pipeline Orchestrator**: Executes the entire sequence idempotently, recording pipeline runs and agent telemetry for admin observability.
