import os
import shutil
from tqdm import tqdm
import argparse


def combine_folders(root_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all sub-folders in the root directory
    subfolders = [os.path.join(root_folder, folder) for folder in os.listdir(root_folder)
                  if os.path.isdir(os.path.join(root_folder, folder))]

    # Iterate through sub-folders
    for subfolder in tqdm(subfolders, desc="Processing sub-folders"):
        # Get all jpg images in the current sub-folder
        images = [file for file in os.listdir(subfolder) if file.lower().endswith(".jpg")]

        for image in images:
            src_path = os.path.join(subfolder, image)
            dest_path = os.path.join(output_folder, image)

            # Ensure unique filenames in the output folder
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(image)
                dest_path = os.path.join(output_folder, f"{name}_{counter}{ext}")
                counter += 1

            # Copy the file to the output folder
            shutil.copy(src_path, dest_path)


def main():
    parser = argparse.ArgumentParser(description="Combine sub-folders with JPG images into one folder.")
    parser.add_argument("root_folder", help="Path to the root folder containing sub-folders.")
    parser.add_argument("output_folder", help="Path to the output folder where images will be combined.")

    args = parser.parse_args()

    combine_folders(args.root_folder, args.output_folder)


if __name__ == "__main__":
    main()
