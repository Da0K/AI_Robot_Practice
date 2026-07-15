import cv2
import numpy as np
from ultralytics import YOLO
from camera import RealSenseD435

def detect_cube_once(camera, model):
    print("\n===Start testing")

    color_image, depth_image = camera.get_image()
    

if __name__ == "__main__":
    model_path = "/home/da0/runs/segment/train-8/weights/best.pt"
    yolo_model = YOLO(model_path)

    cam = RealSenseD435(color_resolution=720, depth_mode="720P")

    try:
        cube_list = detect_cube_once(cam, yolo_model)
    
    finally:
        if hasattr(cam, '_pipeline'):
            cam._pipeline.stop()