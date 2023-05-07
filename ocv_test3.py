import cv2 as cv
import cv2.aruco as aruco
import numpy as np
from matplotlib import pyplot as plt
# 아루코 마커 만들어 주는 코드 
def plot_img(rows, cols, index, img, title, axis='on'):    
    ax = plt.subplot(rows,cols,index)
    if(len(img.shape) == 3 and img.shape[2] == 3):
        ax_img = plt.imshow(img[...,::-1]) # same as img[:,:,::-1]), RGB image is displayed without cv.cvtColor
    else:
        ax_img = plt.imshow(img, cmap='gray')
    plt.axis(axis)
    if(title != None): plt.title(title) 
    return ax_img, ax

# https://docs.opencv.org/master/d9/d6a/group__aruco.html#ga254ed245e10c5b3e2259d5d9b8ea8e2f
# https://www.pyimagesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_50)
arucoParams = cv.aruco.DetectorParameters()

markerPixelSize = 300
marker_img = np.zeros((markerPixelSize, markerPixelSize, 1), dtype="uint8")
cv.aruco.generateImageMarker(arucoDict, 3, markerPixelSize, marker_img, 1)
cv.imwrite('./aruco_markers/m3_101.bmp', marker_img)
