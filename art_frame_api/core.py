import os
import uuid
import shutil
import json
import cv2
import numpy as np
from typing import List
from datetime import datetime

FRAMES_DIR = "storage/frames"
UPLOADS_DIR = "storage/uploads"
RESULTS_DIR = "storage/results"
DB_PATH = "database/frames.json"

# Helper to load/save frame metadata
def load_db():
    if not os.path.exists(DB_PATH):
        return {"frames": []}
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def save_frame_image(frame_image, frame_name):
    frame_id = str(uuid.uuid4())
    frame_path = os.path.join(FRAMES_DIR, f"{frame_id}.jpg")
    with open(frame_path, "wb") as f:
        shutil.copyfileobj(frame_image.file, f)
    db = load_db()
    db["frames"].append({
        "frame_id": frame_id,
        "frame_name": frame_name,
        "image_path": frame_path,
        "coordinates": None
    })
    save_db(db)
    image_url = f"/frames/images/{frame_id}.jpg"
    selection_url = f"/frames/{frame_id}/select"
    return frame_id, image_url, selection_url

def save_coordinates(frame_id, coordinates):
    db = load_db()
    for frame in db["frames"]:
        if frame["frame_id"] == frame_id:
            frame["coordinates"] = coordinates
    save_db(db)

def save_coordinates_enhanced(frame_id, coordinates):
    """Enhanced coordinate saving with visual representation like the original script"""
    try:
        # Load frame image
        frame_path = os.path.join(FRAMES_DIR, f"{frame_id}.jpg")
        if not os.path.exists(frame_path):
            return False
            
        image = cv2.imread(frame_path)
        if image is None:
            return False
            
        # Convert coordinates to the format expected by the original script
        corners_array = [
            coordinates["top_left"],
            coordinates["top_right"],
            coordinates["bottom_right"],
            coordinates["bottom_left"]
        ]
        
        # Create frame data like the original script
        frame_data = {
            "frame_id": frame_id,
            "image_path": frame_path,
            "image_dimensions": {
                "width": image.shape[1],
                "height": image.shape[0]
            },
            "corners": coordinates,
            "corners_array": corners_array,
            "created_at": datetime.now().isoformat()
        }
        
        # Save JSON coordinates file
        coords_file = os.path.join(FRAMES_DIR, f"{frame_id}_coordinates.json")
        with open(coords_file, 'w') as f:
            json.dump(frame_data, f, indent=2)
        
        # Save visual representation
        visual_path = os.path.join(FRAMES_DIR, f"{frame_id}_visual.jpg")
        save_visual_representation(image, corners_array, visual_path)
        
        # Update database
        db = load_db()
        for frame in db["frames"]:
            if frame["frame_id"] == frame_id:
                frame["coordinates"] = coordinates
                frame["coordinates_file"] = coords_file
                frame["visual_file"] = visual_path
                frame["updated_at"] = datetime.now().isoformat()
        save_db(db)
        
        return True
        
    except Exception as e:
        print(f"Error saving enhanced coordinates: {e}")
        return False

def save_visual_representation(image, corners, output_path):
    """Save an image showing the selected frame like the original script"""
    visual = image.copy()
    
    # Draw the selected quadrilateral
    corners_np = np.array(corners, dtype=np.int32)
    cv2.polylines(visual, [corners_np], True, (0, 255, 0), 3)
    
    # Draw corner points and labels
    labels = ["TL", "TR", "BR", "BL"]
    for i, (corner, label) in enumerate(zip(corners, labels)):
        cv2.circle(visual, tuple(corner), 10, (0, 255, 0), -1)
        cv2.putText(visual, f"{i+1}:{label}", 
                   (corner[0] + 15, corner[1] - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    cv2.imwrite(output_path, visual)
    return output_path

def get_frame_list():
    db = load_db()
    for frame in db["frames"]:
        frame["has_coordinates"] = frame["coordinates"] is not None
    return db

def process_batch_artwork(frame_id, artwork_files):
    # Stub: Save files, create job, return job_id
    job_id = str(uuid.uuid4())
    # Save uploaded artwork
    job_dir = os.path.join(RESULTS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    for art in artwork_files:
        art_path = os.path.join(job_dir, art.filename)
        with open(art_path, "wb") as f:
            shutil.copyfileobj(art.file, f)
    # In real code, trigger background processing here
    # For now, just mark as done
    with open(os.path.join(job_dir, "status.json"), "w") as f:
        json.dump({"status": "completed", "processed": len(artwork_files), "total": len(artwork_files)}, f)
    return job_id

def get_job_status(job_id):
    job_dir = os.path.join(RESULTS_DIR, job_id)
    status_path = os.path.join(job_dir, "status.json")
    if os.path.exists(status_path):
        with open(status_path) as f:
            return json.load(f)
    return {"status": "not_found"}

def get_job_results(job_id):
    job_dir = os.path.join(RESULTS_DIR, job_id)
    files = [f for f in os.listdir(job_dir) if not f.endswith(".json")]
    return {"job_id": job_id, "results": files}

async def apply_frame_to_artwork(frame_id, artwork_images):
    """Apply frame coordinates to artwork images like batch_process_frames.py"""
    try:
        # Load frame data and coordinates
        db = load_db()
        frame_data = None
        for frame in db["frames"]:
            if frame["frame_id"] == frame_id:
                frame_data = frame
                break
        
        if not frame_data or not frame_data.get("coordinates"):
            return {"success": False, "error": "Frame not found or coordinates not set"}
        
        # Load frame image
        frame_path = os.path.join(FRAMES_DIR, f"{frame_id}.jpg")
        if not os.path.exists(frame_path):
            return {"success": False, "error": "Frame image not found"}
        
        background = cv2.imread(frame_path)
        if background is None:
            return {"success": False, "error": "Could not load frame image"}
        
        # Get frame coordinates in the correct order
        coords = frame_data["coordinates"]
        frame_corners = np.array([
            coords["top_left"],
            coords["top_right"],
            coords["bottom_right"],
            coords["bottom_left"]
        ], dtype="float32")
        
        # Create results directory for this processing session
        session_id = str(uuid.uuid4())
        results_dir = os.path.join(RESULTS_DIR, session_id)
        os.makedirs(results_dir, exist_ok=True)
        
        processed_count = 0
        failed_count = 0
        results = []
        download_urls = []
        
        # Process each artwork image
        for artwork_file in artwork_images:
            try:
                # Save uploaded artwork temporarily
                temp_art_path = os.path.join(results_dir, f"temp_{artwork_file.filename}")
                with open(temp_art_path, "wb") as f:
                    shutil.copyfileobj(artwork_file.file, f)
                
                # Create output filename
                output_filename = f"framed_{artwork_file.filename}"
                output_path = os.path.join(results_dir, output_filename)
                
                # Apply frame processing (like batch_process_frames.py)
                if apply_art_to_frame_core(temp_art_path, frame_corners, background, output_path):
                    processed_count += 1
                    results.append({
                        "original_filename": artwork_file.filename,
                        "output_filename": output_filename,
                        "status": "success"
                    })
                    download_urls.append(f"/results/{session_id}/{output_filename}")
                else:
                    failed_count += 1
                    results.append({
                        "original_filename": artwork_file.filename,
                        "status": "failed",
                        "error": "Frame processing failed"
                    })
                
                # Clean up temp file
                os.remove(temp_art_path)
                
            except Exception as e:
                failed_count += 1
                results.append({
                    "original_filename": artwork_file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Save processing metadata
        metadata = {
            "session_id": session_id,
            "frame_id": frame_id,
            "processed_count": processed_count,
            "failed_count": failed_count,
            "created_at": datetime.now().isoformat(),
            "results": results
        }
        
        with open(os.path.join(results_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "session_id": session_id,
            "processed_count": processed_count,
            "failed_count": failed_count,
            "results": results,
            "download_urls": download_urls
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def apply_art_to_frame_core(art_image_path, frame_corners, background_image, output_path):
    """Core frame application logic from batch_process_frames.py"""
    try:
        # Load the art image
        art_img = cv2.imread(art_image_path)
        if art_img is None:
            return False
        
        # Create source points (art image corners)
        h, w = art_img.shape[:2]
        src_points = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], dtype="float32")
        
        # Calculate perspective transform from art to frame
        M = cv2.getPerspectiveTransform(src_points, frame_corners)
        
        # Warp the art image to fit the frame
        result = background_image.copy()
        warped_art = cv2.warpPerspective(art_img, M, (result.shape[1], result.shape[0]))
        
        # Create mask for the frame area
        mask = np.zeros(result.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(frame_corners), 255)
        
        # Apply the art to the frame area
        result[mask > 0] = warped_art[mask > 0]
        
        # Save the result
        cv2.imwrite(output_path, result)
        return True
        
    except Exception as e:
        print(f"Error processing {art_image_path}: {e}")
        return False
