from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from minio import Minio
from minio.error import S3Error
from io import BytesIO

app = FastAPI()

# Initialize MinIO client
minio_client = Minio(
    "216.24.57.4:9000",
    access_key="atomictos",
    secret_key="amolt1431",
    secure=False
)

bucket_name = "test"

@app.get("/")
async def read_root():
    """
    Default route to show a welcome message.
    """
    return {"message": "Welcome to the FastAPI MinIO service!"}

@app.get("/connection-status")
async def check_connection():
    """
    Route to check the connection status with MinIO.
    """
    try:
        # Attempt to check if the bucket exists to verify the connection
        if minio_client.bucket_exists(bucket_name):
            return {"status": "Connected to MinIO", "bucket": f"Bucket '{bucket_name}' exists."}
        else:
            return {"status": "Connected to MinIO", "bucket": f"Bucket '{bucket_name}' does not exist."}
    except S3Error as err:
        return {"status": "Failed to connect to MinIO", "error": str(err)}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file to MinIO storage.
    """
    try:
        file_content = await file.read()
        file_like_object = BytesIO(file_content)
        
        # Upload the file to MinIO
        minio_client.put_object(
            bucket_name,
            file.filename,
            file_like_object,
            length=len(file_content),
            content_type=file.content_type
        )
        return {"message": f"File '{file.filename}' uploaded successfully."}
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error occurred: {err}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Endpoint to download a file from MinIO storage.
    """
    try:
        # Download the file from MinIO
        response = minio_client.get_object(bucket_name, filename)
        
        # Create a BytesIO object from the downloaded file content
        file_content = response.read()
        file_like_object = BytesIO(file_content)
        
        # Return the file as a response
        return Response(
            content=file_like_object.getvalue(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except S3Error as err:
        raise HTTPException(status_code=500, detail=f"Error occurred: {err}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
