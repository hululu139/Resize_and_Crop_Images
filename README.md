# Resize_and_Crop_Images
Input: Yolo format, Label txt
Output: Cropped image with resizing to *3.2 (applicable with multiple object)

Instance:
Step 1:
python ytv.py \
--anno annotation_YOLO \
--image image \
--save annotation \

Step2:
--anno annotation \
--image image \
--label label.txt \
--csv . \
--store crop \
