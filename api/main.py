from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from botocore.exceptions import BotoCoreError, NoCredentialsError

import boto3
import yt_dlp
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Enterprise Social Media Downloader API",
    description="Download videos or images from most social media URLs.",
    version="1.0.0"
)

# Read S3 credentials and bucket from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

class DownloadRequest(BaseModel):
    url: HttpUrl

@app.get("/")
def root():
    return JSONResponse(
        content={
            "message": "Welcome to the Enterprise Social Media Downloader API",
            "documentation_url": "/info",
            "download_endpoint": "/download"
        }
    )

@app.get("/info")
def info():
    import shutil
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        ffmpeg_path = "Not found"
    # Return API information
    return JSONResponse(
        content={
            "message": "This API allows you to download media from various social media platforms.",
            "supported_platforms": [
                "YouTube",
                "Twitter",
                "Instagram",
                "Facebook",
                "TikTok",
                "Reddit"
            ],
            "ffmpeg_path": ffmpeg_path
        }
    )

@app.get("/download")
async def download_media_get(url: str = Query(..., description="The URL of the media to download."),
                             fileName: str = Query(None, description="Optional filename for the downloaded media.")):
    if not url:
        return JSONResponse(
            status_code=400,
            content={"detail": "URL parameter is required."}
        )
    ydl_opts = {
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "skip_download": False,
        "format": "bestvideo+bestaudio/best",
        "verbose": True,
        # "ffmpeg_location": os.getenv("FFMPEG_PATH"),  # Set this in your .env if needed
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=True)
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Download failed.")
            def iterfile():
                with open(file_path, "rb") as f:
                    yield from f
            file_name = fileName + "." + os.path.basename(file_path).split(".")[1] or os.path.basename(file_path)
            headers = {"Content-Disposition": f"attachment; filename={file_name}"}
            return StreamingResponse(iterfile(), headers=headers, media_type="application/octet-stream")
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/download")
async def download_media(request: DownloadRequest):
    url = request.url
    if not url:
        return JSONResponse(
            status_code=400,
            content={"detail": "URL parameter is required."}
        )
    ydl_opts = {
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "skip_download": False,
        "format": "bestvideo+bestaudio/best",
        "ffmpeg_location": os.getenv("FFMPEG_PATH"),  # Set this in your .env if needed
        "verbose": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=True)
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Download failed.")
            def iterfile():
                with open(file_path, "rb") as f:
                    yield from f
            filename = os.path.basename(file_path)
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
            return StreamingResponse(iterfile(), headers=headers, media_type="application/octet-stream")
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/download-to-s3")
async def download_to_s3(request: DownloadRequest):
    s3_key = os.getenv("py_media_downloader_s3_key")

    url = request.url
    if not url:
        return JSONResponse(
            status_code=400,
            content={"detail": "URL parameter is required."}
        )
    ydl_opts = {
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "skip_download": False,
        "format": "bestvideo+bestaudio/best",
        "ffmpeg_location": os.getenv("FFMPEG_PATH"),  # Set this in your .env if needed
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Download failed.")
            filename = s3_key or os.path.basename(file_path)
            try:
                s3_client.upload_file(file_path, S3_BUCKET, filename)
                s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
                return JSONResponse({"s3_url": s3_url, "filename": filename})
            except (BotoCoreError, NoCredentialsError) as e:
                raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")