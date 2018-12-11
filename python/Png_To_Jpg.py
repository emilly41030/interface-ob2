from PIL import Image
import os, sys

path = '/home/kelly/data/Dataset/Mura/LCD4/label_img'
out = '/home/kelly/data/Dataset/Mura/LCD4/label_jpg/'
file = os.listdir(path)
for f in file:
    print(f)
    im = Image.open(path+'/'+f)
    f_s = f.split('.')
    rgb_im = im.convert('RGB')
    rgb_im.save(out+f_s[0]+".jpg")
print("finish")