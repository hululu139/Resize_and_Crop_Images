# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 12:12:55 2021

@author: Asus
"""
import os
import argparse
import urllib
import shutil
import json
import random
import numpy as np
import pandas as pd
import cv2
from shutil import copyfile
import os.path
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import sys
#resize#####################################################
def resize(anno_filename,image_dir,anno_dir):
    
    scale=3.2
    
    # rescale image
    imgfile=image_dir+'/'+anno_filename
    img = cv2.imread(imgfile)
    cv2.imwrite(imgfile, cv2.resize(img, (int(160*scale), int(120*scale))))
    
    # rescale annotations
    anno_file= anno_dir+'/'+anno_filename[:-4]+'.xml' 
    tree =ET.parse(anno_file)              
    root=tree.getroot()
    # rescale size
    for i in range(2): 
        s=root[2][i].text
        root[2][i].text= str(int(int(s)*3.2))
    # rescale bbox
    for obb in root.iter('object'):
        for box in obb.findall('bndbox'):
            for c in box:
                c.text = str(int(int(float(c.text)*3.2)))
    tree.write(anno_file)
    

#crop########################################################
picture=[]
posture=[]    
def extract_annotation(xml_file_path,categories,classes):
    
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    annotation = {}
    
    annotation['file'] = root.find('filename').text
    annotation['categories'] = categories
    
    size = root.find('size')
    
    annotation['image_size'] = [{
        'width': int(size.find('width').text),
        'height': int(size.find('height').text),
        'depth': int(size.find('depth').text)
    }]
    
    annotation['annotations'] = []
    
    for item in root.iter('object'):
        class_id = classes.index(item.find('name').text)
        ymin, xmin, ymax, xmax = None, None, None, None
        
        for box in item.findall('bndbox'):
            xmin = int(float(box.find("xmin").text))
            ymin = int(float(box.find("ymin").text))
            xmax = int(float(box.find("xmax").text))
            ymax = int(float(box.find("ymax").text))
        
            if all([xmin, ymin, xmax, ymax]) is not None:
                 annotation['annotations'].append({
                     'class_id': class_id,
                     'boundingbox': [xmin, ymin, xmax, ymax]
                    
                 })
    return annotation
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
###############################################################
def main():
    parser = argparse.ArgumentParser(
        description='This script support resizing and cropping')
    parser.add_argument('--anno', type=dir_path, default=None,
                        help='path to annotation files. It is not need when use --ann_paths_list')
    parser.add_argument('--image', type=dir_path, default=None,
                        help='path of images. It is not need when use --ann_dir and --ann_ids')
    parser.add_argument('--label', type=str, default=None,
                        help='where you want to save cropeed images')
    parser.add_argument('--csv', type=dir_path, default=None,
                        help='where you want to save the csv file')
    parser.add_argument('--store', type=str, default=None,
                        help='where you want to save cropeed images')
    args = parser.parse_args()
    anno_dir=args.anno
    image_dir=args.image
    csv_dir=args.csv
    store_dir=args.store
    label=args.label
    CLASS_MAPPING = {}
    label_file = open(label)
    for line in label_file:
        key, value = line.split()
        CLASS_MAPPING[key] = value
    classes = list(CLASS_MAPPING.values())
    relation=CLASS_MAPPING
    categories=[]
    for key in CLASS_MAPPING:
        cat={}
        cat['class_id']=key
        cat['name']=CLASS_MAPPING.get(key)
        categories.append(cat)
    anno_files = [os.path.join(anno_dir, x) for x in os.listdir(anno_dir) if x[-3:] == 'xml']
    all_images=os.listdir(image_dir)
    for filename in os.listdir(image_dir):
        resize(filename,image_dir,anno_dir)
    os.makedirs(store_dir)
    for i,image in enumerate(all_images):
        xml_file_path=anno_dir+'/'+image[:-4]+'.xml'
        annot=extract_annotation(xml_file_path,categories,classes)
        for l in range(len(annot['annotations'])):
            classid=annot['annotations'][l].get('class_id')
            gesture=relation.get(str(classid))
            bbox=annot['annotations'][l].get('boundingbox')
            im=Image.open(os.path.join(image_dir,image))
            im=im.crop(bbox)
            im.save(store_dir+'/'+image[:-4]+'{}'.format(l)+".jpg")
            picture.append(image[:-4]+'{}'.format(l)+".jpg")
            posture.append(gesture)
    df1=pd.DataFrame (posture, columns=['gesture'])
    df2=pd.DataFrame (picture,columns=['id'])
    df=pd.concat([df1,df2],axis=1)
    df.to_csv(csv_dir+"/"+'gesture.csv', index = False)
    
if __name__ == '__main__':
    main()