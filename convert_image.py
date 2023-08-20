import cv2

# Load the input image
input_image_path = 'Images/20bcs6872.jpg'  # Replace with your input image path
output_image_path = 'Images/20bcs6872.png'  # Replace with desired output image path

# Read the input image
input_image = cv2.imread(input_image_path)

# Define the target resolution
target_resolution = (216, 216)

# Resize the image to the target resolution
resized_image = cv2.resize(input_image, target_resolution)

# Save the resized image
cv2.imwrite(output_image_path, resized_image)

print("Image resized and saved.")
