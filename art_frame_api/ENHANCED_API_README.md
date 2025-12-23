# Art Frame API - Enhanced Interactive Coordinate Selection

## Overview

This enhanced API provides a web-based interface for uploading frame images and selecting frame coordinates using an interactive UI similar to the standalone `interactive_frame_selector.py` script.

## New Features

### 1. Enhanced Interactive Coordinate Selection
- **URL**: `/frames/{frame_id}/interactive-select`
- Provides a rich, interactive UI similar to the original Python script
- Real-time visual feedback with colored corner markers
- Keyboard shortcuts (S for save, R for reset, ESC for clear)
- Displays coordinates in real-time
- Visual confirmation of selected area

### 2. Frame Management Dashboard
- **URL**: `/frames/manage`
- Upload new frames with drag-and-drop interface
- View all existing frames in a grid layout
- See configuration status at a glance
- Quick access to coordinate selection and editing

### 3. Enhanced Coordinate Saving
- Automatically creates visual representation of selected coordinates
- Saves coordinate data in JSON format compatible with the original script
- Provides downloadable coordinate files

## API Endpoints

### Frame Upload and Management
```
POST /frames/upload
- Upload frame image with name
- Returns frame_id and selection URL

GET /frames/manage
- Frame management dashboard (HTML)

GET /frames
- List all frames with status

GET /frames/{frame_id}/info
- Get frame information including dimensions
```

### Interactive Coordinate Selection
```
GET /frames/{frame_id}/interactive-select
- Enhanced interactive coordinate selection UI

POST /frames/{frame_id}/coordinates  
- Save selected coordinates with visual representation

GET /frames/{frame_id}/visual
- View the visual representation of coordinates

GET /frames/{frame_id}/coordinates-file
- Download coordinates JSON file
```

## Usage Workflow

1. **Upload Frame**: Go to `/frames/manage` and upload a frame image
2. **Select Coordinates**: Click "Select Coordinates" to open the interactive selector
3. **Click 4 Corners**: Follow the on-screen instructions to click corners in order:
   - Top-Left
   - Top-Right 
   - Bottom-Right
   - Bottom-Left
4. **Save Coordinates**: Press 'S' or click Save button
5. **Use for Processing**: Frame is now ready for batch artwork processing

## Interactive Features

The enhanced coordinate selector includes:

- **Visual Feedback**: Each corner is marked with a different color and number
- **Real-time Preview**: Lines connect selected points showing the frame area
- **Coordinate Display**: Shows exact coordinates as you select them
- **Keyboard Shortcuts**: 
  - `S` - Save coordinates
  - `R` - Reset selection
  - `ESC` - Clear current selection
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Clear feedback for invalid selections

## Files Created

When coordinates are saved, the system creates:
- `{frame_id}_coordinates.json` - Coordinate data file
- `{frame_id}_visual.jpg` - Visual representation with marked corners

## Compatibility

The coordinate format is fully compatible with the original `interactive_frame_selector.py` script and `apply_frame.py` for processing artwork.

## Running the API

```bash
cd art_frame_api
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then visit `http://localhost:8000/frames/manage` to start using the enhanced interface.