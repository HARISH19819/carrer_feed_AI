from typing import Dict
from app.sources.base_source import BaseSourceAdapter
from app.sources.adapters.remotive_adapter import RemotiveAdapter
from app.sources.adapters.jobicy_adapter import JobicyAdapter
from app.sources.adapters.arbeitnow_adapter import ArbeitnowAdapter
from app.sources.adapters.themuse_adapter import TheMuseAdapter
from app.sources.adapters.remoteok_adapter import RemoteOKAdapter
from app.sources.adapters.weworkremotely_adapter import WeWorkRemotelyAdapter
from app.sources.adapters.internshala_adapter import InternshalaAdapter
from app.sources.adapters.linkedin_adapter import LinkedInAdapter

AVAILABLE_ADAPTERS: Dict[str, BaseSourceAdapter] = {
    "remotive_api": RemotiveAdapter(),
    "jobicy_api": JobicyAdapter(),
    "arbeitnow_api": ArbeitnowAdapter(),
    "themuse_api": TheMuseAdapter(),
    "remoteok_api": RemoteOKAdapter(),
    "wwr_rss": WeWorkRemotelyAdapter(),
    "internshala_feed": InternshalaAdapter(),
    "linkedin_feed": LinkedInAdapter(),
}

def get_adapter(key: str) -> BaseSourceAdapter:
    return AVAILABLE_ADAPTERS.get(key)
