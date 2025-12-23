#!/usr/bin/env python3
"""
Quick script to apply saved frame configuration to a new image
Usage: python apply_frame.py input_image.jpg output_image.jpg
"""

import cv2
import numpy as np
import json
import sys
import os

def apply_saved_frame(insert_image_path, output_path, config_path="frame_config.json"):
    """Apply saved frame configuration to insert an image"""
    
    # Load frame configuration
    if not os.path.exists(config_path):
        raise ValueError(f"Frame configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        frame_data = json.load(f)
    
    # Load background image
    bg_path = frame_data['image_path']
    bg = cv2.imread(bg_path)
    if bg is None:
        raise ValueError(f"Could not load background image: {bg_path}")
    
    # Load insert image
    insert = cv2.imread(insert_image_path)
    if insert is None:
        raise ValueError(f"Could not load insert image: {insert_image_path}")
    
    # Get frame corners
    corners = np.array(frame_data['frame_corners'], dtype="float32")
    
    print(f"Applying frame from: {bg_path}")
    print(f"Insert image: {insert_image_path}")
    print(f"Frame corners: {corners.tolist()}")
    
    # Create source points for the insert image
    src_points = np.array([
        [0, 0],
        [insert.shape[1]-1, 0],
        [insert.shape[1]-1, insert.shape[0]-1],
        [0, insert.shape[0]-1]
    ], dtype="float32")
    
    # Calculate perspective transform
    M = cv2.getPerspectiveTransform(src_points, corners)
    
    # Warp the insert image to fit the frame
    warped = cv2.warpPerspective(insert, M, (bg.shape[1], bg.shape[0]))
    
    # Create mask for the frame area
    mask = np.zeros(bg.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(corners), 255)
    
    # Combine the images
    result = bg.copy()
    result[mask > 0] = warped[mask > 0]
    
    # Save result
    cv2.imwrite(output_path, result)
    print(f"Result saved to: {output_path}")
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply_frame.py <input_image> [output_image]")
        print("Example: python apply_frame.py my_photo.jpg result.jpg")
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_image = sys.argv[2] if len(sys.argv) > 2 else "framed_result.jpg"
    
    if not os.path.exists(input_image):
        print(f"Input image not found: {input_image}")
        sys.exit(1)
    
    try:
        result_path = apply_saved_frame(input_image, output_image)
        print(f"Success! Check your result at: {result_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)