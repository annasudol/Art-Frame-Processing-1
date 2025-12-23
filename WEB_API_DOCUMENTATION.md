# 🌐 Web API for Art Frame Processing System

## 📋 Project Overview

Transform the existing local frame processing tool into a web-based API service that allows users to upload frame templates, select coordinates online, and process artwork through REST endpoints.

## 🎯 API Architecture

### Core Components
- **Frame Management API**: Upload and manage frame templates
- **Coordinate Selection Interface**: Web-based corner selection tool  
- **Batch Processing API**: Process artwork with saved frames
- **Storage Layer**: Frame templates and coordinates persistence
- **Processing Queue**: Handle multiple image processing requests

## 🔧 Technical Stack (Minimalistic Approach)

```python
# Core Dependencies
FastAPI          # Lightweight, high-performance API framework
OpenCV           # Image processing (existing code)
SQLite           # Simple database for frame metadata
Pillow           # Additional image handling
uvicorn          # ASGI server
python-multipart # File upload support
```

## 📚 API Specification

### 1. Frame Management Endpoints

#### `POST /frames/upload`
Upload a frame template image

**Request:**
```http
POST /frames/upload
Content-Type: multipart/form-data

{
  "frame_image": <file>,
  "frame_name": "vintage_frame_01"
}
```

**Response:**
```json
{
  "frame_id": "uuid-123",
  "frame_name": "vintage_frame_01",
  "image_url": "/frames/uuid-123/image",
  "selection_url": "/frames/uuid-123/select",
  "status": "uploaded"
}
```

#### `GET /frames`
List all available frame templates

**Response:**
```json
{
  "frames": [
    {
      "frame_id": "uuid-123",
      "frame_name": "vintage_frame_01",
      "has_coordinates": true,
      "created_at": "2025-12-01T10:30:00Z"
    }
  ]
}
```

### 2. Coordinate Selection Endpoints

#### `GET /frames/{frame_id}/select`
Returns HTML interface for coordinate selection

**Response:**
```html
<!-- Interactive web interface with click-to-select functionality -->
<html>
  <canvas id="frame-canvas"></canvas>
  <script>
    // JavaScript for corner selection
    // Similar to existing interactive_frame_selector.py logic
  </script>
</html>
```

#### `POST /frames/{frame_id}/coordinates`
Save selected coordinates

**Request:**
```json
{
  "coordinates": {
    "top_left": [194, 144],
    "top_right": [647, 140],
    "bottom_right": [610, 869],
    "bottom_left": [133, 824]
  }
}
```

**Response:**
```json
{
  "frame_id": "uuid-123",
  "coordinates_saved": true,
  "ready_for_processing": true
}
```

### 3. Image Processing Endpoints

#### `POST /process/batch`
Process multiple artwork images with selected frame

**Request:**
```http
POST /process/batch
Content-Type: multipart/form-data

{
  "frame_id": "uuid-123",
  "artwork": [<file1>, <file2>, <file3>]
}
```

**Response:**
```json
{
  "job_id": "job-456",
  "status": "processing",
  "total_images": 3,
  "estimated_completion": "2025-12-01T10:35:00Z"
}
```

#### `GET /process/status/{job_id}`
Check processing status

**Response:**
```json
{
  "job_id": "job-456",
  "status": "completed",
  "processed": 3,
  "total": 3,
  "results_url": "/process/results/job-456"
}
```

#### `GET /process/results/{job_id}`
Download processed images

**Response:**
```json
{
  "job_id": "job-456",
  "results": [
    {
      "original_name": "artwork1.jpg",
      "processed_url": "/downloads/job-456/framed_artwork1.jpg"
    },
    {
      "original_name": "artwork2.png", 
      "processed_url": "/downloads/job-456/framed_artwork2.png"
    }
  ],
  "zip_download": "/downloads/job-456/all_framed.zip"
}
```

## 💻 Implementation Plan

### Phase 1: Basic API Structure (2-3 days)

```python
# main.py - FastAPI application
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import uuid
import sqlite3

app = FastAPI(title="Art Frame Processing API")

# Database setup
def init_db():
    conn = sqlite3.connect('frames.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS frames (
            id TEXT PRIMARY KEY,
            name TEXT,
            image_path TEXT,
            coordinates TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.close()

@app.post("/frames/upload")
async def upload_frame(frame_image: UploadFile, frame_name: str):
    frame_id = str(uuid.uuid4())
    # Save image, store metadata
    return {"frame_id": frame_id, "selection_url": f"/frames/{frame_id}/select"}

@app.get("/frames/{frame_id}/select", response_class=HTMLResponse)
async def select_coordinates(frame_id: str):
    # Return HTML canvas interface
    return """
    <html>
        <canvas id="canvas" width="800" height="600"></canvas>
        <script>
            // Coordinate selection logic
        </script>
    </html>
    """
```

### Phase 2: Processing Integration (2-3 days)

```python
# processing.py - Integrate existing frame processing logic
import cv2
import numpy as np
from pathlib import Path

class FrameProcessor:
    def __init__(self):
        # Migrate existing batch_process_frames.py logic
        pass
    
    def process_artwork(self, artwork_path, frame_coords, output_path):
        # Use existing apply_art_to_frame function
        pass
    
    async def batch_process(self, job_id, artwork_files, frame_coords):
        # Process in background with progress tracking
        pass
```

### Phase 3: Web Interface (1-2 days)

```html
<!-- coordinate_selection.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Frame Coordinate Selection</title>
    <style>
        canvas { border: 1px solid #ccc; cursor: crosshair; }
        .instructions { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="instructions">
        <h3>Click on frame corners in order:</h3>
        <ol>
            <li>Top-Left</li>
            <li>Top-Right</li>
            <li>Bottom-Right</li>
            <li>Bottom-Left</li>
        </ol>
    </div>
    <canvas id="frameCanvas"></canvas>
    <button onclick="saveCoordinates()">Save Coordinates</button>
    
    <script>
        let corners = [];
        // Canvas click handling and coordinate capture
    </script>
</body>
</html>
```

## 🚀 Deployment Strategy

### Development Setup
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart pillow

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Docker containerization
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# Deploy to cloud (AWS/Digital Ocean/Heroku)
```

## 📁 Project Structure

```
art-frame-api/
├── main.py                    # FastAPI application
├── models/                    # Database models
│   ├── frames.py
│   └── jobs.py
├── processing/               # Image processing logic
│   ├── frame_processor.py    # Migrated from existing code
│   └── background_tasks.py   # Async job handling
├── static/                   # Web interface files
│   ├── coordinate_selector.html
│   ├── style.css
│   └── app.js
├── storage/                  # File storage
│   ├── frames/              # Uploaded frame templates
│   ├── uploads/             # User artwork uploads
│   └── results/             # Processed images
├── database/
│   └── frames.db           # SQLite database
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔄 User Workflow

1. **Upload Frame**: POST frame image to `/frames/upload`
2. **Select Coordinates**: Open `/frames/{id}/select` in browser
3. **Click Corners**: Interactive web interface saves coordinates
4. **Upload Artwork**: POST multiple images to `/process/batch`
5. **Monitor Progress**: GET `/process/status/{job_id}`
6. **Download Results**: GET processed images from `/process/results/{job_id}`

## ⚡ Performance Considerations

### Optimization Strategies
- **Background Processing**: Use Celery or FastAPI BackgroundTasks
- **Image Caching**: Store processed thumbnails for preview
- **Batch Optimization**: Process multiple images in parallel
- **Compression**: Automatic image optimization for web delivery

### Scaling Options
- **Horizontal Scaling**: Deploy multiple API instances
- **Database Upgrade**: Migrate to PostgreSQL for production
- **CDN Integration**: Use AWS S3/CloudFront for image delivery
- **Queue System**: Redis/RabbitMQ for high-volume processing

## 🔒 Security Features

- **File Validation**: Strict image format checking
- **Rate Limiting**: Prevent API abuse
- **Authentication**: JWT tokens for user management
- **CORS Configuration**: Secure cross-origin requests

## 📈 Development Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| API Core | 3 days | Basic endpoints working |
| Processing Integration | 3 days | Image processing via API |
| Web Interface | 2 days | Coordinate selection UI |
| Testing & Polish | 2 days | Production-ready system |
| **Total** | **10 days** | **Full web service** |

## 💰 Deployment Costs (Estimated)

- **Development Server**: $5-10/month (DigitalOcean droplet)
- **Production Server**: $20-50/month (depending on usage)
- **Storage**: $0.02/GB (for processed images)
- **Domain & SSL**: $15/year

## 🎯 Success Metrics

- ✅ Upload and select coordinates in < 2 minutes
- ✅ Process 10 images in < 30 seconds
- ✅ 99.9% API uptime
- ✅ Support 1000+ concurrent users
- ✅ Mobile-responsive coordinate selection

---

**Ready to transform your desktop tool into a powerful web service! 🚀**