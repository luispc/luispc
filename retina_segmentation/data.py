# -*- coding: utf-8 -*-
"""
Created on Wed May 26 20:25:15 2021

@author: Luis


Retina Blood Vessel Segmentation

Source:
    https://towardsdatascience.com/vessel-segmentation-with-python-and-keras-722f9fb71b21

"""

import os
import numpy as np
import cv2
from glob import glob
from tqdm import tqdm # progressbar
import imageio # to read gif
from albumentations import HorizontalFlip, VerticalFlip, ElasticTransform, GridDistortion, OpticalDistortion


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

        
def load_data(path):
    # return a set of list with path+filenames for training and testing
    # x is input, y is output
    train_x = sorted(glob(os.path.join(path, "training", "images", "*.tif")))
    train_y = sorted(glob(os.path.join(path, "training", "1st_manual", "*.gif")))    
    test_x = sorted(glob(os.path.join(path, "test", "images", "*.tif")))
    test_y = sorted(glob(os.path.join(path, "test", "1st_manual", "*.gif")))    
    return (train_x,train_y),(test_x,test_y)


def augment_data(images,masks,save_path, augment=True):
    H = 256
    W = 256
    for idx, (x,y) in tqdm(enumerate(zip(images,masks)),total=len(images)):
        #print(x,y)
        name = x.split("\\")[-1].split(".")[0]
        x=cv2.imread(x,cv2.IMREAD_COLOR)
        y=imageio.mimread(y)[0]
        
        if augment == True:
            aug = HorizontalFlip(p=1.0)
            augmented = aug(image=x, mask=y)
            x1 = augmented["image"]
            y1 = augmented["mask"]

            aug = VerticalFlip(p=1.0)
            augmented = aug(image=x, mask=y)
            x2 = augmented["image"]
            y2 = augmented["mask"]

            aug = ElasticTransform(p=1, alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03)
            augmented = aug(image=x, mask=y)
            x3 = augmented['image']
            y3 = augmented['mask']

            aug = GridDistortion(p=1)
            augmented = aug(image=x, mask=y)
            x4 = augmented['image']
            y4 = augmented['mask']

            aug = OpticalDistortion(p=1, distort_limit=2, shift_limit=0.5)
            augmented = aug(image=x, mask=y)
            x5 = augmented['image']
            y5 = augmented['mask']

            X = [x, x1, x2, x3, x4, x5]
            Y = [y, y1, y2, y3, y4, y5]
        else:
            X = [x]
            Y = [y]
        index=0
        for i,m in zip(X,Y):
            i = cv2.resize(i, (W,H))
            m = cv2.resize(m, (W,H))
            if len(X)==1:
                tmp_image_name = f"{name}.jpg"
                tmp_mask_name = f"{name}.jpg"
            else:
                tmp_image_name = f"{name}_{index}.jpg"
                tmp_mask_name = f"{name}_{index}.jpg"
            image_path = os.path.join(save_path, "image",tmp_image_name)
            mask_path = os.path.join(save_path, "mask",tmp_mask_name)
            cv2.imwrite(image_path,i)
            cv2.imwrite(mask_path,m)
            index+=1
        

if __name__ == "__main__":
    #%% seeding
    np.random.seed(42)   # magic number
    
    data_path = r'C:/work/py/unet01/dataset/'
    (train_x,train_y),(test_x,test_y) = load_data(data_path)
    
    print(f"Train: {len(train_x)} - {len(train_y)}")
    print(f"Test: {len(test_x)} - {len(test_y)}",flush=True)
        
    #%% create folder
    create_dir("new_data/train/image")
    create_dir("new_data/train/mask")
    create_dir("new_data/test/image")
    create_dir("new_data/test/mask")
    
    augment_data(train_x,train_y, "new_data/train/", augment=True)
    augment_data(test_x,test_y, "new_data/test/", augment=False)
    
    tqdm._instances.clear()
