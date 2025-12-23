import cv2
import numpy as np

def find_frame_corners(image_path, min_area_ratio=0.05, debug=False):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    img_area = img.shape[0] * img.shape[1]
    min_area = int(img_area * min_area_ratio)
    
    print(f"Image dimensions: {img.shape}")
    print(f"Looking for frame with min area: {min_area} ({min_area_ratio*100:.1f}% of image)")
    
    # Save debug images if requested
    debug_dir = "debug_images"
    if debug:
        import os
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        cv2.imwrite(f"{debug_dir}/01_original.jpg", original)
        cv2.imwrite(f"{debug_dir}/02_grayscale.jpg", gray)
    
    # Multiple preprocessing approaches specifically for picture frames
    preprocessing_methods = [
        # Method 1: Standard Canny with moderate thresholds
        ("Standard_Canny", lambda g: cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 50, 150)),
        
        # Method 2: High contrast Canny for strong edges (frame borders)
        ("High_Contrast", lambda g: cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 100, 200)),
        
        # Method 3: Low threshold Canny for subtle edges
        ("Low_Threshold", lambda g: cv2.Canny(cv2.GaussianBlur(g, (7, 7), 0), 20, 60)),
        
        # Method 4: Adaptive threshold for varying lighting
        ("Adaptive_Thresh", lambda g: cv2.adaptiveThreshold(
            cv2.GaussianBlur(g, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
        
        # Method 5: Morphological gradient to detect edges
        ("Morphological", lambda g: cv2.morphologyEx(g, cv2.MORPH_GRADIENT, np.ones((3,3), np.uint8)))
    ]
    
    all_candidates = []
    
    for method_name, preprocess_func in preprocessing_methods:
        print(f"\n--- Processing with {method_name} ---")
        
        # Apply preprocessing
        processed = preprocess_func(gray)
        
        # Additional morphological operations to connect broken edges
        if method_name != "Adaptive_Thresh":  # Skip morphology for threshold methods
            kernel = np.ones((2,2), np.uint8)
            processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
            processed = cv2.dilate(processed, kernel, iterations=1)
        
        if debug:
            cv2.imwrite(f"{debug_dir}/03_{method_name}_processed.jpg", processed)
        
        # Find contours - try both RETR_EXTERNAL and RETR_TREE to catch inner frames
        for retr_mode, mode_name in [(cv2.RETR_EXTERNAL, "external"), (cv2.RETR_TREE, "tree")]:
            contours, hierarchy = cv2.findContours(processed, retr_mode, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"  {mode_name}: Found {len(contours)} contours")
            
            # Sort by area
            contour_areas = [(i, cv2.contourArea(cnt)) for i, cnt in enumerate(contours)]
            contour_areas.sort(key=lambda x: x[1], reverse=True)
            
            # Test different approximation strategies
            for idx, (cont_idx, area) in enumerate(contour_areas[:15]):  # Check top 15 contours
                if area < min_area:
                    continue
                
                cnt = contours[cont_idx]
                
                # Calculate perimeter
                peri = cv2.arcLength(cnt, True)
                if peri == 0:
                    continue
                
                # Try multiple epsilon values for polygon approximation
                epsilon_ratios = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.08, 0.1]
                
                for epsilon_ratio in epsilon_ratios:
                    epsilon = epsilon_ratio * peri
                    approx = cv2.approxPolyDP(cnt, epsilon, True)
                    
                    # Look for 4-sided polygons (quadrilaterals)
                    if len(approx) == 4:
                        # Calculate properties
                        hull = cv2.convexHull(cnt)
                        hull_area = cv2.contourArea(hull)
                        solidity = area / hull_area if hull_area > 0 else 0
                        
                        # Calculate aspect ratio to filter out very thin shapes
                        rect = cv2.boundingRect(approx)
                        aspect_ratio = rect[2] / rect[3] if rect[3] > 0 else 0
                        
                        # Check if this looks like a reasonable frame
                        is_valid_frame = (
                            solidity > 0.6 and  # Not too jagged
                            0.3 < aspect_ratio < 3.0 and  # Reasonable aspect ratio
                            area > min_area  # Large enough
                        )
                        
                        if is_valid_frame:
                            # Calculate center distance from image center (frames are usually central)
                            img_center = np.array([img.shape[1]/2, img.shape[0]/2])
                            frame_center = np.mean(approx.reshape(-1, 2), axis=0)
                            center_distance = np.linalg.norm(frame_center - img_center)
                            center_score = 1.0 / (1.0 + center_distance / 100)  # Preference for central frames
                            
                            candidate = {
                                'corners': approx,
                                'area': area,
                                'solidity': solidity,
                                'aspect_ratio': aspect_ratio,
                                'center_score': center_score,
                                'method': method_name,
                                'mode': mode_name,
                                'epsilon_ratio': epsilon_ratio,
                                'score': area * solidity * center_score  # Combined score
                            }
                            
                            all_candidates.append(candidate)
                            
                            print(f"    Found candidate #{len(all_candidates)}: area={area:.0f}, "
                                  f"solidity={solidity:.3f}, aspect={aspect_ratio:.2f}, "
                                  f"center_score={center_score:.3f}")
                            
                            # Save debug image for this candidate
                            if debug:
                                temp_img = original.copy()
                                cv2.drawContours(temp_img, [approx], -1, (0, 255, 0), 3)
                                for j, corner in enumerate(approx.reshape(-1, 2)):
                                    cv2.circle(temp_img, tuple(corner), 8, (255, 0, 0), -1)
                                    cv2.putText(temp_img, str(j), tuple(corner + 15), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                                
                                cv2.putText(temp_img, f"Area: {area:.0f}", (10, 30), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                cv2.putText(temp_img, f"Solidity: {solidity:.3f}", (10, 60), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                
                                cv2.imwrite(f"{debug_dir}/candidate_{len(all_candidates):02d}_{method_name}_{mode_name}.jpg", temp_img)
    
    if not all_candidates:
        print(f"\nNo frame candidates found!")
        print(f"Tried {len(preprocessing_methods)} preprocessing methods")
        print(f"Minimum area threshold: {min_area}")
        print("Try reducing min_area_ratio parameter")
        
        if debug:
            print(f"Debug images saved to {debug_dir}/")
        
        raise ValueError(f"No suitable frame found! Try min_area_ratio < {min_area_ratio}")
    
    # Sort candidates by combined score (area * solidity * center_score)
    all_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\nFound {len(all_candidates)} total candidates")
    print("Top 3 candidates:")
    for i, candidate in enumerate(all_candidates[:3]):
        print(f"  {i+1}. Score: {candidate['score']:.0f}, Area: {candidate['area']:.0f}, "
              f"Solidity: {candidate['solidity']:.3f}, Method: {candidate['method']}")
    
    # Select the best candidate
    best_candidate = all_candidates[0]
    
    print(f"\nSelected best candidate:")
    print(f"- Method: {best_candidate['method']} ({best_candidate['mode']})")
    print(f"- Area: {best_candidate['area']:.0f}")
    print(f"- Solidity: {best_candidate['solidity']:.3f}")
    print(f"- Aspect ratio: {best_candidate['aspect_ratio']:.2f}")
    print(f"- Center score: {best_candidate['center_score']:.3f}")
    print(f"- Combined score: {best_candidate['score']:.0f}")
    
    if debug:
        # Save final result
        result_img = original.copy()
        cv2.drawContours(result_img, [best_candidate['corners']], -1, (0, 255, 0), 4)
        for j, corner in enumerate(best_candidate['corners'].reshape(-1, 2)):
            cv2.circle(result_img, tuple(corner), 10, (255, 0, 0), -1)
            cv2.putText(result_img, str(j), tuple(corner + 20), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
        cv2.imwrite(f"{debug_dir}/99_final_result.jpg", result_img)
        print(f"Debug images saved to {debug_dir}/")
    
    return best_candidate['corners'], original

def paste_image_inside_frame(background_path, insert_image_path, output_path="result.jpg", min_area_ratio=0.05, debug=False):
    # Find frame corners
    corners, bg = find_frame_corners(background_path, min_area_ratio=min_area_ratio, debug=debug)

    # Load the image you want to insert
    insert = cv2.imread(insert_image_path)

    # Handle different numbers of vertices
    corners = corners.reshape(-1, 2).astype(np.float32)
    
    if len(corners) == 4:
        # Standard quadrilateral processing
        # Order corners properly for perspective transform
        rect = np.zeros((4, 2), dtype="float32")
        s = corners.sum(axis=1)
        diff = np.diff(corners, axis=1)
        
        rect[0] = corners[np.argmin(s)]      # top-left
        rect[2] = corners[np.argmax(s)]      # bottom-right
        rect[1] = corners[np.argmin(diff)]   # top-right
        rect[3] = corners[np.argmax(diff)]   # bottom-left
        
        # Calculate width and height
        width = max(
            int(np.linalg.norm(rect[0] - rect[1])),
            int(np.linalg.norm(rect[2] - rect[3]))
        )
        height = max(
            int(np.linalg.norm(rect[1] - rect[2])),
            int(np.linalg.norm(rect[3] - rect[0]))
        )
        
        # Destination points (perfect rectangle)
        dst_points = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype="float32")
        
        # Source points from insert image
        src_points = np.array([[0, 0], [insert.shape[1]-1, 0], [insert.shape[1]-1, insert.shape[0]-1], [0, insert.shape[0]-1]], dtype="float32")
        
        # Get transform matrix
        M_rect_to_quad = cv2.getPerspectiveTransform(dst_points, rect)
        M_src_to_quad = cv2.getPerspectiveTransform(src_points, rect)
        
        # Warp insert image to fit the detected quadrilateral
        warped = cv2.warpPerspective(insert, M_src_to_quad, (bg.shape[1], bg.shape[0]))
        
        # Create mask
        mask = np.zeros(bg.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(rect), 255)
        
    else:
        # For non-quadrilateral shapes, use a simpler approach
        # Create bounding rectangle
        x, y, w, h = cv2.boundingRect(corners.astype(np.int32))
        
        # Resize insert image to fit bounding rectangle
        resized_insert = cv2.resize(insert, (w, h))
        
        # Create mask for the polygon
        mask = np.zeros(bg.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(corners), 255)
        
        # Create warped image
        warped = bg.copy()
        warped[y:y+h, x:x+w] = resized_insert
    
    # Apply the mask to combine images
    result = bg.copy()
    result[mask > 0] = warped[mask > 0]
    
    # Save intermediate results for debugging
    cv2.imwrite("debug_mask.jpg", mask)
    cv2.imwrite("debug_warped.jpg", warped)

    cv2.imwrite(output_path, result)
    print(f"saved to {output_path}")

    # Optional: show corners on original
    cv2.drawContours(bg, [np.int32(corners)], -1, (0, 255, 0), 3)
    for i, corner in enumerate(corners):
        x, y = corner.ravel().astype(int)
        cv2.putText(bg, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Detected Frame Corners", bg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============== USAGE ==============
# Detect the picture frame in the center of the image
paste_image_inside_frame(
    background_path="frame.jpg",        # your photo with empty frame
    insert_image_path="content.png",    # image you want to put inside
    output_path="final_result.jpg",
    min_area_ratio=0.005,              # 0.5% of image area - very permissive for clear frames
    debug=True                         # Enable debug mode to see processing steps
)