import cv2 as cv
import cv2.aruco as aruco
import numpy as np
from matplotlib import pyplot as plt

def plot_img(rows, cols, index, img, title, axis='on'):
    ax = plt.subplot(rows,cols,index)
    if(len(img.shape) == 3 and img.shape[2] == 3):
        ax_img = plt.imshow(img[...,::-1]) # same as img[:,:,::-1]), RGB image is displayed without cv.cvtColor
    else:
        ax_img = plt.imshow(img, cmap='gray')
    plt.axis(axis)
    if(title != None): plt.title(title) 
    return ax_img, ax

arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_50) # 6x6의 마커세트. 미리 만들어진 50개 사용
arucoParams = cv.aruco.DetectorParameters()

markerPixelSize = 300
marker_img = np.zeros((markerPixelSize,markerPixelSize,1), dtype="uint8")
cv.aruco.generateImageMarker(arucoDict, 3, markerPixelSize, marker_img, 5) # 마지막 파라미터는 border임. 
cv.imwrite('./aruco_markers/m3_100.bmp', marker_img)
