import cv2
import numpy as np
import argparse
import time
from ultralytics import YOLO
from pathlib import Path

# Initialize YOLO model
def load_model():
    # Load YOLOv8 model
    # Options: yolov8n.pt (nano), yolov8s.pt (small), yolov8m.pt (medium), 
    # yolov8l.pt (large), yolov8x.pt (xlarge)
    model = YOLO('yolov8l.pt')  # Using large model for better accuracy
    return model

# Process image and count people
def process_image(model, image_path, output_path=None, conf_threshold=0.4):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return None, 0
    
    # Run YOLOv8 inference on the image with additional parameters
    results = model(
        img,
        conf=conf_threshold,
        iou=DETECTION_CONFIG['iou_threshold'],
        agnostic_nms=DETECTION_CONFIG['agnostic_nms'],
        max_det=DETECTION_CONFIG['max_det']
    )
    
    # Initialize person counter
    person_count = 0
    
    # Process the results
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Class 0 is person in COCO dataset which YOLOv8 uses by default
            if int(box.cls) == 0:  
                person_count += 1
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Draw bounding box
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add label
                label = f"Person: {conf:.2f}"
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Add total count to the image
    cv2.putText(img, f"Total People: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Save the output image if specified
    if output_path:
        cv2.imwrite(output_path, img)
        print(f"Output saved to {output_path}")
    
    return img, person_count

# Process video and count people
def process_video(model, video_path, output_path=None, conf_threshold=0.4, display=True):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize video writer if output path is specified
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    total_people = 0
    processing_times = []
    
    # Initialize frame buffer for averaging
    frame_buffer = []
    buffer_size = 3
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Add frame to buffer
        frame_buffer.append(frame)
        if len(frame_buffer) > buffer_size:
            frame_buffer.pop(0)
            
        # Average frames if buffer is full
        if len(frame_buffer) == buffer_size:
            frame = np.mean(frame_buffer, axis=0).astype(np.uint8)
        
        start_time = time.time()
        
        # Run YOLOv8 inference on the frame
        results = model(frame, conf=conf_threshold)
        
        # Initialize person counter for this frame
        person_count = 0
        
        # Process the results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Class 0 is person in COCO dataset
                if int(box.cls) == 0:  
                    person_count += 1
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Add label
                    label = f"Person: {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add total count to the frame
        cv2.putText(frame, f"People in frame: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Calculate and display FPS
        end_time = time.time()
        processing_time = end_time - start_time
        processing_times.append(processing_time)
        fps_text = f"FPS: {1/processing_time:.2f}"
        cv2.putText(frame, fps_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Write the frame to output video if specified
        if writer:
            writer.write(frame)
        
        # Display the frame if requested
        if display:
            cv2.imshow('People Counter', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break
        
        frame_count += 1
        total_people += person_count
    
    # Release resources
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    
    # Calculate average processing time and FPS
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    avg_fps = 1 / avg_processing_time if avg_processing_time > 0 else 0
    
    print(f"Processed {frame_count} frames")
    print(f"Average people per frame: {total_people/frame_count:.2f}")
    print(f"Average processing time: {avg_processing_time:.4f} seconds")
    print(f"Average FPS: {avg_fps:.2f}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Count people in images and videos using YOLO')
    parser.add_argument('--source', type=str, required=True, help='Path to input image or video file')
    parser.add_argument('--output', type=str, help='Path to output file (optional)')
    parser.add_argument('--conf', type=float, default=0.3, help='Confidence threshold (default: 0.3)')
    parser.add_argument('--no-display', action='store_true', help='Do not display output (for video processing)')
    
    args = parser.parse_args()
    
    # Load the YOLO model
    model = load_model()
    
    # Check if the source is an image or video based on file extension
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source file {args.source} does not exist")
        return
    
    # Process based on file type
    if source_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
        # Process image
        output_img, count = process_image(model, args.source, args.output, args.conf)
        
        if output_img is not None:
            print(f"Detected {count} people in the image")
            
            # Display the image if not explicitly disabled
            if not args.no_display:
                cv2.imshow('People Counter', output_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
    
    elif source_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
        # Process video
        process_video(model, args.source, args.output, args.conf, not args.no_display)
    
    else:
        print(f"Error: Unsupported file format {source_path.suffix}")

if __name__ == "__main__":
    main()