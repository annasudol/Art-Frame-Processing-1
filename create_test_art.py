import cv2
import numpy as np

# Create a simple test artwork
width, height = 400, 300
img = np.ones((height, width, 3), dtype=np.uint8) * 255

# Add some colorful geometric shapes
cv2.rectangle(img, (50, 50), (150, 150), (255, 0, 0), -1)  # Blue square
cv2.circle(img, (250, 100), 50, (0, 255, 0), -1)  # Green circle
cv2.rectangle(img, (200, 180), (350, 250), (0, 0, 255), -1)  # Red rectangle

# Add some text
cv2.putText(img, "Test Art", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Save to art folder
cv2.imwrite("art/test_artwork.jpg", img)
print("Created test artwork: art/test_artwork.jpg")