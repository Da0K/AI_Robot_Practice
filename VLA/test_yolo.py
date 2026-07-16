import cv2
import numpy as np
from ultralytics import YOLO
from camera import RealSenseD435

from test_RD import AnomalyDetector

def detect_cubes_once(camera, model):
    print("\n=== Start testing the one-time cube detection function ===")

    color_image, depth_image = camera.get_image()

    # Generally Use conf=0.6, but I don't use ANOMALY CUBE in cube detector dataset
    # SO, I use low conf for figure out
    results = model(color_image, conf=0.1, verbose=False)
    
    # Create image for visualization (for debug)
    annotated_frame = results[0].plot()

    # List of cube data to return last
    detected_cubes = []


    # best threshold in 0.3 ~ 0.8
    # check in RD_Tester.ipynb
    detector = AnomalyDetector(_class_="cube", threshold=0.55)

    # Calculate center point, distance, and rotation angle based on segmentation mask information
    if results[0].masks is not None:
        for box, segments in zip(results[0].boxes, results[0].masks.xy):
            xyxy = box.xyxy[0].cpu().numpy()  # [xmin, ymin, xmax, ymax]
            cx = int((xyxy[0] + xyxy[2]) / 2)
            cy = int((xyxy[1] + xyxy[3]) / 2)
            print(cx, cy)
            
            # Check if pixels are valid within the 1280x720 image range
            if 0 <= cx < 1280 and 0 <= cy < 720:
                distance_m = depth_image[cy, cx]
                
                print(distance_m)

                if distance_m > 0:
                    # --- [Calculation of rotation angle] ---
                    contours = segments.astype(np.int32)
                    rect = cv2.minAreaRect(contours)
                    box_points = cv2.boxPoints(rect)
                    box_points = np.int0(box_points)
                    
                    angle = rect[2]

                    (width, height) = rect[1]
                    if width < height:
                        angle = angle + 90.0
                    # ------------------------
                    
                    # detect anomaly
                    x, y, w_box, h_box = cv2.boundingRect(contours)

                    x_min, y_min = max(0, x), max(0, y)
                    x_max, y_max = min(1280, x+w_box), min(720, y+h_box)
                    cube_crop = color_image[y_min:y_max, x_min:x_max]

                    anomaly_status = detector.is_anomaly(cube_crop)

                    # [pixel X, Pixel Y, Distance Z (m), Rotation Angle (degree)]
                    detected_cubes.append([cx, cy, float(distance_m), float(angle), anomaly_status])

                    # print(distance_m, anomaly_status)

                    # For visualization (for debug)
                    cv2.drawContours(annotated_frame, [box_points], 0, (0, 255, 0), 2)
                    cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)
                    text = f"Z:{distance_m:.3f}m R:{angle:.1f}deg, anomaly={anomaly_status}"
                    cv2.putText(annotated_frame, text, (cx + 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # For visualization (for debug)
    cv2.imshow("Cube Detection Result (Single Frame)", annotated_frame) # If you don't need a visualization window, annotate it.

    cv2.waitKey(0) # If you don't need a visualization window, annotate it.
    cv2.destroyAllWindows() # If you don't need a visualization window, annotate it.

    print(f"\n[Detected] Length of returned list: {len(detected_cubes)}")
    print("------------------------------------------")
    for idx, cube in enumerate(detected_cubes):
        px, py, pz, rot, ano = cube
        print(f"Cube_list[{idx}] -> Pixel X: {px}, Pixel Y: {py}, Distance Z: {pz:.3f}m, Rotation Angle: {rot:.1f}°, Anomaly: {ano}")
    
    return detected_cubes



if __name__ == "__main__":
    # Initialize weight & model file
    model_path = "/home/da0/AI_Robot_Practice/VLA/best.pt"
    yolo_model = YOLO(model_path)

    # Initialize camera
    camera = RealSenseD435(color_resolution=720, depth_mode="720P")
    
    try:
        cube_list = detect_cubes_once(camera, yolo_model)
            
    finally:
        if hasattr(camera, '_pipeline'):
            camera._pipeline.stop()
