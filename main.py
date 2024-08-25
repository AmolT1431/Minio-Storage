from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
import httpx

app = FastAPI()
@app.get("/")
async def get_system_name():
    return {"massage: working"}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    # The URL of the MinIO service
    minio_url = f"http://10.220.93.64:45067/{full_path}"

    # Create a new HTTPX client instance
    async with httpx.AsyncClient() as client:
        # Forward the request to MinIO
        minio_response = await client.request(
            method=request.method,
            url=minio_url,
            headers=request.headers.raw,
            params=request.query_params,
            content=await request.body(),
            timeout=30.0
        )

        # Prepare the response to send back to the client
        response_headers = dict(minio_response.headers)
        content = minio_response.content

        return StreamingResponse(
            content,
            status_code=minio_response.status_code,
            headers=response_headers
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
