import cv2
import time
import argparse
from ultralytics import YOLO

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Count people in webcam feed using YOLO')
    parser.add_argument('--device', type=int, default=0, help='Webcam device number (default: 0)')
    parser.add_argument('--conf', type=float, default=0.3, help='Confidence threshold (default: 0.3)')
    parser.add_argument('--output', type=str, help='Path to output video file (optional)')
    
    args = parser.parse_args()
    
    # Load the YOLO model
    print("Loading YOLO model...")
    model = YOLO('yolov8n.pt')  # Using the nano model, will download if not present
    
    # Open webcam
    print(f"Opening webcam device {args.device}...")
    cap = cv2.VideoCapture(args.device)
    if not cap.isOpened():
        print(f"Error: Could not open webcam device {args.device}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30  # Assume 30 FPS for webcam
    
    # Initialize video writer if output path is specified
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        print(f"Recording output to {args.output}")
    
    # Initialize variables for FPS calculation
    frame_count = 0
    start_time = time.time()
    fps_update_interval = 10  # Update FPS display every 10 frames
    current_fps = 0
    
    print("Press 'q' to quit")
    
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error reading from webcam")
            break
        
        # Run YOLOv8 inference on the frame
        results = model(frame, conf=args.conf)
        
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
        
        # Calculate and update FPS every few frames
        frame_count += 1
        if frame_count % fps_update_interval == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            current_fps = fps_update_interval / elapsed_time
            start_time = time.time()
        
        # Add information to the frame
        cv2.putText(frame, f"People: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Write the frame to output video if specified
        if writer:
            writer.write(frame)
        
        # Display the frame
        cv2.imshow('YOLO Webcam People Counter', frame)
        
        # Check for key press
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break
    
    # Release resources
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("Webcam people counter stopped")

if __name__ == "__main__":
    main()