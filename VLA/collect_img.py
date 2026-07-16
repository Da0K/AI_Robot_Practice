import os
import cv2
import numpy as np

from camera import RealSenseD435

output_dir = "/home/da0/data"

os.makedirs(output_dir, exist_ok=True)
os.makedirs(f'{output_dir}/color', exist_ok=True)
os.makedirs(f'{output_dir}/depth', exist_ok=True)
    
cam = RealSenseD435(color_resolution=720, depth_mode="720P")

count = 0
print(" === RealSense Data Collect === ")
print(" - [Spacebar] : Save Image (RGB & Depth)")
print(" - [ESC]      : Exit ")
print(" ==============================  ")

try:
    while True:
        color_img, depth_meters = cam.get_image()
        depth_img = (depth_meters * 1000).astype(np.uint16)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((color_img, depth_colormap))

        cv2.putText(images, f'Saved : {count} images', (10, 30), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Realsense Data Collection', images)

        key = cv2.waitKey(1) & 0xFF

        # ESC = exit
        if key == 27:
            print("Exit...")
            break

        # Spacebar = save image
        elif key == ord(' '):
            color_path = f'{output_dir}/color/cube_{count:03d}.png'
            depth_path = f'{output_dir}/depth/cube_{count:03d}.png'

            cv2.imwrite(color_path, color_img)
            cv2.imwrite(depth_path, depth_img.astype(np.uint16))

            print(f'Save Complete {color_path} & {depth_path}')
            count += 1

finally:
    if hasattr(cam, '_pipeline'):
        cam._pipeline.stop()
    cv2.destroyAllWindows()