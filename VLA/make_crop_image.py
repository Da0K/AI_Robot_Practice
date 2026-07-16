# To make dataset -> cropped dataset

import os
import cv2
import numpy as np
from pathlib import Path

def crop_yolo_segmentation_path():

    for img_p in image_paths:
        base_name = img_p.stem
        
        label_p = label_path_obj / f"{base_name}.txt"
        if not label_p.exists():
            print(f" No label : '{base_name}.txt'")
            continue
        
        image = cv2.imread(str(img_p), cv2.IMREAD_COLOR)
        if image is None:
            print(f"Fail Image Load : {base_name}")
            continue
            
        h, w, c = image.shape
        
        with open(label_p, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print(f"Empty files : {base_name}")
            continue
            
        
        for obj_idx, line in enumerate(lines):
            data = line.strip().split()
            if len(data) < 7:
                continue
                
            class_id = data[0]
            coords = np.array(data[1:], dtype=np.float32)
            
            coords[0::2] *= w  
            coords[1::2] *= h  
            
            pts = coords.reshape(-1, 2).astype(np.int32)
        
            x, y, box_w, box_h = cv2.boundingRect(pts)
            
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [pts], 255)
            
            masked_img = cv2.bitwise_and(image, image, mask=mask)
            
            final_crop = masked_img[y:y+box_h, x:x+box_w]
            
            output_file_path = out_path_obj / f"{base_name}_obj{obj_idx}_cls{class_id}.png"
            cv2.imwrite(str(output_file_path), final_crop)
                    
        print(f"Make Crop : total - {base_name}, success -{len(lines)}")

if __name__ == "__main__":

    current_script_dir = Path(__file__).resolve().parent if '__file__' in locals() else Path(os.getcwd()).resolve()
    
    img_path_obj = current_script_dir / "dataset_RD" / "train" / "images"
    label_path_obj = current_script_dir / "dataset_RD" / "train" / "labels"
    out_path_obj = current_script_dir / "dataset_RD" / "train" / "cropped"
    out_path_obj.mkdir(parents=True, exist_ok=True)

    image_extensions = ['*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.png', '*.PNG']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(list(img_path_obj.glob(ext)))
        
    print(f"Image amount :  {len(image_paths)}")
    print("-" * 60)

    crop_yolo_segmentation_path()
