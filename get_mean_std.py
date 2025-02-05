'''Train Fer2013 with PyTorch.'''
# 10 crop for data enhancement
from __future__ import print_function

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn
import torchvision
from torchvision import transforms as transforms
import numpy as np
import os
import time
import argparse
import utils
from datasets.RAF import RAF
from datasets.ExpW import ExpW
from datasets.CK_Plus import CK_Plus
from torch.autograd import Variable
from torchtoolbox.transform import Cutout
from torchtoolbox.tools import mixup_data, mixup_criterion

parser = argparse.ArgumentParser(description='PyTorch Fer2013 CNN Training')
parser.add_argument('--dataset', type=str, default='ExpW', help='CNN architecture')
parser.add_argument('--train_bs', default=64, type=int, help='learning rate')
parser.add_argument('--test_bs', default=16, type=int, help='learning rate')
parser.add_argument('--lr', default=0.01, type=float, help='learning rate')
parser.add_argument('--resume', default=False, type=int, help='resume from checkpoint')
opt = parser.parse_args()

use_cuda = torch.cuda.is_available()

# Data
print('==> Preparing data..')
transform_train = transforms.Compose([
    transforms.RandomCrop(92),
    #Cutout(),
    transforms.RandomHorizontalFlip(),
])

teacher_norm = transforms.Compose([
    transforms.ToTensor(),
])

student_norm = transforms.Compose([
    transforms.Resize(44),
    transforms.ToTensor(),
])

transform_test = transforms.Compose([
    transforms.Resize(48),
    transforms.TenCrop(44),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])

if opt.dataset  == 'ExpW':
    print('This is ExpW..')
    trainset = ExpW(split = 'Training', transform=transform_train, student_norm=student_norm, teacher_norm=teacher_norm)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=opt.train_bs, 
        shuffle=True, num_workers=1)

    PrivateTestset = ExpW(split = 'PrivateTest', transform=transform_test, student_norm=None, teacher_norm=None)
    PrivateTestloader = torch.utils.data.DataLoader(PrivateTestset, batch_size=opt.test_bs,
        shuffle=False, num_workers=1)



train_mean=0 
train_std=0
epoch_mean=0 
epoch_std=0

for epoch in range(1, 10):
    for batch_idx, (inputs, _, targets) in enumerate(trainloader):
        #inputs, targets_a, targets_b, lam = mixup_data(inputs, targets, 0.6)
        train_mean += np.mean(inputs.numpy(), axis=(0,2,3))
        train_std += np.std(inputs.numpy(), axis=(0,2,3))
        mean = train_mean/(batch_idx+1)
        std = train_std/(batch_idx+1)    
    train_mean=0 
    train_std=0
    epoch_mean += mean
    epoch_std += std
print('------train_teacher--------')
print (epoch_mean/epoch, epoch_std/epoch)



train_mean=0 
train_std=0
epoch_mean=0 
epoch_std=0

for epoch in range(1, 10):
    for batch_idx, (_, inputs, targets) in enumerate(trainloader):
        #inputs, targets_a, targets_b, lam = mixup_data(inputs, targets, 0.6)
        train_mean += np.mean(inputs.numpy(), axis=(0,2,3))
        train_std += np.std(inputs.numpy(), axis=(0,2,3))
        mean = train_mean/(batch_idx+1)
        std = train_std/(batch_idx+1)    
    train_mean=0 
    train_std=0
    epoch_mean += mean
    epoch_std += std
print('------train_student--------')
print (epoch_mean/epoch, epoch_std/epoch)




train_mean=0 
train_std=0
epoch_mean=0 
epoch_std=0

for epoch in range(1, 10):
    for batch_idx, (inputs, targets) in enumerate(PrivateTestloader):
        train_mean += np.mean(inputs.numpy(), axis=(0,1,3,4))
        train_std += np.std(inputs.numpy(), axis=(0,1,3,4))
        mean = train_mean/(batch_idx+1)
        std = train_std/(batch_idx+1)    
    train_mean=0 
    train_std=0
    epoch_mean += mean
    epoch_std += std
print('------test---------')
print (epoch_mean/epoch, epoch_std/epoch)

