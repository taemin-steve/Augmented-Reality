import cv2 as cv
import numpy as np

"""
import glob
image_names = glob.glob('./camera images/*.jpg')

imgIndex = 0
for fn in image_names:
    img = cv.imread(fn)
    resized_img = cv.resize(img, (900, 1200))
    cv.imwrite('./resized images/image{}.jpg'.format(imgIndex), resized_img)
    imgIndex += 1
"""

patternSize = (7, 5)

img = cv.imread('./resized images/image0.jpg')
h, w = img.shape[:2]
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
found, corners = cv.findChessboardCorners(img_gray, (7, 5))
if found:
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 30, 0.1)
    print(corners[10])
    corners = cv.cornerSubPix(img_gray, corners, (5, 5), (-1, -1), criteria)
    print(corners[10])
    cv.drawChessboardCorners(img, patternSize, corners, found)

#cv.imshow("test", img)
#cv.imwrite("./testout2.jpg", img)
#cv.waitKey(0)

pattern_points = np.zeros((patternSize[0] * patternSize[1], 3), np.float32)
pattern_points[:, :2] = np.indices(patternSize).T.reshape(-1, 2)
#print(pattern_points)
pattern_points *= 37.0 # my chessboard size is 37 mm
#print(pattern_points)
points3Ds = [pattern_points]
points2Ds = [corners]

rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = cv.calibrateCamera(points3Ds, points2Ds, (w, h), None, None)   

print("\nRMS:", rms_err)
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())

# undistort
dst = cv.undistort(img, intrisic_mtx, dist_coefs, None, intrisic_mtx)
cv.imshow("dist", img)
cv.imshow("undist", dst)
cv.waitKey(0)
    