from fastapi import FastAPI

app = FastAPI(title="Mock External Posts Service")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mock-external-posts"}


@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    return {
        "id": post_id,
        "userId": 1,
        "title": f"Mock post {post_id}",
        "body": "This is a mock post body for testing.",
    }
