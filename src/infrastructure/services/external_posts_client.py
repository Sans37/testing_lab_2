import os
from typing import Any, Dict

import httpx


class ExternalPostsClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "EXTERNAL_POSTS_BASE_URL",
            "https://jsonplaceholder.typicode.com",
        ).rstrip("/")
        self.timeout = float(os.getenv("EXTERNAL_POSTS_TIMEOUT", "5.0"))

    async def get_post(self, post_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/posts/{post_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        return {
            "id": int(data.get("id", post_id)),
            "user_id": int(data.get("userId", 0)),
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "source": self.base_url,
        }
