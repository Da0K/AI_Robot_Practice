import os
import torch
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from torch.nn import functional as F
import cv2

from resnet import wide_resnet50_2
from de_resnet import de_wide_resnet50_2
from dataset import get_data_transforms
from de_resnet import de_wide_resnet50_2

def cal_anomaly_map(fs_list, ft_list, out_size=224, amap_mode='mul'):
    if amap_mode == 'mul':
        anomaly_map = np.ones([out_size, out_size])
    else:
        anomaly_map = np.zeros([out_size, out_size])
    for i in range(len(ft_list)):
        fs = fs_list[i]
        ft = ft_list[i]
        a_map = 1 - F.cosine_similarity(fs, ft)
        a_map = torch.unsqueeze(a_map, dim=1)
        a_map = F.interpolate(a_map, size=out_size, mode='bilinear', align_corners=True)
        a_map = a_map[0, 0, :, :].to('cpu').detach().numpy()
        if amap_mode == 'mul':
            anomaly_map *= a_map
        else:
            anomaly_map += a_map
    return anomaly_map


class AnomalyDetector:
    def __init__(self, _class_="cube", threshold=0.3, checkpoint_dir='/home/da0/AI_Robot_Practice/VLA/checkpoints'):

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.threshold = threshold
        
        self.data_transform = get_data_transforms(256, 256)
        
        ckp_path = os.path.join(checkpoint_dir, f'wres50_{_class_}.pth')
        
        print(f"[{_class_}] RD Model Reset... ({self.device})")
        self.encoder, bn = wide_resnet50_2(pretrained=True)
        self.encoder = self.encoder.to(self.device)
        self.encoder.eval()
        
        self.bn = bn.to(self.device)
        self.decoder = de_wide_resnet50_2(pretrained=False).to(self.device)
        
        # checkpoint load
        ckp = torch.load(ckp_path)
        for k, v in list(ckp['bn'].items()):
            if 'memory' in k:
                ckp['bn'].pop(k)
                
        self.decoder.load_state_dict(ckp['decoder'])
        self.bn.load_state_dict(ckp['bn'])
        
        self.bn.eval()
        self.decoder.eval()
        print("Ready to RD Model")

    @torch.no_grad()
    def is_anomaly(self, cv2_image):

        if cv2_image is None or cv2_image.size == 0:
            print("Empty image problem")
            return 0

        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
        
        # Make Data to Format [3, 256, 256]
        img_tensor = self.data_transform(pil_img)
        img_tensor = img_tensor.unsqueeze(0).to(self.device)
        
        # Model Forwarding
        inputs = self.encoder(img_tensor)
        outputs = self.decoder(self.bn(inputs))
        
        # Calculate Anomaly Score
        anomaly_map = cal_anomaly_map(inputs, outputs, img_tensor.shape[-1], amap_mode='a')
        anomaly_map = gaussian_filter(anomaly_map, sigma=4)
        max_score = np.max(anomaly_map)
        
        # Is anomaly?
        if max_score < self.threshold:
            return 0  # Good
        else:
            return 1  # Bad
