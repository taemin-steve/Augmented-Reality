import cv2 as cv
import numpy as np


pattern_points = np.array([[0.210745,0.211728,-0.193256],[0.180948,0.101878,0.087774],[0.173486,0.170723,0.082539],[0.190451,0.200691,-0.123108],[0.226842,0.121402,-0.206477]]).astype(np.float32)
print(pattern_points)


points3Ds = []
points2Ds = []

img_cr = cv.imread('C:/AR/Augmented-Reality/1.jpg', cv.IMREAD_GRAYSCALE)
h,w = img_cr.shape[:2]

points3Ds.append(pattern_points)
points2Ds.append(np.array([[335, 315],[1169, 1101],[613, 1130],[404, 798],[1014, 229]]).astype(np.float32))
    
print(points3Ds)
print(points2Ds)

rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = cv.calibrateCamera(points3Ds, points2Ds, (w, h), None, None)  
#! For non-planar calibration rigs the initial intrinsic matrix must be specified in function 'cvCalibrateCamera2Internal'

print("\nRMS:", rms_err)
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())

    