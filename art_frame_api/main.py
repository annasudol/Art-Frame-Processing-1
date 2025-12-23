from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import uuid
import os
import shutil
import json
from PIL import Image

from core import save_frame_image, save_coordinates, save_coordinates_enhanced, process_batch_artwork, get_frame_list, get_job_status, get_job_results

app = FastAPI(title="Art Frame Processing API")

# Mount static for frame previews and HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to frames management"""
    return HTMLResponse(content='''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Art Frame Processing API</title>
        <meta http-equiv="refresh" content="0;url=/frames/manage">
    </head>
    <body>
        <h1>🖼️ Art Frame Processing API</h1>
        <p>Redirecting to <a href="/frames/manage">Frame Management</a>...</p>
    </body>
    </html>
    ''')

FRAMES_DIR = "storage/frames"
UPLOADS_DIR = "storage/uploads"
RESULTS_DIR = "storage/results"
DB_PATH = "database/frames.json"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs("database", exist_ok=True)

# Serve frame images through a custom endpoint
@app.get("/frames/images/{frame_filename}")
async def serve_frame_image(frame_filename: str):
    frame_path = os.path.join(FRAMES_DIR, frame_filename)
    if os.path.exists(frame_path):
        return FileResponse(frame_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Frame image not found")

@app.post("/frames/upload")
async def upload_frame(frame_image: UploadFile = File(...), frame_name: str = Form(...)):
    frame_id, image_url, selection_url = save_frame_image(frame_image, frame_name)
    return {"frame_id": frame_id, "image_url": image_url, "selection_url": selection_url}

@app.get("/frames/{frame_id}/select", response_class=HTMLResponse)
async def select_coordinates(frame_id: str):
    # Serve HTML canvas for coordinate selection
    with open("static/coordinate_selector.html") as f:
        html = f.read().replace("__FRAME_ID__", frame_id)
    return HTMLResponse(content=html)

@app.get("/frames/{frame_id}/interactive-select", response_class=HTMLResponse)
async def interactive_select_coordinates(frame_id: str):
    # Serve enhanced interactive coordinate selector
    with open("static/interactive_selector.html") as f:
        html = f.read().replace("__FRAME_ID__", frame_id)
    return HTMLResponse(content=html)

@app.get("/frames/{frame_id}/info")
async def get_frame_info(frame_id: str):
    """Get frame information including image dimensions"""
    frame_path = os.path.join(FRAMES_DIR, f"{frame_id}.jpg")
    if not os.path.exists(frame_path):
        return JSONResponse(status_code=404, content={"error": "Frame not found"})
    
    with Image.open(frame_path) as img:
        width, height = img.size
    
    return {
        "frame_id": frame_id,
        "image_dimensions": {
            "width": width,
            "height": height
        },
        "image_url": f"/frames/images/{frame_id}.jpg"
    }

@app.post("/frames/{frame_id}/coordinates")
async def save_frame_coordinates(frame_id: str, request: Request):
    data = await request.json()
    coordinates = data["coordinates"]
    
    # Save coordinates with enhanced metadata like the original script
    success = save_coordinates_enhanced(frame_id, coordinates)
    
    if success:
        return {
            "frame_id": frame_id, 
            "coordinates_saved": True, 
            "ready_for_processing": True,
            "visual_saved": True
        }
    else:
        return JSONResponse(
            status_code=500, 
            content={"error": "Failed to save coordinates"}
        )

@app.get("/frames")
async def list_frames():
    return get_frame_list()

@app.get("/frames/manage", response_class=HTMLResponse)
async def frames_management_page():
    """Serve frames management page"""
    with open("static/frames_manager.html") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.post("/process/batch")
async def process_batch(frame_id: str = Form(...), artwork: List[UploadFile] = File(...)):
    job_id = process_batch_artwork(frame_id, artwork)
    return {"job_id": job_id, "status": "processing"}

@app.post("/frames/{frame_id}/process-artwork")
async def process_artwork_with_frame(frame_id: str, artwork_images: List[UploadFile] = File(...)):
    """Process uploaded artwork images with the specified frame coordinates"""
    try:
        # Import frame processing functions
        from core import apply_frame_to_artwork
        
        # Process the artwork with the frame
        result = await apply_frame_to_artwork(frame_id, artwork_images)
        
        if result["success"]:
            return {
                "success": True,
                "frame_id": frame_id,
                "processed_count": result["processed_count"],
                "failed_count": result["failed_count"],
                "results": result["results"],
                "download_urls": result["download_urls"]
            }
        else:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"], "success": False}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}", "success": False}
        )

@app.get("/results/{session_id}/{filename}")
async def get_result_file(session_id: str, filename: str):
    """Serve processed artwork result files"""
    file_path = os.path.join("storage/results", session_id, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="image/jpeg",
        filename=filename
    )

@app.get("/process/status/{job_id}")
async def process_status(job_id: str):
    return get_job_status(job_id)

@app.get("/process/results/{job_id}")
async def process_results(job_id: str):
    return get_job_results(job_id)

@app.get("/frames/{frame_id}/visual")
async def get_frame_visual(frame_id: str):
    """Get the visual representation of the frame coordinates"""
    visual_path = os.path.join(FRAMES_DIR, f"{frame_id}_visual.jpg")
    if os.path.exists(visual_path):
        return FileResponse(visual_path, media_type="image/jpeg")
    else:
        return JSONResponse(status_code=404, content={"error": "Visual not found"})

@app.get("/frames/{frame_id}/coordinates-file")
async def get_coordinates_file(frame_id: str):
    """Download the coordinates JSON file"""
    coords_path = os.path.join(FRAMES_DIR, f"{frame_id}_coordinates.json")
    if os.path.exists(coords_path):
        return FileResponse(coords_path, media_type="application/json", filename=f"frame_{frame_id}_coordinates.json")
    else:
        return JSONResponse(status_code=404, content={"error": "Coordinates file not found"})

# Bulk upload endpoints (stubs)
@app.post("/frames/bulk/upload")
async def bulk_upload(frames: List[UploadFile] = File(...), names: List[str] = Form(None)):
    # Implement bulk upload logic
    return {"frames": []}

@app.post("/frames/bulk/coordinates")
async def bulk_coordinates(request: Request):
    # Implement bulk coordinates save logic
    return {"saved": True}
