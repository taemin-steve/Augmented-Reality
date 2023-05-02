from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
import panda3d.core as p3c

import cv2 as cv
import cv2.aruco as aruco
import numpy as np

vid_cap = cv.VideoCapture(0, cv.CAP_DSHOW) 
# Check if the webcam is opened correctly
if not vid_cap.isOpened():
    raise IOError("Cannot open webcam")

imgW = int(vid_cap.get(cv.CAP_PROP_FRAME_WIDTH))
imgH = int(vid_cap.get(cv.CAP_PROP_FRAME_HEIGHT))

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        
        winprops = p3c.WindowProperties()
        winprops.setSize(imgW, imgH)
        self.win.requestProperties(winprops)
        
        print("hello!")
        
        # Load the environment model.
        self.myAxis = self.loader.loadModel("models/zup-axis")
        # Reparent the model to render.
        self.myAxis.reparentTo(self.render)
        matScale1 = p3c.LMatrix4f().scaleMat(3.7, 3.7, 3.7)
        self.myAxis.setMat(matScale1)
        
        self.myTeapot = self.loader.loadModel("models/teapot")
        self.myTeapot.reparentTo(self.render)
        matScale = p3c.LMatrix4f().scaleMat(6, 6, 6)
        self.myTeapot.setMat(matScale)

        #matScale = p3c.LMatrix4f().scaleMat(3, 3, 3)
        #matTranslate = p3c.LMatrix4f().translateMat(0, 0, 5)
        #matT = matScale * matTranslate
        #self.myTeapot.setMat(matT)
        
        bbox = self.myAxis.getTightBounds()
        print(bbox)
        
        self.cam.setPos(0, -50, 0)
        self.cam.lookAt(p3c.LPoint3f(0, 0, 0), p3c.LVector3f(0, 0, 1))
        
        self.camLens.setNearFar(1, 1000)
        self.camLens.setFov(90)
        #self.cam.lookAt(p3c.LPoint3f(0, 0, 0), p3c.LVector3f(1, 0, 0))
        
        self.tex = p3c.Texture()
        self.tex.setup2dTexture(imgW, imgH, p3c.Texture.T_unsigned_byte, p3c.Texture.F_rgb)
        background = OnscreenImage(image=self.tex) # Load an image object
        background.reparentTo(self.render2dp)

app = MyApp()

arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_50)
arucoParams = cv.aruco.DetectorParameters()

patternSize = (5,4)
patter_points = ()

points2Ds = []


def updateBg(task):
    success, frame = vid_cap.read()
    if success == False:
        return task.cont
    # positive y goes down in openCV, so we must flip the y coordinates
    flip_frame = cv.flip(frame, 0)
    # overwriting the memory with new frame
    app.tex.setRamImage(flip_frame)
    
    #################
    (corners, ids, rejected) = cv.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    print("corners {}, ".format(len(corners)))
    
    return task.cont




app.taskMgr.add(updateBg, 'video frame update')


app.run()


















'''
tex = p3c.Texture()
tex.setup2dTexture(imgW, imgH, p3c.Texture.T_unsigned_byte, p3c.Texture.F_rgb)

imgTest = cv.imread('./resized images/image5.jpg')
imgTest = cv.flip(imgTest, 0)
tex.setRamImage(imgTest)

background = OnscreenImage(image=tex) # Load an image object
background.reparentTo(app.render2dp)

# We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering.
app.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)

# later http://blog.yarrago.com/2011/08/introduction-to-augmented-reality.html
fr = cv.FileStorage("./cameraParameters.txt", cv.FileStorage_READ)
if not fr.isOpened():
    raise IOError("Cannot open cam parameters")
intrisic_mtx = fr.getNode('camera intrinsic matrix').mat()
dist_coefs = fr.getNode('distortion coefficients').mat()
newcameramtx = fr.getNode('camera optimized intrinsic matrix').mat()
rvec = fr.getNode('pose R').mat()
tvec = fr.getNode('pose T').mat()
print("camera intrinsic matrix:\n", intrisic_mtx)
print("distortion coefficients: ", dist_coefs.ravel())
print("camera new intrinsic matrix:\n", newcameramtx)
print("rvec:{}, tvec:{}".format(rvec, tvec))
fr.release()
print(intrisic_mtx[0][2], intrisic_mtx[1][2])

near = 1
app.camLens.setNearFar(near, 1000)
app.camLens.setFocalLength(near)

ratio_x_pix = near / intrisic_mtx[0][0]
ratio_y_pix = near / intrisic_mtx[1][1]    # the same effect for the opencv flip
sensor_w = ratio_x_pix * imgW
sensor_h = ratio_y_pix * imgH
app.camLens.setFilmSize(sensor_w, sensor_h)
print("ratio_pix w, h : ", ratio_x_pix, ratio_y_pix)
print("sensor w, h : ", sensor_w, sensor_h)

sensor_offset_x = sensor_w * 0.5 - intrisic_mtx[0][2] * ratio_x_pix
sensor_offset_y = sensor_h * 0.5 - intrisic_mtx[1][2] * ratio_y_pix
app.camLens.setFilmOffset(sensor_offset_x, sensor_offset_y)

# from rvecs and tvecs to opencv view transform...
def getViewMatrix(rvec, tvec):
    # build view matrix
    rmtx = cv.Rodrigues(rvec)[0] # col-major
    
    view_matrix = p3c.LMatrix4(rmtx[0][0], rmtx[1][0], rmtx[2][0], 0,
                        rmtx[0][1], rmtx[1][1], rmtx[2][1], 0,
                        rmtx[0][2], rmtx[1][2], rmtx[2][2], 0,
                        tvec[0], tvec[1], tvec[2], 1)
                        
    return view_matrix 

matView = getViewMatrix(rvec, tvec)
matViewInv = p3c.LMatrix4()
matViewInv.invertFrom(matView)

cam_pos = matViewInv.xformPoint(p3c.LPoint3(0, 0, 0))
cam_view = matViewInv.xformVec(p3c.LVector3(0, 0, 1))
cam_up = matViewInv.xformVec(p3c.LVector3(0, -1, 0))

app.cam.setPos(cam_pos)
app.cam.lookAt(cam_pos + cam_view, cam_up)

print(cam_pos)

app.run()
'''