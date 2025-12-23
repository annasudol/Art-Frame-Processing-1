# Running the Art Frame Processing API

## 1. Install Requirements

```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart pillow
```

## 2. Project Structure

```
art_frame_api/
├── main.py                  # FastAPI app (entry point)
├── core.py                  # Core logic (frame/artwork processing)
├── static/                  # Static files (coordinate selector UI)
├── storage/                 # Uploaded frames, artwork, results
├── database/                # Frame metadata (frames.json)
└── README.md                # API documentation
```

## 3. Start the API Server

From the `art_frame_api/` directory:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- The API will be available at: [http://localhost:8000](http://localhost:8000)
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 4. Example Workflow

### A. Upload a Frame
- `POST /frames/upload` (use Postman or Swagger UI)
- Upload a frame image and provide a name

### B. Select Frame Coordinates
- Open the `selection_url` from the upload response in your browser
- Click the four corners of the frame (top-left, top-right, bottom-right, bottom-left)
- Click "Save Coordinates"

### C. Process Artwork
- `POST /process/batch` with `frame_id` and one or more artwork images
- Get a `job_id` in the response

### D. Check Status & Download Results
- `GET /process/status/{job_id}` to check progress
- `GET /process/results/{job_id}` to get URLs for all processed images

## 5. Bulk Operations
- Use `/frames/bulk/upload` and `/frames/bulk/coordinates` for multi-frame workflows

## 6. Notes
- All uploads and results are stored in the `storage/` directory
- Frame metadata is stored in `database/frames.json`
- No authentication or user management (add as needed)
- For production, use a process manager and consider Docker

---

**Ready to use! See README.md for full API details.**
