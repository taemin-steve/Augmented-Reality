import cv2 as cv
import numpy as np
# checker board를 이용하여 camera calibreate 하는 코드 
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

imgInit = cv.imread('./checkerboard/frame5.png')
h, w = imgInit.shape[:2]

pattern_points = np.zeros((patternSize[0] * patternSize[1], 3), np.float32)
pattern_points[:, :2] = np.indices(patternSize).T.reshape(-1, 2)
pattern_points *= 20.0 # my chessboard size is 37 mm
print(pattern_points)
import glob
image_names = glob.glob('./checkerboard/*.png')
points3Ds = []
points2Ds = []

i = 0
for cb_fileName in image_names:
    corners, img = detect_2d_points_from_cbimg(cb_fileName)
    # cv.imshow("test" + str(i), img)
    points3Ds.append(pattern_points)
    points2Ds.append(corners)
    
#cv.imshow("test", img)
#cv.imwrite("./testout2.jpg", img)
#cv.waitKey(0)
#print(pattern_points)
#print(pattern_points)
rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = cv.calibrateCamera(points3Ds, points2Ds, (w, h), None, None)   

print("\nRMS:", rms_err)
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())

newcameramtx, roi = cv.getOptimalNewCameraMatrix(intrisic_mtx, dist_coefs, (w,h), 0, (w,h))
print("camera new intrinsic matrix:\n", newcameramtx)
fs = cv.FileStorage("./cameraParameters.txt", cv.FileStorage_WRITE)
fs.write('camera intrinsic matrix', intrisic_mtx)
fs.write('camera optimized intrinsic matrix', newcameramtx)
fs.write('distortion coefficients', dist_coefs)
fs.write('pose R', rvecs[5])
fs.write('pose T', tvecs[5]) #pos는 다른거가 있다
# 카메라 프로젝션 >> 카메라의 원점이 world의 중심에 가게 해야한다. 
fs.release()

# undistort
img = imgInit
dst = cv.undistort(img, intrisic_mtx, dist_coefs, None, intrisic_mtx)
dst2 = cv.undistort(img, newcameramtx, dist_coefs, None, intrisic_mtx)
cv.imshow("dist", img)
cv.imshow("undist", dst)
cv.imshow("undist2", dst2)
cv.waitKey(0)