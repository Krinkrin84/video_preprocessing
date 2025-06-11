import cv2
import os
import argparse
from tqdm import tqdm


def crop_video_end(input_video_path, output_video_path, cut_duration_minutes):
    """
    Crop the end portion of a video and save it as a new MP4 file.

    Args:
        input_video_path: Path to the input video file
        output_video_path: Path to save the output video
        cut_duration_minutes: Duration to cut from the end (in minutes)
    Returns:
        bool: True if successful, False otherwise
    """
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file {input_video_path}")
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps
    cut_seconds = cut_duration_minutes * 60

    # Calculate start frame for the cut duration
    start_seconds = max(0, duration_seconds - cut_seconds)
    start_frame = int(start_seconds * fps)
    remaining_frames = total_frames - start_frame

    # Set the starting position
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Get video codec and size
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec

    # Create video writer
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Initialize progress bar
    progress = tqdm(total=remaining_frames, unit='frames',
                    desc=f"Cutting last {cut_duration_minutes} minutes")

    # Read and write frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)
        progress.update(1)

    # Close progress bar and release resources
    progress.close()
    cap.release()
    out.release()

    # Verify output
    if os.path.exists(output_video_path):
        print(f"\nSuccessfully saved last {cut_duration_minutes} minutes to: {output_video_path}")
        return True
    print("\nError: Failed to create output video")
    return False


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Crop the end portion of a video.')
    parser.add_argument('-i', '--input', required=True, help='Input video file path')
    parser.add_argument('-o', '--output', required=True, help='Output video file path')
    parser.add_argument('-m', '--minutes', type=float, default=15.0,
                        help='Duration to cut from end in minutes (default: 15)')

    args = parser.parse_args()

    # Run the cropping function
    if crop_video_end(args.input, args.output, args.minutes):
        print("Operation completed successfully!")
    else:
        print("Operation failed")


if __name__ == "__main__":
    main()