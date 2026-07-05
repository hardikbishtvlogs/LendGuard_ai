import logging
import httpx
from ..core.config import get_settings

log = logging.getLogger(__name__)


async def push_prediction(row: dict):
    url = get_settings().powerbi_push_url
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.post(url, json=[row])
            response.raise_for_status()
    except Exception:
        log.exception("Power BI push failed; prediction remains safely persisted")

