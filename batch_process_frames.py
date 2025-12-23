import cv2
import numpy as np
import json
import os
from pathlib import Path

def load_frame_coordinates(json_file="frame_coordinates.json"):
    """Load saved frame coordinates"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract coordinates from the dictionary format
        corners = data['corners']
        
        # Convert to numpy array in the correct order: top-left, top-right, bottom-right, bottom-left
        coords = np.array([
            corners['top_left'],
            corners['top_right'], 
            corners['bottom_right'],
            corners['bottom_left']
        ], dtype="float32")
        
        print(f"Loaded frame coordinates:")
        print(f"  Top-left: {corners['top_left']}")
        print(f"  Top-right: {corners['top_right']}")
        print(f"  Bottom-right: {corners['bottom_right']}")
        print(f"  Bottom-left: {corners['bottom_left']}")
        
        return coords
        
    except FileNotFoundError:
        print(f"Frame coordinates file '{json_file}' not found!")
        print("Please run interactive_frame_selector.py first to select frame coordinates.")
        return None
    except Exception as e:
        print(f"Error loading frame coordinates: {e}")
        return None

def apply_art_to_frame(art_image_path, frame_corners, background_image, output_path):
    """Apply art image to the selected frame area"""
    try:
        # Load the art image
        art_img = cv2.imread(art_image_path)
        if art_img is None:
            print(f"Could not load art image: {art_image_path}")
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
        print(f"✓ Created: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {art_image_path}: {e}")
        return False

def batch_process_art_images(art_folder="art", output_folder="output", frame_image="frame.jpg", frame_coords_file="frame_coordinates.json"):
    """Process all art images in the art folder"""
    
    # Load frame coordinates
    frame_corners = load_frame_coordinates(frame_coords_file)
    if frame_corners is None:
        return
    
    # Load background frame image
    background = cv2.imread(frame_image)
    if background is None:
        print(f"Could not load frame image: {frame_image}")
        return
    
    # Create directories
    os.makedirs(art_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Supported image extensions
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Find all art images
    art_folder_path = Path(art_folder)
    art_images = []
    
    for ext in supported_extensions:
        art_images.extend(art_folder_path.glob(f"*{ext}"))
        art_images.extend(art_folder_path.glob(f"*{ext.upper()}"))
    
    if not art_images:
        print(f"No art images found in '{art_folder}' folder!")
        print(f"Please add some images (.jpg, .png, etc.) to the '{art_folder}' folder.")
        return
    
    print(f"Found {len(art_images)} art images to process...")
    print(f"Using frame coordinates from: {frame_coords_file}")
    print(f"Background frame: {frame_image}")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    # Process each art image
    for art_path in art_images:
        # Create output filename
        output_filename = f"framed_{art_path.name}"
        output_path = Path(output_folder) / output_filename
        
        # Apply art to frame
        if apply_art_to_frame(str(art_path), frame_corners, background, str(output_path)):
            successful += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Processing complete!")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"Results saved in: {output_folder}/")

def preview_single_image(art_image_path, frame_coords_file="frame_coordinates.json", frame_image="frame.jpg"):
    """Preview a single art image with frame (useful for testing)"""
    
    frame_corners = load_frame_coordinates(frame_coords_file)
    if frame_corners is None:
        return
    
    background = cv2.imread(frame_image)
    if background is None:
        print(f"Could not load frame image: {frame_image}")
        return
    
    # Create preview
    preview_path = "preview_result.jpg"
    if apply_art_to_frame(art_image_path, frame_corners, background, preview_path):
        print(f"Preview created: {preview_path}")
        
        # Show the result
        result = cv2.imread(preview_path)
        if result is not None:
            # Resize for display if too large
            height, width = result.shape[:2]
            if width > 1200 or height > 900:
                scale = min(1200/width, 900/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                result = cv2.resize(result, (new_width, new_height))
            
            cv2.imshow("Preview Result", result)
            print("Press any key to close preview...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🎨 Batch Art Frame Processor")
    print("=" * 40)
    
    # Check if frame coordinates exist
    if not os.path.exists("frame_coordinates.json"):
        print("⚠️  No frame coordinates found!")
        print("Please run: python interactive_frame_selector.py frame.jpg")
        print("to select frame coordinates first.")
        exit()
    
    # Check if frame image exists
    if not os.path.exists("frame.jpg"):
        print("⚠️  Frame image 'frame.jpg' not found!")
        exit()
    
    print("Choose an option:")
    print("1. Process all images in 'art' folder")
    print("2. Preview single image")
    print("3. Just create folders and exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        batch_process_art_images()
    elif choice == "2":
        # Create art folder if it doesn't exist
        os.makedirs("art", exist_ok=True)
        
        # List available images in art folder
        art_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            art_files.extend(Path("art").glob(f"*{ext}"))
            art_files.extend(Path("art").glob(f"*{ext.upper()}"))
        
        if not art_files:
            print("No images found in 'art' folder. Please add some images first.")
        else:
            print("Available art images:")
            for i, f in enumerate(art_files, 1):
                print(f"  {i}. {f.name}")
            
            try:
                img_choice = int(input("Select image number: ")) - 1
                if 0 <= img_choice < len(art_files):
                    preview_single_image(str(art_files[img_choice]))
                else:
                    print("Invalid selection")
            except ValueError:
                print("Please enter a valid number")
    
    elif choice == "3":
        os.makedirs("art", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        print("Created folders:")
        print("📁 art/ - Put your artwork images here")
        print("📁 output/ - Framed results will be saved here")
    
    else:
        print("Invalid choice")