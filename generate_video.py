import cv2
import os

def create_video_from_images(image_folder, output_path, fps=30):
    images = []
    # Get all files in the folder sorted by name
    files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    if not files:
        raise ValueError(f"No image files found in {image_folder}")
    
    # Read first image to get dimensions
    first_image = cv2.imread(os.path.join(image_folder, files[0]))
    height, width, _ = first_image.shape
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Add all images to video
    for filename in files:
        img_path = os.path.join(image_folder, filename)
        frame = cv2.imread(img_path)
        if frame is not None:
            out.write(frame)
    
    out.release()

if __name__ == "__main__":
    # Example usage
    image_folder = "/workspace/Shi_recon/pulling_images"
    output_path = "/workspace/Shi_recon/pulling_video.mp4"
    create_video_from_images(image_folder, output_path)
