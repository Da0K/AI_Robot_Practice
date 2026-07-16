import torch
import time
import natsort
import os
from dataset import get_data_transforms
from torchvision.datasets import ImageFolder
import numpy as np
import random
import os
from torch.utils.data import DataLoader
from resnet import resnet18, resnet34, resnet50, wide_resnet50_2
from de_resnet import de_resnet18, de_resnet34, de_wide_resnet50_2, de_resnet50
from dataset import RD_Dataset
import torch.backends.cudnn as cudnn
import argparse
from torch.nn import functional as F
# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)

def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def loss_fucntion(a, b):
    #mse_loss = torch.nn.MSELoss()
    cos_loss = torch.nn.CosineSimilarity()
    loss = 0
    for item in range(len(a)):
        #print(a[item].shape)
        #print(b[item].shape)
        #loss += 0.1*mse_loss(a[item], b[item])
        loss += torch.mean(1-cos_loss(a[item].view(a[item].shape[0],-1),
                                      b[item].view(b[item].shape[0],-1)))
    return loss

def loss_concat(a, b):
    mse_loss = torch.nn.MSELoss()
    cos_loss = torch.nn.CosineSimilarity()
    loss = 0
    a_map = []
    b_map = []
    size = a[0].shape[-1]
    for item in range(len(a)):
        #loss += mse_loss(a[item], b[item])
        a_map.append(F.interpolate(a[item], size=size, mode='bilinear', align_corners=True))
        b_map.append(F.interpolate(b[item], size=size, mode='bilinear', align_corners=True))
    a_map = torch.cat(a_map,1)
    b_map = torch.cat(b_map,1)
    loss += torch.mean(1-cos_loss(a_map,b_map))
    return loss

def train(_class_):
    print(_class_)
        
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)

    data_transform = get_data_transforms(image_size, image_size)
    
    train_path = './data/' + _class_ + '/train'
    ckp_path = './checkpoints/' + 'wres50_'+_class_+'.pth'
    os.makedirs('./checkpoints', exist_ok=True)
    
    train_data = ImageFolder(root=train_path, transform=data_transform)
    train_dataloader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)

    encoder, bn = wide_resnet50_2(pretrained=True)
    encoder = encoder.to(device)
    bn = bn.to(device)
    encoder.eval()
    decoder = de_wide_resnet50_2(pretrained=False)
    decoder = decoder.to(device)

    optimizer = torch.optim.Adam(list(decoder.parameters())+list(bn.parameters()), lr=learning_rate, betas=(0.5,0.999))


    for epoch in range(epochs):
        start = time.time() 
        
        bn.train()
        decoder.train()
        loss_list = []
        for img, label in train_dataloader:
            img = img.to(device)
            inputs = encoder(img)
            outputs = decoder(bn(inputs))#bn(inputs))
            loss = loss_fucntion(inputs, outputs)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_list.append(loss.item())
        print('epoch [{}/{}], loss:{:.4f}'.format(epoch + 1, epochs, np.mean(loss_list)))
        print("time :",time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

        # if (epoch + 1) % 2 == 0:
        # for cpu test
        if (epoch + 1) % 10 == 0:
            torch.save({'bn': bn.state_dict(),'decoder': decoder.state_dict()}, ckp_path)
            
    return loss

def main():
    setup_seed(111)

    #학습
    for i in item_list:
        start_class = time.time()  # 시작 시간 저장

        train(i)
        print(i, "time :",time.time() - start_class)  # 현재시각 - 시작시간 = 실행 시간



if __name__ == "__main__":
    # find the dataset list
    base_path = "/home/da0/AI_ROBOT_PRACTICE/VLA/data/"
    folder_list = os.listdir("./data/")
    item_list = natsort.natsorted(folder_list)
    print("다음 데이터셋들이 학습됩니다 : ", item_list)

    #최소10, 200~400 추천, 10단위로 pth가 저장됨

    epochs = 100
    batch_size = 4

    #3090 24GB에서 64까지 사용 가능했음
    learning_rate = 0.005
    # image_size = 256
    image_size = 640
    main()