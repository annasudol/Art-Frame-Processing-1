import cv2
import numpy as np
import json

class InteractiveFrameSelector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        self.display_image = self.image.copy()
        self.corners = []
        self.window_name = "Select Frame Corners - Click 4 corners in order: Top-Left, Top-Right, Bottom-Right, Bottom-Left"
        
        # Resize image if too large for display
        height, width = self.image.shape[:2]
        max_size = 800
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
            self.scale_factor = scale
        else:
            self.scale_factor = 1.0
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.corners) < 4:
                # Convert display coordinates back to original image coordinates
                orig_x = int(x / self.scale_factor)
                orig_y = int(y / self.scale_factor)
                
                self.corners.append((orig_x, orig_y))
                
                # Draw point on display image
                cv2.circle(self.display_image, (x, y), 8, (0, 255, 0), -1)
                cv2.putText(self.display_image, str(len(self.corners)), 
                           (x + 15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                print(f"Corner {len(self.corners)}: ({orig_x}, {orig_y})")
                
                # Draw lines between points
                if len(self.corners) > 1:
                    # Scale corners for display
                    display_corners = [(int(cx * self.scale_factor), int(cy * self.scale_factor)) 
                                     for cx, cy in self.corners]
                    
                    # Draw line to previous point
                    cv2.line(self.display_image, display_corners[-2], display_corners[-1], 
                            (255, 0, 0), 2)
                    
                    # If we have 4 points, close the quadrilateral
                    if len(self.corners) == 4:
                        cv2.line(self.display_image, display_corners[-1], display_corners[0], 
                                (255, 0, 0), 2)
                        print("\nFrame selection complete!")
                        print("Press 's' to save, 'r' to reset, or 'q' to quit")
                
                cv2.imshow(self.window_name, self.display_image)
            
            elif len(self.corners) == 4:
                print("Already selected 4 corners. Press 'r' to reset or 's' to save.")
    
    def reset_selection(self):
        """Reset the corner selection"""
        self.corners = []
        self.display_image = self.image.copy()
        
        # Apply scaling if needed
        if self.scale_factor != 1.0:
            height, width = self.image.shape[:2]
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            self.display_image = cv2.resize(self.display_image, (new_width, new_height))
        
        print("Selection reset. Click 4 corners in order:")
        print("1. Top-Left")
        print("2. Top-Right") 
        print("3. Bottom-Right")
        print("4. Bottom-Left")
        cv2.imshow(self.window_name, self.display_image)
    
    def save_frame_data(self, output_file="frame_coordinates.json"):
        """Save the frame coordinates and image info to a JSON file"""
        if len(self.corners) != 4:
            print("Error: Need exactly 4 corners selected")
            return False
        
        frame_data = {
            "image_path": self.image_path,
            "image_dimensions": {
                "width": self.image.shape[1],
                "height": self.image.shape[0]
            },
            "corners": {
                "top_left": self.corners[0],
                "top_right": self.corners[1], 
                "bottom_right": self.corners[2],
                "bottom_left": self.corners[3]
            },
            "corners_array": self.corners
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(frame_data, f, indent=2)
            print(f"Frame coordinates saved to {output_file}")
            
            # Also save a visual representation
            visual_path = output_file.replace('.json', '_visual.jpg')
            self.save_visual_representation(visual_path)
            
            return True
        except Exception as e:
            print(f"Error saving frame data: {e}")
            return False
    
    def save_visual_representation(self, output_path):
        """Save an image showing the selected frame"""
        visual = self.image.copy()
        
        # Draw the selected quadrilateral
        corners_np = np.array(self.corners, dtype=np.int32)
        cv2.polylines(visual, [corners_np], True, (0, 255, 0), 3)
        
        # Draw corner points and labels
        labels = ["TL", "TR", "BR", "BL"]
        for i, (corner, label) in enumerate(zip(self.corners, labels)):
            cv2.circle(visual, corner, 10, (0, 255, 0), -1)
            cv2.putText(visual, f"{i+1}:{label}", 
                       (corner[0] + 15, corner[1] - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, visual)
        print(f"Visual representation saved to {output_path}")
    
    def run(self):
        """Main interactive loop"""
        print("=== Interactive Frame Selector ===")
        print("Instructions:")
        print("1. Click 4 corners of the frame in this order:")
        print("   - Top-Left corner")
        print("   - Top-Right corner")
        print("   - Bottom-Right corner")
        print("   - Bottom-Left corner")
        print("\nKeyboard commands:")
        print("- 's': Save coordinates")
        print("- 'r': Reset selection")
        print("- 'q': Quit without saving")
        print("\nClick on the image to start selecting corners...")
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        cv2.imshow(self.window_name, self.display_image)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Quitting without saving...")
                break
            elif key == ord('r'):
                self.reset_selection()
            elif key == ord('s'):
                if len(self.corners) == 4:
                    if self.save_frame_data():
                        print("Frame data saved successfully!")
                        break
                else:
                    print(f"Need 4 corners, currently have {len(self.corners)}")
            elif key == 27:  # ESC key
                print("Quitting without saving...")
                break
        
        cv2.destroyAllWindows()
        return len(self.corners) == 4

def apply_saved_frame(frame_json_path, insert_image_path, output_path="result_with_saved_frame.jpg"):
    """Apply a previously saved frame to insert a new image"""
    
    try:
        # Load frame data
        with open(frame_json_path, 'r') as f:
            frame_data = json.load(f)
        
        # Load the original frame image
        frame_image = cv2.imread(frame_data['image_path'])
        if frame_image is None:
            raise ValueError(f"Could not load frame image: {frame_data['image_path']}")
        
        # Load the insert image
        insert_image = cv2.imread(insert_image_path)
        if insert_image is None:
            raise ValueError(f"Could not load insert image: {insert_image_path}")
        
        # Get the saved corners
        corners = np.array(frame_data['corners_array'], dtype=np.float32)
        
        # Create source points (corners of the insert image)
        h, w = insert_image.shape[:2]
        src_points = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], dtype=np.float32)
        
        # Compute perspective transform
        M = cv2.getPerspectiveTransform(src_points, corners)
        
        # Warp the insert image to fit the frame
        warped = cv2.warpPerspective(insert_image, M, (frame_image.shape[1], frame_image.shape[0]))
        
        # Create mask for the frame area
        mask = np.zeros(frame_image.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(corners), 255)
        
        # Combine images
        result = frame_image.copy()
        result[mask > 0] = warped[mask > 0]
        
        # Save result
        cv2.imwrite(output_path, result)
        print(f"Result saved to {output_path}")
        
        # Show result
        cv2.imshow("Result", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True
        
    except Exception as e:
        print(f"Error applying saved frame: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Select frame: python interactive_frame_selector.py frame.jpg")
        print("  Apply saved frame: python interactive_frame_selector.py apply frame_coordinates.json insert_image.jpg")
        sys.exit(1)
    
    if sys.argv[1] == "apply" and len(sys.argv) >= 4:
        # Apply saved frame mode
        frame_json = sys.argv[2]
        insert_image = sys.argv[3]
        output_file = sys.argv[4] if len(sys.argv) > 4 else "result_with_saved_frame.jpg"
        
        success = apply_saved_frame(frame_json, insert_image, output_file)
        if success:
            print("Successfully applied saved frame!")
        else:
            print("Failed to apply saved frame!")
    else:
        # Interactive selection mode
        image_path = sys.argv[1]
        
        try:
            selector = InteractiveFrameSelector(image_path)
            selector.run()
        except Exception as e:
            print(f"Error: {e}")