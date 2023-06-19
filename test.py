import cv2
import numpy as np
import panda3d.core as p3c

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

WEBCAM_RESIZE_RATIO = 1
N_CALIBRATION_IMAGES = 30
PATTERN_SIZE = (5, 3) # (5, 3)
PATTERN_LENGTH = 26.26590886
MIN_DISTANCE = 30
VIDEO_PATH = "record.mp4"

# This class represents a simple application that uses a webcam to capture images and display them on the screen.
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

        self.imgW = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)*WEBCAM_RESIZE_RATIO)
        self.imgH = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)*WEBCAM_RESIZE_RATIO)
        
        winprops = p3c.WindowProperties()
        winprops.setSize(self.imgW, self.imgH)
        self.win.requestProperties(winprops)

        self.myAxis = self.loader.loadModel("models/zup-axis")
        matScale = p3c.LMatrix4f().scaleMat(3.7, 3.7,3.7)
        self.myAxis.setMat(matScale)
        self.myAxis.reparentTo(self.render)

        self.cam.setPos(0, -50, 0)
        self.cam.lookAt(p3c.LPoint3f(0, 0, 0), p3c.LVector3f(0, 0, 1))
        # self.cam.lookAt(p3c.LPoint3f(0, 0, 0))

        self.camLens.setNearFar(1, 1000)
        
        self.camLens.setFov(90)
        
        self.tex = p3c.Texture()
        self.tex.setup2dTexture(self.imgW, self.imgH, p3c.Texture.T_unsigned_byte, p3c.Texture.F_rgb)
        
        background = OnscreenImage(image=self.tex)

        
        background.reparentTo(self.render2dp)

        
        self.cam2dp.node().getDisplayRegion(0).setSort(-20)

        self.textObject = OnscreenText(text="", pos=( -0.05, -0.95), 
                            scale=(0.07, 0.07),
                            fg=(1, 0.5, 0.5, 1), 
                            align=p3c.TextNode.A_right,
                            mayChange=1)
        self.textObject.reparentTo(self.aspect2d)

        
        self.accept('1', self.calibrateBegin)

        
        self.accept('2', self.calibrateEnd)
 
        
        self.calibrateOn = False
        self.pattern_points = np.zeros((PATTERN_SIZE[0] * PATTERN_SIZE[1], 3), np.float32)
        self.pattern_points[:, :2] = np.indices(PATTERN_SIZE).T.reshape(-1, 2)
        self.pattern_points *= PATTERN_LENGTH

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
        self.prev_center_corner = (0, 0)
        self.intrisic_mtx = np.array([[1,0,0],[0,1,0],[0,0,1]])
        self.dist_coefs = np.array([0,0,0,0])

        self.points3Ds = []
        self.points2Ds = []

        self.taskMgr.add(updateBg, 'video frame update')

        self.arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        self.arucoParams = cv2.aruco.DetectorParameters()

        # Load the video file
        self.video1 = self.loader.loadTexture(VIDEO_PATH)

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
        self.myMovieTexture = p3c.MovieTexture("Movie")
        self.myMovieTexture.read(VIDEO_PATH)
        # self.plane.setUvRange(self.myMovieTexture)
        # aspect_ratio = 0.7840531561461794
        # self.plane.setFrame(-1, 1, -1/aspect_ratio, 1/aspect_ratio)

        self.plane.reparentTo(self.render)
        self.plane.setTexture(myTextureStage, self.video1)

    def calibrateBegin(self):

        self.textObject.text = "calibrate On"

        self.calibrateOn = True
        self.intrisic_mtx = None
        self.dist_coefs = None
        self.points2Ds = []
        self.points3Ds = []
        


    def calibrateEnd(self):

        self.textObject.text = "calibrate Off"

        self.calibrateOn = False

# This function calculates the distance between two points.
def distance_between_points(p1, p2):
    """
    Calculates the distance between two points.

    Args:
    p1: A NumPy array of shape (2,) representing the first point.
    p2: A NumPy array of shape (2,) representing the second point.

    Returns:
    The distance between the two points.
    """

    # Calculate the difference between the points.
    d = p2 - p1

    # Calculate the length of the difference vector.
    distance = np.linalg.norm(d)

    # Return the distance.
    return distance



# This function updates the background image.
def updateBg(task):
    """
    Updates the background image.

    Args:
    task: The task object.

    Returns:
    The task object.
    """

    # Read the next frame from the camera.
    success, frame = app.cap.read()
    if not success:
        raise("camera error!")
    
    # Resize the frame.
    frame = cv2.resize(frame, None, fx=WEBCAM_RESIZE_RATIO, fy=WEBCAM_RESIZE_RATIO)
    
    # If the camera is being calibrated and there are less than 50 points,
    # find the checkerboard corners in the frame.
    if app.calibrateOn == True and len(app.points2Ds) < N_CALIBRATION_IMAGES:
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(img_gray, PATTERN_SIZE)

        # If the checkerboard corners were found,
        # draw them on the frame and get the center of the checkerboard.
        if found:
            app.textObject.text = "checker board is detected!!!!"
            # Get the corners of the checkerboard
            corners2 = cv2.cornerSubPix(img_gray, corners, PATTERN_SIZE, (-1, -1), app.criteria)
            center_corner = np.sum(corners2, axis=0).squeeze() / PATTERN_SIZE[0] / PATTERN_SIZE[1]

            distance = distance_between_points(app.prev_center_corner, center_corner)                        
            
            if distance > MIN_DISTANCE and corners2[5][0][1] > corners2[0][0][1]:
                # Draw the corners on the image
                cv2.drawChessboardCorners(frame, PATTERN_SIZE, corners2, found)
                app.points3Ds.append(app.pattern_points)
                app.points2Ds.append(corners2)
                app.prev_center_corner = center_corner
                print(f"{len(app.points2Ds)}, {distance:4.4f}")
            
        # If the checkerboard corners were not found,
        # print a message.
        else:
            app.textObject.text = "checker board is not found!"
    # If there are N_CALIBRATION_IMAGES points,
    # calibrate the camera.
    elif app.calibrateOn == True and len(app.points2Ds) == N_CALIBRATION_IMAGES:
        print("run calibarions")
        rms_err, intrisic_mtx, dist_coefs, rvecs, tvecs = \
            cv2.calibrateCamera(
                app.points3Ds, 
                app.points2Ds, 
                (app.imgH, app.imgH), 
                None, 
                None
            )
        print("\nRMS:", rms_err)
        # print("camera intrinsic matrix:\n", intrisic_mtx)
        # print("distortion coefficients: ", dist_coefs.ravel())
        app.calibrateEnd()

        app.intrisic_mtx = intrisic_mtx
        app.dist_coefs = dist_coefs

    # undistort the frame.
    if app.calibrateOn == False and app.intrisic_mtx is not None:
        frame = cv2.undistort(frame, app.intrisic_mtx, app.dist_coefs, None, app.intrisic_mtx)
    
    #################
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, app.arucoDict, parameters=app.arucoParams)

    if ids is not None and 3 in ids:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        index = np.where(ids == 3)[0][0]
        marker_corners = corners[index].squeeze()

        a = np.array([[-25, 0, 25], [25, 0, 25], [25, 0, -25], [-25, 0, -25]], dtype=np.float32)

        success, rvec, tvec = cv2.solvePnP(
            np.array(a), 
            marker_corners, 
            app.intrisic_mtx, 
            app.dist_coefs, 
            flags=0
            )
        
        # Create a TextureStage and apply the transformation to it
        if success:
            matView = getViewMatrix(rvec, tvec)
            matViewInv = p3c.LMatrix4()
            matViewInv.invertFrom(matView)

            cam_pos = matViewInv.xformPoint(p3c.LPoint3(0, 0, 0))
            cam_view = matViewInv.xformVec(p3c.LVector3(0, 0, 1))
            cam_up = matViewInv.xformVec(p3c.LVector3(0, -1, 0))

            app.cam.setPos(cam_pos)
            app.cam.lookAt(cam_pos + cam_view, cam_up)

            app.plane.setPos(0, 0, 0)

    # positive y goes down in openCV, so we must flip the y coordinates
    flip_frame = cv2.flip(frame, 0)

    # flip the frame horizontally for mirror mode.
    flip_frame = cv2.flip(flip_frame, 1)

    # overwriting the memory with new frame
    app.tex.setRamImage(flip_frame)

    # return the task object.
    return task.cont

# from rvecs and tvecs to opencv view transform…
def getViewMatrix(rvec, tvec):
    # build view matrix
    rmtx = cv2.Rodrigues(rvec)[0] # col-major
    
    view_matrix = p3c.LMatrix4(rmtx[0][0], rmtx[1][0], rmtx[2][0], 0,
                        rmtx[0][1], rmtx[1][1], rmtx[2][1], 0,
                        rmtx[0][2], rmtx[1][2], rmtx[2][2], 0,
                        tvec[0], tvec[1], tvec[2], 1)
                        
    return view_matrix 

if __name__ == '__main__':
    app = MyApp()
    near = 1
    app.camLens.setNearFar(near, 1000)
    app.camLens.setFocalLength(near)
    
    ratio_x_pix = near / app.intrisic_mtx[0][0]
    ratio_y_pix = near / app.intrisic_mtx[1][1]    # the same effect for the opencv flip
    sensor_w = ratio_x_pix * app.imgW
    sensor_h = ratio_y_pix * app.imgH
    app.camLens.setFilmSize(sensor_w, sensor_h)
    
    sensor_offset_x = sensor_w * 0.5 - app.intrisic_mtx[0][2] * ratio_x_pix
    sensor_offset_y = sensor_h * 0.5 - app.intrisic_mtx[1][2] * ratio_y_pix
    app.camLens.setFilmOffset(sensor_offset_x, sensor_offset_y)    
    # K = app.intrisic_mtx
    
    app.run()
cv2.destroyAllWindows()