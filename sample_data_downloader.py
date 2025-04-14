import os
import urllib.request
import argparse
from pathlib import Path

# Sample data URLs
SAMPLE_IMAGES = {
    'crowd1': 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=1200',
    'crowd2': 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=1200',
    'street': 'https://images.unsplash.com/photo-1454117096348-e4abbeba002c?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&w=1200'
}

# Sample video URL (Pexels free stock video)
SAMPLE_VIDEOS = {
    'people_walking': 'https://www.pexels.com/download/video/855564/?fps=25.0&h=720&w=1280',
    'crowd': 'https://www.pexels.com/download/video/1739012/?fps=29.97&h=720&w=1280'
}

def download_file(url, output_path):
    """Download a file from URL to the specified path"""
    print(f"Downloading {output_path.name}...")
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded {output_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download sample images and videos for YOLO people counter')
    parser.add_argument('--type', choices=['images', 'videos', 'all'], default='all',
                        help='Type of sample data to download (default: all)')
    parser.add_argument('--output', type=str, default='./sample_data',
                        help='Output directory for downloaded files (default: ./sample_data)')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    images_dir = output_dir / 'images'
    videos_dir = output_dir / 'videos'
    
    # Download images
    if args.type in ['images', 'all']:
        images_dir.mkdir(parents=True, exist_ok=True)
        print("\nDownloading sample images...")
        for name, url in SAMPLE_IMAGES.items():
            output_path = images_dir / f"{name}.jpg"
            if output_path.exists():
                print(f"{output_path} already exists, skipping")
                continue
            download_file(url, output_path)
    
    # Download videos
    if args.type in ['videos', 'all']:
        videos_dir.mkdir(parents=True, exist_ok=True)
        print("\nDownloading sample videos...")
        for name, url in SAMPLE_VIDEOS.items():
            output_path = videos_dir / f"{name}.mp4"
            if output_path.exists():
                print(f"{output_path} already exists, skipping")
                continue
            download_file(url, output_path)
    
    print("\nDownload complete!")
    print("\nYou can now use these samples with the people counter:")
    
    if args.type in ['images', 'all']:
        print("\nSample image commands:")
        for name in SAMPLE_IMAGES.keys():
            print(f"python people_counter.py --source {images_dir / f'{name}.jpg'} --output {images_dir / f'{name}_result.jpg'}")
    
    if args.type in ['videos', 'all']:
        print("\nSample video commands:")
        for name in SAMPLE_VIDEOS.keys():
            print(f"python people_counter.py --source {videos_dir / f'{name}.mp4'} --output {videos_dir / f'{name}_result.mp4'}")

if __name__ == "__main__":
    main()