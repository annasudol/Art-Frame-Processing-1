import cv2
import numpy as np
import json
import os

class FrameSelector:
    def __init__(self):
        self.points = []
        self.img = None
        self.original_img = None
        self.window_name = "Frame Selection - Click 4 corners in order: Top-Left, Top-Right, Bottom-Right, Bottom-Left"
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 4:
                self.points.append([x, y])
                print(f"Point {len(self.points)}: ({x}, {y})")
                
                # Draw the point
                cv2.circle(self.img, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(self.img, str(len(self.points)), (x+10, y-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # If we have more than 1 point, draw lines
                if len(self.points) > 1:
                    cv2.line(self.img, tuple(self.points[-2]), tuple(self.points[-1]), (0, 255, 0), 2)
                
                # If we have 4 points, complete the quadrilateral
                if len(self.points) == 4:
                    cv2.line(self.img, tuple(self.points[3]), tuple(self.points[0]), (0, 255, 0), 2)
                    cv2.fillPoly(self.img, [np.array(self.points)], (0, 255, 0, 50))  # Semi-transparent fill
                
                cv2.imshow(self.window_name, self.img)
                
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click to reset
            self.reset_selection()
    
    def reset_selection(self):
        self.points = []
        self.img = self.original_img.copy()
        cv2.imshow(self.window_name, self.img)
        print("Selection reset. Click 4 corners again.")
    
    def select_frame(self, image_path):
        """Interactive frame selection"""
        self.original_img = cv2.imread(image_path)
        if self.original_img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Resize if image is too large
        height, width = self.original_img.shape[:2]
        max_dimension = 1000
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            display_img = cv2.resize(self.original_img, (new_width, new_height))
            self.scale_factor = scale
        else:
            display_img = self.original_img.copy()
            self.scale_factor = 1.0
        
        self.img = display_img.copy()
        
        # Instructions
        print("\n" + "="*60)
        print("FRAME SELECTION INSTRUCTIONS:")
        print("1. Click 4 corners in this order:")
        print("   - Top-Left corner")
        print("   - Top-Right corner") 
        print("   - Bottom-Right corner")
        print("   - Bottom-Left corner")
        print("2. Right-click to reset selection")
        print("3. Press 's' to save when done")
        print("4. Press 'q' to quit without saving")
        print("="*60)
        
        cv2.imshow(self.window_name, self.img)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s') and len(self.points) == 4:
                # Save the selection
                # Scale points back to original image size
                original_points = [[int(p[0] / self.scale_factor), int(p[1] / self.scale_factor)] 
                                 for p in self.points]
                
                frame_data = {
                    'image_path': image_path,
                    'image_dimensions': [self.original_img.shape[1], self.original_img.shape[0]],  # [width, height]
                    'frame_corners': original_points,
                    'corners_order': ['top-left', 'top-right', 'bottom-right', 'bottom-left']
                }
                
                # Save to JSON file
                config_path = 'frame_config.json'
                with open(config_path, 'w') as f:
                    json.dump(frame_data, f, indent=4)
                
                print(f"\nFrame configuration saved to: {config_path}")
                print("Original image coordinates:", original_points)
                break
                
            elif key == ord('q'):
                print("Exiting without saving.")
                break
                
            elif key == ord('r'):
                # Reset selection
                self.reset_selection()
        
        cv2.destroyAllWindows()
        return len(self.points) == 4

def apply_frame_to_image(insert_image_path, output_path="result_manual.jpg", config_path="frame_config.json"):
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
    
    print(f"Using saved frame corners: {corners.tolist()}")
    
    # Calculate the size of the frame area
    width = int(max(
        np.linalg.norm(corners[1] - corners[0]),  # top edge
        np.linalg.norm(corners[2] - corners[3])   # bottom edge
    ))
    height = int(max(
        np.linalg.norm(corners[3] - corners[0]),  # left edge
        np.linalg.norm(corners[2] - corners[1])   # right edge
    ))
    
    print(f"Frame dimensions: {width} x {height}")
    
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
    
    # Show result
    # Resize for display if too large
    display_result = result.copy()
    if max(result.shape[:2]) > 800:
        scale = 800 / max(result.shape[:2])
        new_width = int(result.shape[1] * scale)
        new_height = int(result.shape[0] * scale)
        display_result = cv2.resize(result, (new_width, new_height))
    
    cv2.imshow("Final Result", display_result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return output_path

def main():
    """Main function with menu options"""
    while True:
        print("\n" + "="*50)
        print("MANUAL FRAME SELECTOR")
        print("="*50)
        print("1. Select frame corners manually")
        print("2. Apply saved frame to new image") 
        print("3. View saved frame configuration")
        print("4. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            frame_image = input("Enter path to frame image (or press Enter for 'frame.jpg'): ").strip()
            if not frame_image:
                frame_image = "frame.jpg"
            
            if not os.path.exists(frame_image):
                print(f"Image not found: {frame_image}")
                continue
            
            selector = FrameSelector()
            try:
                success = selector.select_frame(frame_image)
                if success:
                    print("Frame selection completed and saved!")
                else:
                    print("Frame selection cancelled.")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '2':
            if not os.path.exists("frame_config.json"):
                print("No saved frame configuration found. Please select a frame first.")
                continue
            
            insert_image = input("Enter path to image to insert (or press Enter for 'content.png'): ").strip()
            if not insert_image:
                insert_image = "content.png"
            
            if not os.path.exists(insert_image):
                print(f"Insert image not found: {insert_image}")
                continue
            
            output_name = input("Enter output filename (or press Enter for 'result_manual.jpg'): ").strip()
            if not output_name:
                output_name = "result_manual.jpg"
            
            try:
                apply_frame_to_image(insert_image, output_name)
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            if os.path.exists("frame_config.json"):
                with open("frame_config.json", 'r') as f:
                    config = json.load(f)
                print("\nSaved Frame Configuration:")
                print(json.dumps(config, indent=2))
            else:
                print("No saved configuration found.")
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()