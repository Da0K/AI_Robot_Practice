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

# Teacher와 Student의 Feature map을 받아와 Anomaly map을 생성하는 함수 (기존과 동일)
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
        """
        프로그램 시작 시 가중치 및 모델을 미리 GPU/CPU 메모리에 로드합니다.
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.threshold = threshold
        
        # 데이터 전처리 트랜스폼 설정 (256x256 타겟 해상도 지정)
        self.data_transform = get_data_transforms(256, 256)
        
        # 모델 빌드 및 가중치 경로 정의
        ckp_path = os.path.join(checkpoint_dir, f'wres50_{_class_}.pth')
        
        print(f"[{_class_}] RD Model Reset... ({self.device})")
        self.encoder, bn = wide_resnet50_2(pretrained=True)
        self.encoder = self.encoder.to(self.device)
        self.encoder.eval()
        
        self.bn = bn.to(self.device)
        self.decoder = de_wide_resnet50_2(pretrained=False).to(self.device)
        
        # 체크포인트 안전 로드
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

        # 1. OpenCV(BGR) 이미지 형식을 PIL(RGB)로 변환 (기존 RD_Dataset 구조 동기화)
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
        
        # 2. 데이터 전처리 수행 ([3, 256, 256])
        img_tensor = self.data_transform(pil_img)
        
        # 3. 배치 차원 추가 ([3, 256, 256] ->) 후 장치로 이동
        img_tensor = img_tensor.unsqueeze(0).to(self.device)
        
        # 4. 모델 포워딩 수행
        inputs = self.encoder(img_tensor)
        outputs = self.decoder(self.bn(inputs))
        
        # 5. 아노말리 맵 계산 및 필터 처리
        anomaly_map = cal_anomaly_map(inputs, outputs, img_tensor.shape[-1], amap_mode='a')
        anomaly_map = gaussian_filter(anomaly_map, sigma=4)
        
        # 6. 현재 단일 단면의 최고 불량 점수 추출
        # (주의: 기존 전체 평가 코드는 min-max 정규화를 테스트셋 전체 점수로 나눴으나, 
        #  실시간 단일 처리 시에는 raw score 기준으로 threshold 값을 조정하거나 스케일 처리를 보정해야 할 수 있습니다.)
        max_score = np.max(anomaly_map)
        
        # 7. 임계값(threshold) 기준 판단
        if max_score < self.threshold:
            return 0  # Good (정상)
        else:
            return 1  # Bad (비정상)
