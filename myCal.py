import cv2 as cv
import numpy as np
from circle import make_2D_points

# pattern_points = np.array([[0.210745,0.211728,-0.193256],[0.180948,0.101878,0.087774],[0.173486,0.170723,0.082539],[0.190451,0.200691,-0.123108],[0.226842,0.121402,-0.206477]]).astype(np.float32)
# print(pattern_points)

print(make_2D_points())
points3Ds = []
points2Ds = []

img_cr = cv.imread('C:/AR/Augmented-Reality/1.jpg', cv.IMREAD_GRAYSCALE)
h,w = img_cr.shape[:2]

points3Ds.append(np.array([[0.210745,0.211728,-0.193256],[0.180948,0.101878,0.087774],[0.173486,0.170723,0.082539],[0.190451,0.200691,-0.123108],[0.226842,0.121402,-0.206477],
                           [0.311317,0.210845,-0.1959000],[0.281802,0.103462,-0.089169],[0.277797,0.172846,-0.084092],[0.289305,0.200209,-0.128950],[-0.320648,0.119240,-0.211209],
                           [0.283365,0.215584,-0.170411],[-0.187261,0.104984,-0.090066],[0.178418,0.174899,-0.084664],[0.204821,0.203591,-0.116953],[0.275486,0.125324,-0.178331]]).astype(np.float32))

points2Ds.append(np.array([[335, 315],[1169, 1101],[613, 1130],[404, 798],[1014, 229],
                           [411, 390],[1112, 1109],[630, 1126],[459, 828],[1012, 313],
                           [338, 469],[1087, 1179],[541, 1124],[365, 839],[978, 497]]).astype(np.float32))
    
print(points3Ds)
print(points2Ds)

rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = cv.calibrateCamera(points3Ds, points2Ds, (w, h), None, None)  
#! For non-planar calibration rigs the initial intrinsic matrix must be specified in function 'cvCalibrateCamera2Internal'

print("\nRMS:", rms_err)
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())

    