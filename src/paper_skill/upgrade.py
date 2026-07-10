"""Source upgrading (§15): one free OpenAlex call climbs rung 4 -> rung 1."""
import re
import requests
from .paper2pack import UA, _no_apis


def find_arxiv_sibling(title: str, get=requests.get) -> str | None:
    if _no_apis():
        return None
    try:
        data = get("https://api.openalex.org/works", timeout=20, headers=UA,
                   params={"search": title, "per_page": 1,
                           "select": "ids"}).json()
        ids = (data.get("results") or [{}])[0].get("ids") or {}
        m = re.search(r"(\d{4}\.\d{4,5})", ids.get("arxiv") or "")
        return m.group(1) if m else None
    except Exception:
        return None
