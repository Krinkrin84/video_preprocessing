"""
Video Frame Extraction and Random Selection Tool

This script provides functionality to:
1. Extract frames from videos at specified intervals
2. Optionally perform random selection of frames to maintain a desired percentage

Usage:
    Basic frame extraction:
        python vid_folder_cut_frame.py --input_folder <input_path> --output_folder <output_path> --n <interval>

    Frame extraction with random selection (keeps 80% of frames):
        python vid_folder_cut_frame.py --input_folder <input_path> --output_folder <output_path> --n <interval> --random_select

Parameters:
    --input_folder, -i: Path to folder containing input videos
    --output_folder, -o: Path where extracted frames will be saved
    --n: Frame interval (extract every nth frame)
    --random_select, -r: Enable random frame selection
    --keep_percentage, -k: Percentage of frames to keep (default: 0.8)

Example:
    python vid_folder_cut_frame.py --input_folder ./videos --output_folder ./frames --n 10 --random_select

Notes:
    - Supported video formats: .mp4, .avi, .mov, .mkv, .dav
    - Output frames are saved as .jpg files
    - Random selection is performed independently for each subfolder
    - Progress bars show real-time processing status
"""

import cv2
import os
import argparse
from tqdm import tqdm
from datetime import datetime
import shutil
from multiprocessing import Pool, cpu_count
from collections import defaultdict
import random

class ProcessingStats:
    def __init__(self):
        self.total_videos = 0
        self.processed_videos = 0
        self.total_frames = 0
        self.extracted_frames = 0
        self.video_stats = defaultdict(lambda: {'frames': 0, 'extracted': 0})

    def update_video_stats(self, video_name, total_frames, extracted_frames):
        self.video_stats[video_name]['frames'] = total_frames
        self.video_stats[video_name]['extracted'] = extracted_frames
        self.total_frames += total_frames
        self.extracted_frames += extracted_frames
        self.processed_videos += 1

    def print_summary(self):
        print("\n=== Processing Summary ===")
        print(f"Total videos found: {self.total_videos}")
        print(f"Videos processed: {self.processed_videos}")
        print(f"Total frames across all videos: {self.total_frames}")
        print(f"Total frames extracted: {self.extracted_frames}")
        print("\nPer-video statistics:")
        for video, stats in self.video_stats.items():
            print(f"\n{video}:")
            print(f"  Total frames: {stats['frames']}")
            print(f"  Extracted frames: {stats['extracted']}")
        print("\n=======================")

# Global stats object
stats = ProcessingStats()

def copy_file(args):
    src_path, dest_path = args
    # Ensure unique filenames in the output folder
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(os.path.basename(src_path))
        dest_path = os.path.join(os.path.dirname(dest_path), f"{name}_{counter}{ext}")
        counter += 1
    # Copy the file to the output folder
    shutil.copy(src_path, dest_path)

def combine_folders(root_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all sub-folders in the root directory
    subfolders = [os.path.join(root_folder, folder) for folder in os.listdir(root_folder)
                  if os.path.isdir(os.path.join(root_folder, folder))]

    # Prepare list of all files to copy
    copy_tasks = []
    for subfolder in subfolders:
        # Get all jpg images in the current sub-folder
        images = [file for file in os.listdir(subfolder) if file.lower().endswith(".jpg")]
        for image in images:
            src_path = os.path.join(subfolder, image)
            dest_path = os.path.join(output_folder, image)
            copy_tasks.append((src_path, dest_path))

    # Use multiprocessing to copy files in parallel
    num_processes = max(1, cpu_count() - 1)  # Leave one CPU core free
    with Pool(processes=num_processes) as pool:
        list(tqdm(pool.imap(copy_file, copy_tasks), total=len(copy_tasks), desc="Copying files"))

def extract_frames(input_folder, output_folder, n):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of video files in the input folder
    video_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f)) and f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv','.dav'))]
    
    # Update total videos count
    stats.total_videos = len(video_files)

    # Iterate through the video files
    for video_name in video_files:
        video_path = os.path.join(input_folder, video_name)

        # Create a folder for frames of this video
        video_output_folder = os.path.join(output_folder, os.path.splitext(video_name)[0])
        if not os.path.exists(video_output_folder):
            os.makedirs(video_output_folder)

        # Capture the video
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        saved_frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Use tqdm to iterate over the frames of the current video
        with tqdm(total=total_frames, desc=f"Processing {video_name}", unit="frame") as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Save every nth frame
                if frame_count % n == 0:
                    # Use video name (without extension) in the image file name
                    video_name_without_ext = os.path.splitext(video_name)[0]
                    frame_filename = os.path.join(video_output_folder, f'{video_name_without_ext}_frame_{saved_frame_count:05d}.jpg')
                    cv2.imwrite(frame_filename, frame)
                    saved_frame_count += 1

                frame_count += 1
                pbar.update(1)

        cap.release()
        
        # Update statistics for this video
        stats.update_video_stats(video_name, total_frames, saved_frame_count)

    # Print final summary
    stats.print_summary()
    print(f"Frames have been extracted and saved to {output_folder}")

def remove_frame(args):
    """Helper function for parallel frame removal"""
    frame_path, should_remove = args
    if should_remove:
        try:
            os.remove(frame_path)
            return True
        except Exception as e:
            print(f"Error removing {frame_path}: {str(e)}")
            return False
    return False

def process_folder(folder_path, keep_percentage):
    """Process a single folder for random frame selection"""
    # Get all jpg files in the current folder
    all_frames = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    total_frames = len(all_frames)
    
    if total_frames == 0:
        return 0, 0, 0
    
    # Calculate number of frames to keep
    frames_to_keep = int(total_frames * keep_percentage)
    
    # Randomly select frames to keep
    frames_to_keep_list = random.sample(all_frames, frames_to_keep)
    frames_to_keep_set = set(frames_to_keep_list)
    
    # Prepare arguments for parallel processing
    remove_tasks = []
    for frame in all_frames:
        frame_path = os.path.join(folder_path, frame)
        should_remove = frame not in frames_to_keep_set
        remove_tasks.append((frame_path, should_remove))
    
    # Use multiprocessing to remove frames in parallel
    num_processes = max(1, cpu_count() - 1)  # Leave one CPU core free
    removed_count = 0
    
    with Pool(processes=num_processes) as pool:
        results = list(tqdm(
            pool.imap(remove_frame, remove_tasks),
            total=len(remove_tasks),
            desc=f"Processing {os.path.basename(folder_path)}"
        ))
        removed_count = sum(results)
    
    return total_frames, frames_to_keep, removed_count

def random_select_frames(output_folder, keep_percentage=0.8):
    """
    Randomly select and keep a percentage of frames from the output folder and its subfolders.
    Removes the remaining frames using parallel processing.
    
    Args:
        output_folder (str): Path to the folder containing extracted frames
        keep_percentage (float): Percentage of frames to keep (default: 0.8 for 80%)
    """
    print(f"\nRandomly selecting {keep_percentage*100}% of frames from all subfolders...")
    
    # Get all subfolders including the root folder
    all_folders = [output_folder]  # Start with root folder
    for root, dirs, files in os.walk(output_folder):
        for dir_name in dirs:
            all_folders.append(os.path.join(root, dir_name))
    
    # Process each folder
    total_stats = {
        'total_frames': 0,
        'frames_kept': 0,
        'frames_removed': 0
    }
    
    for folder in all_folders:
        print(f"\nProcessing folder: {folder}")
        total_frames, frames_kept, frames_removed = process_folder(folder, keep_percentage)
        
        if total_frames > 0:
            total_stats['total_frames'] += total_frames
            total_stats['frames_kept'] += frames_kept
            total_stats['frames_removed'] += frames_removed
            
            print(f"Folder summary:")
            print(f"  Total frames: {total_frames}")
            print(f"  Frames kept: {frames_kept}")
            print(f"  Frames removed: {frames_removed}")
    
    print(f"\n=== Overall Frame Selection Summary ===")
    print(f"Total folders processed: {len(all_folders)}")
    print(f"Total frames across all folders: {total_stats['total_frames']}")
    print(f"Total frames kept: {total_stats['frames_kept']}")
    print(f"Total frames removed: {total_stats['frames_removed']}")
    print("=====================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract frames from videos at a specific interval.")
    parser.add_argument("--input_folder", "--i", type=str, required=True, help="Path to the input folder containing videos.")
    parser.add_argument("--output_folder", "--o", type=str, required=True, help="Path to the output folder to save frames.")
    parser.add_argument("--n", type=int, required=True, help="Frame interval to extract frames (e.g., every nth frame).")
    
    #////////// Random Smapling //////////
    parser.add_argument("--random_select", "--r", action="store_true", help="Enable random selection of 80% of frames after extraction.")
    parser.add_argument("--keep_percentage", "--k", type=float, default=0.8, help="Percentage of frames to keep when random selection is enabled (default: 0.8)")

    args = parser.parse_args()

    # Extract frames
    extract_frames(args.input_folder, args.output_folder, args.n)
    
    # If random selection is enabled, perform the selection
    if args.random_select:
        random_select_frames(args.output_folder, args.keep_percentage)
