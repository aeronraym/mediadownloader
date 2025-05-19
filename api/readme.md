# Social Media Downloader API

A FastAPI-powered service to download media from popular social media platforms (YouTube, Twitter, Instagram, Facebook, TikTok, Reddit) to your local machine or directly to an AWS S3 bucket.

---

## Features

- Download videos/images from a variety of social media platforms via URL.
- Downloaded media can be streamed directly or uploaded to S3.
- Supports both GET (with query parameter) and POST (with JSON body) endpoints.
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust video/audio handling.
- S3 credentials and paths are managed via environment variables for security.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/username/repo.git
cd repo
```

### 2. Create a virtual environment (optional, but recommended)

```bash
# On Windows
python -m venv env_name
env_name\Scripts\activate 
    # or 
env_name\Scripts\activate.bat

# On Mac/Linux
python3 -m venv env_name
source env_name/bin/activate

# To Deactivate 
deactivate 
```

### 3. Install dependencies using PIP (Preferred Installer Program)
```bash
pip install -r requirements.txt # -r stands for install from a file
# or 
pip3 install -r requirements.txt


#view install dependencies
pip list
```

### 4. Install FFmpeg

#### Option 1: Using winget (Windows 10/11)
```powershell
winget install ffmpeg
```

#### Option 2: using linux
``` bash


```


#### Option 3: Manual Download

- Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (Windows) or [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (all platforms).
- Extract, and add the `bin` folder to your system PATH.

#### Confirm Installation

```bash
ffmpeg -version
```

---

### 5. Set up your `.env` file

Create a `.env` file in the project root with the following content:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
S3_BUCKET=your_bucket_name
FFMPEG_PATH=C:\\full\\path\\to\\ffmpeg\\bin    # optional, only if ffmpeg is not in system PATH
py_media_downloader_s3_key=                    # optional, default S3 object key
```

---

### 6. Run the API

```bash
uvicorn api.main:app --reload
# or, if your entry is in the root:
# uvicorn main:app --reload
```

---

## API Usage

### Download to Local (Streamed Response)

#### GET

```
GET /download?url=https://www.youtube.com/watch?v=J9ahZRa7ul0
```

#### POST

```http
POST /download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=J9ahZRa7ul0"
}
```

---

### Download to S3

```http
POST /download-to-s3
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=J9ahZRa7ul0"
}
```

Response:
```json
{
  "s3_url": "https://your-bucket-name.s3.your-region.amazonaws.com/filename.ext",
  "filename": "filename.ext"
}
```

---

## Deployment Notes

- On deployment, make sure to run `pip install -r requirements.txt` in your environment.
- Make sure your `.env` file is present and correct.
- If deploying with Docker or cloud services, ensure environment variables are set securely.

---

## Troubleshooting

- If you see an error like `ffmpeg is not installed`, ensure FFmpeg is on your system PATH or set `FFMPEG_PATH` in `.env`.
- For S3 upload errors, check your AWS credentials and bucket permissions.
- Always restart your terminal/server after updating `.env` or installing new dependencies.

---