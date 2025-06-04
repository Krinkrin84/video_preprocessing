import cv2
import os
import argparse
from tqdm import tqdm

def extract_frames(input_folder, output_folder, n):
    # Ensure base output folder exists
    os.makedirs(output_folder, exist_ok=True)
    total_frames_saved = 0
    folder_count = 1
    current_output_folder = os.path.join(output_folder, f"batch_{folder_count}")
    os.makedirs(current_output_folder, exist_ok=True)

    # Loop through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(('.avi', '.mp4')):  # Updated to include .mp4
            video_name = os.path.splitext(filename)[0]

            video_path = os.path.join(input_folder, filename)

            # Open the video file
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            with tqdm(total=frame_count, desc=f"Processing {filename}") as pbar:
                current_frame = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Save every nth frame
                    if current_frame % n == 0:
                        if total_frames_saved >= 500:
                            # Create a new folder if the current one has 500 frames
                            folder_count += 1
                            current_output_folder = os.path.join(output_folder, f"batch_{folder_count}")
                            os.makedirs(current_output_folder, exist_ok=True)
                            total_frames_saved = 0

                        frame_filename = f"{video_name}_frame_{current_frame}.jpg"
                        frame_path = os.path.join(current_output_folder, frame_filename)
                        cv2.imwrite(frame_path, frame)
                        total_frames_saved += 1

                    current_frame += 1
                    pbar.update(1)

            cap.release()

    print(f"Frames saved across folders.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract frames from AVI and MP4 videos.')  # Updated description
    parser.add_argument('input_folder', type=str, help='Path to the input folder containing AVI or MP4 videos')
    parser.add_argument('output_folder', type=str, help='Path to the output folder to save JPEG images')
    parser.add_argument('n', type=int, help='Extract every nth frame')

    args = parser.parse_args()
    extract_frames(args.input_folder, args.output_folder, args.n)
    print('Hi i am in main branch')
