# 🖼️ Art Frame Processing API

**Professional artwork framing made simple!** Upload your frame template, set coordinates with our interactive UI, then process unlimited artwork through our REST API.

## ✨ What This Does

Transform any artwork to fit perfectly within your frame template using professional perspective correction. Perfect for:
- **Art Galleries**: Standardize artwork presentation
- **Print Shops**: Automated framing service
- **E-commerce**: Product mockups with consistent framing
- **Artists**: Preview artwork in different frames

## 🚀 Quick Start (3 Simple Steps)

### 1️⃣ Start the Server
```bash
# Clone and setup
git clone https://github.com/oyekamal/Automated-Art-Frame-Processing-Tool.git
cd Automated-Art-Frame-Processing-Tool
pip install -r requirements.txt

# Start API server
cd art_frame_api
python main.py
```
*Server runs at: http://localhost:8000*

### 2️⃣ Setup Your Frame (One-Time)
1. **Visit**: http://localhost:8000/frames/manage
2. **Upload** your frame template image
3. **Click the 4 corners** of your frame area (where artwork should appear)
4. **Save coordinates** - you'll get a `frame_id` to use in API calls

### 3️⃣ Process Artwork via API
```bash
# Replace {frame_id} with your actual frame ID from step 2
curl -X POST "http://localhost:8000/frames/{frame_id}/process-artwork" \
  -F "artwork_images=@your_artwork.jpg"
```

**That's it!** Get download URLs in the response to retrieve your framed artwork.

## 🛠️ Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository

*All Python packages install automatically from `requirements.txt`*

## 🎯 Quick Start

## 📖 Complete API Guide

### 🔍 Get Your Frame ID
After setting up coordinates in the web UI, get your frame ID:
```bash
curl "http://localhost:8000/frames"
```
*Copy the `frame_id` from the response for use in processing calls.*

### 🎨 Process Your Artwork

**Single Image:**
```bash
curl -X POST "http://localhost:8000/frames/4134ad05-aabb-4d74-ad9a-06138759914a/process-artwork" \
  -F "artwork_images=@your_image.jpg"
```

**Multiple Images:**
```bash
curl -X POST "http://localhost:8000/frames/4134ad05-aabb-4d74-ad9a-06138759914a/process-artwork" \
  -F "artwork_images=@image1.jpg" \
  -F "artwork_images=@image2.png" \
  -F "artwork_images=@image3.jpeg"
```

**Using Postman/Insomnia:**
- **Method**: POST
- **URL**: `http://localhost:8000/frames/{your_frame_id}/process-artwork`
- **Body**: Form-data
- **Key**: `artwork_images` (File type)
- **Value**: Select your image file(s)

### 📥 API Response Example
```json
{
  "success": true,
  "frame_id": "4134ad05-aabb-4d74-ad9a-06138759914a",
  "processed_count": 2,
  "failed_count": 0,
  "results": [
    {
      "original_filename": "artwork.jpg",
      "output_filename": "framed_artwork.jpg", 
      "status": "success"
    }
  ],
  "download_urls": [
    "/results/abc123-session/framed_artwork.jpg"
  ]
}
```

### 💾 Download Processed Images
```bash
# Use the download_urls from the API response
curl -O "http://localhost:8000/results/abc123-session/framed_artwork.jpg"
```

*Or simply paste the download URL in your browser: `http://localhost:8000/results/abc123-session/framed_artwork.jpg`*

## 🎯 Real-World Examples

### Example 1: E-commerce Product Mockups
```bash
# Upload your frame template via web UI, get frame_id: "gallery-frame-001"
curl -X POST "http://localhost:8000/frames/gallery-frame-001/process-artwork" \
  -F "artwork_images=@product_design.png"
```

### Example 2: Batch Process Art Portfolio  
```bash
# Process multiple artworks at once
curl -X POST "http://localhost:8000/frames/vintage-frame-002/process-artwork" \
  -F "artwork_images=@painting1.jpg" \
  -F "artwork_images=@painting2.jpg" \
  -F "artwork_images=@sculpture_photo.png"
```

### Example 3: Using with Absolute Paths
```bash
curl --location 'http://localhost:8000/frames/4134ad05-aabb-4d74-ad9a-06138759914a/process-artwork' \
--form 'artwork_images=@"/home/user/Downloads/my_artwork.png"'
```

## 🔧 Troubleshooting

### Server Won't Start?
```bash
# Make sure you're in the right directory
cd art_frame_api
python main.py

# If python command not found, try:
python3 main.py
```

### Frame ID Not Working?
```bash
# Get list of all available frames and their IDs
curl "http://localhost:8000/frames"
# Copy the exact frame_id from the response
```

### Upload Failed?
- **File size**: Keep images under 50MB
- **File format**: Use JPG, PNG, or similar standard formats
- **File path**: Use absolute paths or ensure files exist

### Can't Download Results?
- Results expire after some time - process and download immediately
- Use the exact URL from the API response
- Check that the session_id and filename match exactly

## 📞 Support & Integration

### 🏢 For Business Integration
This API can be easily integrated into:
- **Web Applications**: Direct HTTP calls from any programming language
- **Mobile Apps**: Standard REST API integration
- **Automation Scripts**: Batch processing workflows
- **E-commerce Platforms**: Product mockup generation

### 🤝 Need Help?
- **Check the troubleshooting section** above for common issues
- **Test with the provided examples** to ensure everything works
- **Use small images first** to verify your setup before processing large batches

### ⚡ Performance Tips
- **Batch processing**: Upload multiple images in one API call for efficiency
- **Image optimization**: Resize large images before upload for faster processing
- **Local hosting**: Run on local server for fastest processing speeds

---

## 🎉 You're Ready!

**Perfect for:** Art galleries, print shops, e-commerce sites, marketing teams, and anyone who needs professional artwork framing at scale.

**Start now:** Follow the 3-step Quick Start guide above! 🚀

## 📊 Current Configuration

**Frame Coordinates:**
- Top-left: [194, 144]
- Top-right: [647, 140]
- Bottom-right: [610, 869]
- Bottom-left: [133, 824]

**Supported Formats:**
- Input: .jpg, .jpeg, .png, .bmp, .tiff, .webp
- Output: Same format as input with "framed_" prefix

