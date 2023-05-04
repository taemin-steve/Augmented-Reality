from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
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
        bbox = self.myTeapot.getTightBounds()
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
        self.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)
        
        self.accept('1', self.calibrateBegin)
        self.accept('2', self.calibrateEnd)
        
        self.calibrateOn = False
        # Load the video file
        self.video1 = self.loader.loadTexture("./pose_dance_1.mp4")
        #self.video1 = self.loader.loadTexture("./img1.jpg")

        myTextureStage = p3c.TextureStage("myTextureStage")
        myTextureStage.setMode(p3c.TextureStage.MReplace)

        # Create a plane to display the video on
        vdata = p3c.GeomVertexData(
            'triangle_data', p3c.GeomVertexFormat.getV3t2(), p3c.Geom.UHStatic)
        vdata.setNumRows(4)  # optional for performance enhancement!
        vertex = p3c.GeomVertexWriter(vdata, 'vertex')
        vertex.addData3(-30, 0, 30)
        vertex.addData3(30, 0, 30)
        vertex.addData3(30, 0, -30)
        vertex.addData3(-30, 0, -30)
        texcoord = p3c.GeomVertexWriter(vdata, 'texcoord')
        texcoord.addData2(0, 1)
        texcoord.addData2(1, 1)
        texcoord.addData2(1, 0)
        texcoord.addData2(0, 0)
        primTris = p3c.GeomTriangles(p3c.Geom.UHStatic)
        primTris.addVertices(0, 1, 2)
        primTris.addVertices(0, 2, 3)
        geom = p3c.Geom(vdata)
        geom.addPrimitive(primTris)
        geomNode = p3c.GeomNode("Plane")
        geomNode.addGeom(geom)
        # note nodePath is the instance for node (obj resource)
        self.plane = p3c.NodePath(geomNode)
        self.plane.setTwoSided(True)
        #self.plane = self.loader.loadModel("models/box")
        #bbox = self.plane.getTightBounds()
        #print(bbox)
        #self.plane.setScale(50)
        self.plane.reparentTo(self.render)
        self.plane.setTexture(myTextureStage, self.video1)
        
    def calibrateBegin(self):
        self.textObject.text = "calibrate On"
        self.calibrateOn = True
        
    def calibrateEnd(self):
        self.textObject.text = "calibrate Off"
        self.calibrateOn = False

app = MyApp()

arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_50)
arucoParams = cv.aruco.DetectorParameters()

patternSize = (5, 4)
pattern_points = np.zeros((patternSize[0] * patternSize[1], 3), np.float32)
pattern_points[:, :2] = np.indices(patternSize).T.reshape(-1, 2)
pattern_points *= 29.7 # my chessboard size is 29.7 mm

points3Ds = []
numCorrespondingPairs = 50
for x in range(numCorrespondingPairs):
    points3Ds.append(pattern_points)
    
points2Ds = []
app.prev_corners = np.zeros((patternSize[0] * patternSize[1], 1, 2), np.float32)
app.intrisic_mtx = None
app.flags = None

######
# as long as you get the correct intrinsics, just load the parameters from a file
# TO DO

def updateBg(task):
    success, frame = vid_cap.read()
    if success == False:
        return task.cont

    # positive y goes down in openCV, so we must flip the y coordinates
    # overwriting the memory with new frame
    
    #################
    
    if app.calibrateOn == True:
        # TO DO
        img = frame
        h, w = img.shape[:2]

        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        found, corners = cv.findChessboardCorners(img_gray, patternSize)
        if found:
            app.textObject.text = "checker board is detected!"
            # TO DO

        else : # not found
            app.textObject.text = "checker board is not found!"
        
    flip_frame = cv.flip(frame, 0)
    app.tex.setRamImage(flip_frame)
    
    #################
    (corners, ids, rejected) = cv.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    #print("corners {}, ".format(len(corners)))
    
    if len(corners) > 0:
        for id in ids:
            print("[INFO] ArUco marker ID: {}".format(id))
            # TO DO when the marker is our target one
    
    return task.cont

app.textObject = OnscreenText(text="No AR Marker Detected", pos=( -0.05, -0.95), 
                        scale=(0.07, 0.07),
                        fg=(1, 0.5, 0.5, 1), 
                        align=p3c.TextNode.A_right,
                        mayChange=1)
app.textObject.reparentTo(app.aspect2d)

app.taskMgr.add(updateBg, 'video frame update')

app.run()
