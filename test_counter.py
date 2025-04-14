import os
import argparse
from pathlib import Path
from people_counter import load_model, process_image, process_video

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test YOLO people counter with sample data')
    parser.add_argument('--mode', choices=['image', 'video'], default='image',
                        help='Test mode: image or video (default: image)')
    parser.add_argument('--sample-dir', type=str, default='./sample_data',
                        help='Directory containing sample data (default: ./sample_data)')
    
    args = parser.parse_args()
    sample_dir = Path(args.sample_dir)
    
    # Check if sample directory exists
    if not sample_dir.exists():
        print(f"Sample directory {sample_dir} does not exist.")
        print("Please run sample_data_downloader.py first to download sample data.")
        print("Example: python sample_data_downloader.py")
        return
    
    # Load the YOLO model
    print("Loading YOLO model...")
    model = load_model()
    
    if args.mode == 'image':
        # Process sample images
        images_dir = sample_dir / 'images'
        if not images_dir.exists() or not any(images_dir.iterdir()):
            print(f"No sample images found in {images_dir}")
            print("Please run sample_data_downloader.py to download sample images.")
            return
        
        print(f"\nProcessing sample images from {images_dir}...")
        for img_path in images_dir.glob('*.jpg'):
            if '_result' in img_path.name:
                continue  # Skip result images
                
            print(f"\nProcessing {img_path.name}...")
            output_path = images_dir / f"{img_path.stem}_result.jpg"
            
            # Process the image
            _, count = process_image(model, str(img_path), str(output_path))
            print(f"Detected {count} people in {img_path.name}")
            print(f"Result saved to {output_path.name}")
    
    elif args.mode == 'video':
        # Process sample videos
        videos_dir = sample_dir / 'videos'
        if not videos_dir.exists() or not any(videos_dir.iterdir()):
            print(f"No sample videos found in {videos_dir}")
            print("Please run sample_data_downloader.py to download sample videos.")
            return
        
        print(f"\nProcessing sample videos from {videos_dir}...")
        for video_path in videos_dir.glob('*.mp4'):
            if '_result' in video_path.name:
                continue  # Skip result videos
                
            print(f"\nProcessing {video_path.name}...")
            output_path = videos_dir / f"{video_path.stem}_result.mp4"
            
            # Process the video
            process_video(model, str(video_path), str(output_path), display=True)
            print(f"Result saved to {output_path.name}")

if __name__ == "__main__":
    main()