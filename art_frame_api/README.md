# Art Frame Processing API — Technical Overview

This API allows clients to upload frame images, select frame coordinates online, process artwork, and create multiple framed images in bulk. The system is designed for easy extension to support multiple frames per image in the future.

## 1. Frame Upload & Coordinate Setup

### POST /frames/upload
Upload a frame template image to the server.
- **Request (multipart/form-data):**
  - `frame_image`: Frame template file (JPG/PNG/WebP/TIFF/BMP)
  - `frame_name`: String name for identification
- **Response:**
  - `frame_id`
  - URL for coordinate selection
  - URL for frame image preview

### GET /frames/{frame_id}/select
Returns a web-based HTML canvas to select the four corner coordinates.
- **User Flow:**
  1. Client uploads frame image
  2. Client opens this link in browser
  3. Click the four frame corners in order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
  4. Click “Save Coordinates”

### POST /frames/{frame_id}/coordinates
Save the selected coordinates in the database.
- **Request Body:**
```json
{
  "coordinates": {
    "top_left": [x1, y1],
    "top_right": [x2, y2],
    "bottom_right": [x3, y3],
    "bottom_left": [x4, y4]
  }
}
```
- **Response:**
  - Coordinates saved
  - Frame ready for image processing

### GET /frames
List all uploaded frames with coordinate status.

## 2. Artwork Processing APIs

### POST /process/batch
Process multiple artwork images with a selected frame.
- **Request (multipart/form-data):**
  - `frame_id`
  - `artwork[]`: Array of image files
- **Response:**
  - `job_id` (for tracking processing)

### GET /process/status/{job_id}
Check batch processing progress.

### GET /process/results/{job_id}
Download all framed artwork (individual URLs + ZIP).

## 3. Bulk Frame Creation APIs

### POST /frames/bulk/upload
Upload multiple frame templates in one request.
- **Request (multipart/form-data):**
  - `frames[]`: array of frame image files
  - `names[]`: optional names (matched by index)
- **Response:**
  - List of frame_ids
  - Links for coordinate selection for each frame

### POST /frames/bulk/coordinates
Save coordinates for multiple frames at once.
- **Request Body Example:**
```json
{
  "frames": [
    {
      "frame_id": "f1",
      "coordinates": { ... }
    },
    {
      "frame_id": "f2",
      "coordinates": { ... }
    }
  ]
}
```

## 4. Future-Ready: Multi-Frame in a Single Output
The API is designed so that in future versions:
- A single artwork can be placed inside multiple frames
- A frame can contain more than one coordinate region
- Frames can be layered or merged automatically

**Future Endpoint Example:**
- `POST /process/multi-frame`: Process artwork with multiple frames applied in sequence or layers.

## Delivered APIs Summary

### Frame Setup
- `POST /frames/upload`
- `GET /frames/{frame_id}/select`
- `POST /frames/{frame_id}/coordinates`
- `GET /frames`

### Artwork Processing
- `POST /process/batch`
- `GET /process/status/{job_id}`
- `GET /process/results/{job_id}`

### Bulk Operations
- `POST /frames/bulk/upload`
- `POST /frames/bulk/coordinates`

## Implementation Notes
- Uses FastAPI for minimal, clean API code
- Core logic is separated in `core.py` for maintainability
- No authentication or user management for simplicity (add later as needed)
- Storage is file-based and easy to migrate to a database or cloud
- HTML/JS for coordinate selection is included in `static/coordinate_selector.html`

---

**Ready for rapid prototyping and future expansion!**
