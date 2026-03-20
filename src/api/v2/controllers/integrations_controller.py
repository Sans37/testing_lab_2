from fastapi import APIRouter, HTTPException, status

from src.api.v2.dtos.response_dtos import ExternalPostResponse
from src.infrastructure.services.external_posts_client import ExternalPostsClient

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/posts/{post_id}", response_model=ExternalPostResponse)
async def get_external_post(post_id: int):
    """Integration with external Posts service (mock or real)."""
    client = ExternalPostsClient()
    try:
        post = await client.get_post(post_id)
        return ExternalPostResponse(**post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External service error: {str(e)}",
        )
