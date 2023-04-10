import cv2 as cv
import numpy as np


import glob
image_names = glob.glob('./camera images/*.jpg')


imgIndex = 0
for fn in image_names:
    print(fn)
    img = cv.imread(fn)
    resized_img = cv.resize(img, (900, 1200))
    cv.imwrite('./resized images/image{}.jpg'.format(imgIndex), resized_img)
    imgIndex += 1

patternSize = (8, 6)

def detect_2d_points_from_cbimg(file_name):
    print("processing", file_name)
    img = cv.imread(file_name)
    h, w = img.shape[:2]

    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    found, corners = cv.findChessboardCorners(img_gray, patternSize)
    if found:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 30, 0.1)
        #print(corners[10])
        corners = cv.cornerSubPix(img_gray, corners, (5, 5), (-1, -1), criteria)
        #print(corners[10])
        cv.drawChessboardCorners(img, patternSize, corners, found)
    else : # not found
        print('chessboard not found')
        return None
    
    return corners, img

imgInit = cv.imread('./resized images/image0.jpg')
h, w = imgInit.shape[:2]

pattern_points = np.zeros((patternSize[0] * patternSize[1], 3), np.float32)
pattern_points[:, :2] = np.indices(patternSize).T.reshape(-1, 2)
pattern_points *= 10.0 # my chessboard size is 37 mm
print(pattern_points)

import glob
image_names = glob.glob('./resized images/*.jpg')
points3Ds = []
points2Ds = []

i = 0
for cb_fileName in image_names:
    if(detect_2d_points_from_cbimg(cb_fileName)):
        corners, img = detect_2d_points_from_cbimg(cb_fileName)
        cv.imshow("test" + str(i), img)
        points3Ds.append(pattern_points) # 3D좌표
        points2Ds.append(corners) # 2D 좌표
    
print(points3Ds)
print(points2Ds)
#cv.imshow("test", img)
#cv.imwrite("./testout2.jpg", img)
#cv.waitKey(0)
#print(pattern_points)
#print(pattern_points)
rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = cv.calibrateCamera(points3Ds, points2Ds, (w, h), None, None)   

print("\nRMS:", rms_err)
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())

# undistort
img = imgInit
dst = cv.undistort(img, intrisic_mtx, dist_coefs, None, intrisic_mtx)
cv.imshow("dist", img)
cv.imshow("undist", dst)
cv.waitKey(0)
    