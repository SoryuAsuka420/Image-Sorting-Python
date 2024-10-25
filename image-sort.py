#Install Pillow library with: pip install pillow
#!/usr/bin/env python3
import os
from pathlib import Path
from PIL import Image, ExifTags
from shutil import move
from datetime import datetime

# Function to prompt for a valid folder path
def get_valid_folder_path(prompt_message):
    while True:
        folder_path = Path(input(prompt_message).strip())
        if folder_path.exists() and folder_path.is_dir():
            return folder_path
        else:
            print(f"Error: '{folder_path}' is not a valid directory. Please try again.")

# Prompt for valid source and destination folder paths
source_folder = get_valid_folder_path("Enter the path to the source folder containing images: ")
destination_folder = get_valid_folder_path("Enter the path to the destination folder for sorted images: ")

# Make sure destination folder exists
destination_folder.mkdir(parents=True, exist_ok=True)

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {".png", ".jpeg", ".jpg", ".gif"}

# Lists to keep track of moved and ignored files
moved_files = []
ignored_files = []

# Path for the log file
log_file_path = Path(__file__).parent / "log.txt"

# Clear log file at the beginning of each run
with open(log_file_path, "w") as log_file:
    log_file.write("File Move Log\n")
    log_file.write("=" * 50 + "\n")

# Helper function to extract EXIF metadata
def get_exif_data(image):
    exif_data = {}
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                exif_data[decoded] = value
    return exif_data

# Helper function to find the closest aspect ratio category
def get_aspect_ratio_category(aspect_ratio, orientation):
    # Define standard aspect ratios for landscape and portrait
    landscape_ratios = {'16:9': 16/9, '4:3': 4/3}
    portrait_ratios = {'9:16': 9/16, '3:4': 3/4}
    
    # Select appropriate ratio set based on orientation
    ratios = landscape_ratios if orientation == "Landscape" else portrait_ratios
    
    # Find the closest standard ratio
    closest_category = min(ratios, key=lambda k: abs(aspect_ratio - ratios[k]))
    return closest_category

# Helper function to categorize images by orientation and closest aspect ratio
def categorize_image(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        aspect_ratio = width / height
        
        # Determine orientation
        orientation = "Landscape" if width >= height else "Portrait"
        
        # Determine the closest aspect ratio category
        aspect_category = get_aspect_ratio_category(aspect_ratio, orientation)
        
        exif_data = get_exif_data(img)
        return orientation, aspect_category, exif_data

# Helper function to get the next available numerical filename in the target folder
def get_next_filename(target_folder, extension):
    existing_files = list(target_folder.glob(f"*.{extension}"))
    next_number = len(existing_files) + 1
    return target_folder / f"{next_number}.{extension}"

# Main function to sort images by aspect ratio, rename them, and provide a summary report
def sort_and_rename_images():
    with open(log_file_path, "a") as log_file:  # Open log file in append mode after clearing
        for image_path in source_folder.iterdir():
            # Only process files with allowed image extensions
            if image_path.suffix.lower() in ALLOWED_EXTENSIONS:
                orientation, aspect_category, exif_data = categorize_image(image_path)
                
                # Define destination based on orientation and closest aspect ratio category
                target_folder = destination_folder / orientation / aspect_category
                target_folder.mkdir(parents=True, exist_ok=True)
                
                # Get the file extension to preserve it
                extension = image_path.suffix.lstrip(".").lower()
                
                # Determine the next filename in the sequence
                next_filename = get_next_filename(target_folder, extension)
                
                # Move and rename the image to the categorized folder with the new name
                move(image_path, next_filename)
                moved_files.append(next_filename.name)
                print(f"Moved {image_path.name} to {next_filename}")
                
                # Log details of the file move with timestamp, organized as requested
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp} | Original Path: {image_path} | New Path: {next_filename} | "
                               f"Original Name: {image_path.name} | New Name: {next_filename.name}\n")
            else:
                ignored_files.append(image_path.name)

    # Summary Report
    print("\nSummary Report")
    print("=" * 20)
    print(f"Total files moved: {len(moved_files)}")
    print("Moved files:", moved_files)
    print(f"\nTotal files ignored: {len(ignored_files)}")
    print("Ignored files:", ignored_files)

# Run the function
sort_and_rename_images()
