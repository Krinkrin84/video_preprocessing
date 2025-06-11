import os
from tqdm import tqdm
from collections import Counter

def count_class_ids(folder_path):
    """
    Count the occurrence of each class ID in all .txt files in the folder.

    Args:
        folder_path (str): Path to the folder containing .txt files.
    """
    class_counts = Counter()  # To store the counts of each class ID
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    if not txt_files:
        print("No .txt files found in the specified folder.")
        return

    # Use tqdm to track progress
    for file_name in tqdm(txt_files, desc="Processing .txt files", unit="file"):
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, "r") as file:
                for line in file:
                    columns = line.split()
                    if columns:
                        # The class ID is assumed to be the first column
                        class_id = columns[0]
                        class_counts[class_id] += 1
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    # Print the results
    print("\nClass ID Counts:")
    for class_id, count in sorted(class_counts.items(), key=lambda x: int(x[0])):
        print(f"Class ID {class_id}: {count} occurrences")


if __name__ == "__main__":
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Count class IDs in text label files.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing .txt files.")

    # Parse arguments
    args = parser.parse_args()

    # Count class IDs
    count_class_ids(args.folder_path)