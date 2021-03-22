# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 08:56:01 2021

@author: Asus
"""
import os
import xml.etree.cElementTree as ET
from PIL import Image
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

CLASS_MAPPING = {}
label_file = open("label.txt")
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
def create_root(file_prefix, width, height):
    root = ET.Element("annotations")
    ET.SubElement(root, "filename").text = "{}.jpg".format(file_prefix)
    ET.SubElement(root, "folder").text = "images"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"
    return root


def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = voc_label[0]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = str(0)
        ET.SubElement(obj, "difficult").text = str(0)
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(voc_label[1])
        ET.SubElement(bbox, "ymin").text = str(voc_label[2])
        ET.SubElement(bbox, "xmax").text = str(voc_label[3])
        ET.SubElement(bbox, "ymax").text = str(voc_label[4])
    return root


def create_file(file_prefix, width, height, voc_labels,save_dir):
    root = create_root(file_prefix, width, height)
    root = create_object_annotation(root, voc_labels)
    tree = ET.ElementTree(root)
    tree.write("{}/{}.xml".format(save_dir, file_prefix))
    
def read_file(file_path,image_dir,anno_dir,save_dir):
    file_prefix = file_path
    image_file_name = file_prefix.split(".")[0]+".jpg"
    img = Image.open(image_dir+"/"+image_file_name)
    w, h = img.size
    with open(anno_dir+"/"+file_path, 'r') as file:
        lines = file.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip()
            data = line.split()
            voc.append(CLASS_MAPPING.get(data[0]))
            bbox_width = int(float(data[3]) * w)+1
            bbox_height = int(float(data[4]) * h)+1
            center_x = int(float(data[1]) * w)+1
            center_y = int(float(data[2]) * h)+1
            voc.append(center_x - (bbox_width / 2))
            voc.append(center_y - (bbox_height / 2))
            voc.append(center_x + (bbox_width / 2))
            voc.append(center_y + (bbox_height / 2))
            voc_labels.append(voc)
        create_file(file_prefix.split(".")[0], w, h, voc_labels,save_dir)
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
def main():
    parser = argparse.ArgumentParser(
        description='This script support resizing and cropping')
    parser.add_argument('--anno', type=dir_path, default=None,
                        help='path to annotation files. It is not need when use --ann_paths_list')
    parser.add_argument('--image', type=dir_path, default=None,
                        help='path of images. It is not need when use --ann_dir and --ann_ids')
    parser.add_argument('--save', type=str, default=None,
                    help='path of images. It is not need when use --ann_dir and --ann_ids')
    args = parser.parse_args()
    anno_dir=args.anno
    image_dir=args.image
    save_dir=args.save
    os.makedirs(save_dir)
    for filename in os.listdir(anno_dir):
        read_file(filename,image_dir,anno_dir,save_dir)
    
if __name__ == '__main__':
    main()