import pytest
import httpx
from app.main import app
from app.database.mongo import connect_to_mongo, close_mongo_connection

@pytest.mark.asyncio
async def test_complete_e2e_api_flow():
    await connect_to_mongo()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver/api") as client:
            # 1. Health check
            health = await client.get("http://testserver/health")
            assert health.status_code == 200
            assert health.json()["status"] == "ok"

            # 2. Candidate Login
            login_res = await client.post("/auth/login", json={
                "email": "candidate@jobfusion.ai",
                "password": "Candidate123!"
            })
            assert login_res.status_code == 200
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 3. Get Profile
            profile_res = await client.get("/profile", headers=headers)
            assert profile_res.status_code == 200
            profile = profile_res.json()
            assert profile["name"] is not None
            assert len(profile["skills"]) >= 1

            # 4. Get Matches
            matches_res = await client.get("/matches", headers=headers)
            assert matches_res.status_code == 200
            matches = matches_res.json()["items"]
            assert len(matches) > 0
            assert len(matches[0]["strong_matches"]) > 0

            # 5. Save Job
            first_job_id = matches[0]["job_id"]
            save_res = await client.post(f"/saved/{first_job_id}", headers=headers)
            assert save_res.status_code in [200, 201]

            saved_list = await client.get("/saved", headers=headers)
            assert any(s["job_id"] == first_job_id for s in saved_list.json()["items"])

            # 6. Track Application
            app_res = await client.post(f"/applications/{first_job_id}", headers=headers, json={
                "job_id": first_job_id,
                "status": "Applied"
            })
            assert app_res.status_code in [200, 201]
            assert app_res.json()["status"] == "Applied"

            # 7. Update Application stage to Interview
            app_id = app_res.json()["id"]
            patch_res = await client.patch(f"/applications/{app_id}", headers=headers, json={
                "status": "Interview"
            })
            assert patch_res.status_code == 200
            assert patch_res.json()["status"] == "Interview"

            # 8. Skill Gaps Intelligence
            gaps_res = await client.get("/skill-gaps", headers=headers)
            assert gaps_res.status_code == 200
            gaps_data = gaps_res.json()
            assert "skill_gaps" in gaps_data
            assert gaps_data["total_matches_analyzed"] > 0

            # 9. Pipeline Status & 4 Agent Cards
            pipe_status = await client.get("/pipeline/status", headers=headers)
            assert pipe_status.status_code == 200
            cards = pipe_status.json()["agent_cards"]
            assert len(cards) == 4
            agent_ids = [c["agent_id"] for c in cards]
            assert "scanner" in agent_ids
            assert "classifier" in agent_ids
            assert "profile" in agent_ids
            assert "matcher" in agent_ids

            # 10. Admin Verification
            admin_login = await client.post("/auth/login", json={
                "email": "admin@jobfusion.ai",
                "password": "AdminPassword123!"
            })
            assert admin_login.status_code == 200
            admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

            admin_stats = await client.get("/admin/stats", headers=admin_headers)
            assert admin_stats.status_code == 200
            stats = admin_stats.json()
            assert stats["total_jobs"] > 0
            assert stats["active_jobs"] > 0

            admin_sources = await client.get("/admin/sources", headers=admin_headers)
            assert admin_sources.status_code == 200
            assert len(admin_sources.json()) >= 3
    finally:
        await close_mongo_connection()
