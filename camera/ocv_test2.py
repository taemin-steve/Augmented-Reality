import cv2 as cv

import glob
image_names = glob.glob('./camera images/*.jpg')

imgIndex = 0
for fn in image_names:
    img = cv.imread(fn)
    resized_img = cv.imwrite() #이거 체커보드 안쪽 점부터 세어줘야한다. 