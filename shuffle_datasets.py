import os
import shutil
import random
import math
import logging
import argparse
from tqdm import tqdm

# -------------------- Configuration -------------------- #

# Define the batch size
BATCH_SIZE = 500

# Define the names of the images and labels folders within the input directory
IMAGES_FOLDER_NAME = 'images'
LABELS_FOLDER_NAME = 'labels'

# Define image and label file extensions (lowercase)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
LABEL_EXTENSIONS = {'.txt', '.json', '.xml', '.csv'}  # Adjust based on label formats

# -------------------------------------------------------- #

def setup_logging():
    """
    Sets up logging to output to both console and a log file named 'batch_processing.log'.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("batch_processing.log"),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
    - args: Parsed arguments containing input_dir and output_dir.
    """
    parser = argparse.ArgumentParser(description="Batch Image-Label Pair Organizer")

    parser.add_argument(
        'input_dir',
        type=str,
        help='Path to the root input directory containing "images" and "labels" folders.'
    )

    parser.add_argument(
        'output_dir',
        type=str,
        help='Path to the root output directory where batched folders will be created.'
    )

    args = parser.parse_args()
    return args

def collect_image_label_pairs(root_input_dir):
    """
    Traverses the root input directory to find all image-label file pairs.

    Parameters:
    - root_input_dir (str): Path to the root input directory.

    Returns:
    - pairs (list of tuples): Each tuple contains (image_path, label_path).
    """
    pairs = []

    images_dir = os.path.join(root_input_dir, IMAGES_FOLDER_NAME)
    labels_dir = os.path.join(root_input_dir, LABELS_FOLDER_NAME)

    # Verify that images and labels directories exist
    if not os.path.isdir(images_dir):
        logging.error(f"Images directory '{images_dir}' does not exist.")
        return pairs
    if not os.path.isdir(labels_dir):
        logging.error(f"Labels directory '{labels_dir}' does not exist.")
        return pairs

    # Collect image files
    try:
        image_files = os.listdir(images_dir)
    except Exception as e:
        logging.error(f"Error accessing images directory '{images_dir}': {e}")
        return pairs

    image_mapping = {}
    for img_file in image_files:
        img_base, img_ext = os.path.splitext(img_file)
        if img_ext.lower() not in IMAGE_EXTENSIONS:
            continue  # Skip files with unwanted extensions
        image_mapping[img_base] = os.path.join(images_dir, img_file)

    # Collect label files
    try:
        label_files = os.listdir(labels_dir)
    except Exception as e:
        logging.error(f"Error accessing labels directory '{labels_dir}': {e}")
        return pairs

    label_mapping = {}
    for lbl_file in label_files:
        lbl_base, lbl_ext = os.path.splitext(lbl_file)
        if lbl_ext.lower() not in LABEL_EXTENSIONS:
            continue  # Skip files with unwanted extensions
        label_mapping[lbl_base] = os.path.join(labels_dir, lbl_file)

    # Identify common base filenames
    common_bases = set(image_mapping.keys()) & set(label_mapping.keys())
    missing_labels = set(image_mapping.keys()) - set(label_mapping.keys())

    if missing_labels:
        logging.warning(f"{len(missing_labels)} images do not have corresponding labels and will be skipped.")

    for base in common_bases:
        image_path = image_mapping[base]
        label_path = label_mapping[base]
        pairs.append((image_path, label_path))

    logging.info(f"Total image-label pairs found: {len(pairs)}")
    return pairs

def shuffle_and_split_pairs(pairs):
    """
    Shuffles the list of pairs and splits them into batches.

    Parameters:
    - pairs (list of tuples): List containing (image_path, label_path).

    Returns:
    - batches (list of lists): Each sublist contains a batch of (image_path, label_path).
    """
    random.shuffle(pairs)
    total_pairs = len(pairs)
    total_batches = math.ceil(total_pairs / BATCH_SIZE)
    batches = []

    for i in tqdm(range(total_batches), desc="Creating Batches", unit="batch"):
        start_index = i * BATCH_SIZE
        end_index = min(start_index + BATCH_SIZE, total_pairs)
        batch = pairs[start_index:end_index]
        batches.append(batch)
        logging.info(f"Batch {i+1}: Pairs {start_index + 1} to {end_index}")

    logging.info(f"Total batches created: {len(batches)}")
    return batches

def copy_batches_to_folders(batches, output_dir):
    """
    Copies each batch of image-label pairs into separate parent folders with 'images' and 'labels' subfolders.

    Parameters:
    - batches (list of lists): Each sublist contains a batch of (image_path, label_path).
    - output_dir (str): Path to the root output directory.

    Returns:
    - None
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")
        except Exception as e:
            logging.error(f"Failed to create output directory '{output_dir}': {e}")
            return

    for batch_num, batch in enumerate(tqdm(batches, desc="Copying Batches", unit="batch"), start=1):
        batch_folder_name = f"batch_{batch_num}"
        batch_folder_path = os.path.join(output_dir, batch_folder_name)
        images_output_dir = os.path.join(batch_folder_path, IMAGES_FOLDER_NAME)
        labels_output_dir = os.path.join(batch_folder_path, LABELS_FOLDER_NAME)

        try:
            os.makedirs(images_output_dir, exist_ok=True)
            os.makedirs(labels_output_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create batch folders '{images_output_dir}' or '{labels_output_dir}': {e}")
            continue

        logging.info(f"Processing {batch_folder_name} with {len(batch)} pairs.")

        for image_path, label_path in batch:
            try:
                # Determine destination paths
                image_filename = os.path.basename(image_path)
                label_filename = os.path.basename(label_path)

                dest_image_path = os.path.join(images_output_dir, image_filename)
                dest_label_path = os.path.join(labels_output_dir, label_filename)

                # Copy image
                shutil.copy2(image_path, dest_image_path)

                # Copy label
                shutil.copy2(label_path, dest_label_path)

            except Exception as e:
                logging.error(f"Error copying files '{image_path}' and '{label_path}': {e}")

        logging.info(f"Completed {batch_folder_name}")

def main():
    """
    Main function to execute the batching process.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Setup logging
    setup_logging()

    logging.info("Starting the image-label batching process.")

    # Step 1: Collect all image-label pairs
    pairs = collect_image_label_pairs(args.input_dir)

    if not pairs:
        logging.error("No image-label pairs found. Exiting the script.")
        return

    # Step 2: Shuffle and split into batches
    batches = shuffle_and_split_pairs(pairs)

    # Step 3: Copy batches into separate parent folders with 'images' and 'labels' subfolders
    copy_batches_to_folders(batches, args.output_dir)

    logging.info("Batching process completed successfully.")

if __name__ == "__main__":
    main()