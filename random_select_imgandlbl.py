import os
import shutil
import random
from tqdm import tqdm
import argparse


def random_pick_images_and_labels(images_folder, labels_folder, output_folder, ratio):
    # Ensure output folders exist
    output_images_folder = os.path.join(output_folder, "images")
    output_labels_folder = os.path.join(output_folder, "labels")
    os.makedirs(output_images_folder, exist_ok=True)
    os.makedirs(output_labels_folder, exist_ok=True)

    # Get all image filenames
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(".jpg")]

    # Shuffle and calculate number of files to pick
    total_files = len(image_files)
    num_to_pick = int(total_files * ratio)
    random.shuffle(image_files)
    selected_files = image_files[:num_to_pick]

    # Copy selected images and corresponding labels
    copied_count = 0
    for file in tqdm(selected_files, desc="Copying files"):
        image_src = os.path.join(images_folder, file)
        label_src = os.path.join(labels_folder, os.path.splitext(file)[0] + ".txt")

        # Ensure both image and label exist
        if os.path.exists(image_src) and os.path.exists(label_src):
            shutil.copy(image_src, os.path.join(output_images_folder, file))
            shutil.copy(label_src, os.path.join(output_labels_folder, os.path.splitext(file)[0] + ".txt"))
            copied_count += 1

    return copied_count


def main():
    parser = argparse.ArgumentParser(description="Randomly pick images and labels based on a ratio.")
    parser.add_argument("images_folder", help="Path to the folder containing images.")
    parser.add_argument("labels_folder", help="Path to the folder containing labels.")
    parser.add_argument("output_folder",
                        help="Path to the output folder where selected images and labels will be copied.")
    parser.add_argument("ratio", type=float, help="Ratio of images and labels to pick (e.g., 0.2 for 20%).")

    args = parser.parse_args()

    # Call the function and print the number of files copied
    copied_count = random_pick_images_and_labels(args.images_folder, args.labels_folder, args.output_folder, args.ratio)
    print(f"\nTotal files copied to '{args.output_folder}': {copied_count}")


if __name__ == "__main__":
    main()
