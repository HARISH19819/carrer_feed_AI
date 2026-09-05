# Zero-Cost Free-Tier Deployment Guide

JobFusion AI is architected from the ground up to be deployed on 100% free-tier student and open-source infrastructure without requiring paid vector databases, Redis clusters, or expensive LLM token subscriptions.

## Target Free-Tier Topology

```
+---------------------------+        +--------------------------+
|  Frontend (Vite / React)  |        |  Backend (FastAPI Web)   |
|  Hosted on:               |        |  Hosted on:              |
|  - Vercel (Free)          |  --->  |  - Render (Free Tier)    |
|  - Cloudflare Pages (Free)| (REST) |  - Fly.io / Railway      |
|  - Netlify (Free)         |        |  - Docker Container      |
+---------------------------+        +--------------------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |  Database (MongoDB)      |
                                     |  Hosted on:              |
                                     |  - MongoDB Atlas (M0)    |
                                     |  - 512 MB Free Cluster   |
                                     +--------------------------+
```

## Scheduled Automation
- **GitHub Actions**: Background cron workflow (`.github/workflows/job_pipeline.yml`) executes twice daily to run ingestion, deduplication, classification, and matching without needing a paid background worker.

## Deployment Instructions

### 1. Database (MongoDB Atlas)
1. Create a free M0 cluster on [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Create a database user with read/write privileges.
3. Whitelist `0.0.0.0/0` (allow all IP access for hosting platforms).
4. Copy the connection string: `mongodb+srv://<user>:<password>@cluster.mongodb.net/jobfusion?retryWrites=true&w=majority`.

### 2. Backend (Render / Railway / Fly.io)
1. Connect your GitHub repository to Render as a **Web Service**.
2. Set Root Directory to `backend/`.
3. Set Environment to `Python 3`.
4. Set Build Command: `pip install -r requirements.txt && pip install pydantic-settings`.
5. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add Environment Variables:
   - `APP_ENV`: `production`
   - `MONGODB_URI`: `<Your MongoDB Atlas URI>`
   - `DATABASE_NAME`: `jobfusion`
   - `SECRET_KEY`: `<Generate random 32-character string>`
   - `JWT_SECRET`: `<Generate random 32-character string>`
   - `FRONTEND_URL`: `<Your Vercel/Netlify URL>`
   - `LLM_PROVIDER`: `local` (or `gemini` if API key provided)

### 3. Frontend (Vercel / Cloudflare Pages / Netlify)
1. Connect your GitHub repository.
2. Set Root Directory to `frontend/`.
3. Build Command: `npm run build`.
4. Output Directory: `dist`.
5. Set Environment Variable:
   - In `src/services/api.js`, set `API_BASE` to your deployed backend URL.
