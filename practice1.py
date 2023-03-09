from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
import panda3d.core as p3c

import cv2 as cv

vid_cap = cv.VideoCapture(0, cv.CAP_DSHOW) 
# Check if the webcam is opened correctly
if not vid_cap.isOpened():
    raise IOError("Cannot open webcam")

frame_w = int(vid_cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_h = int(vid_cap.get(cv.CAP_PROP_FRAME_HEIGHT))

class MyApp(ShowBase):

    def __init__(self): # initial start// only one time
        ShowBase.__init__(self)
        
        print("hello!") # this is for initial work, so it run only one time 
        
        # Load the environment model.
        self.myAxis = self.loader.loadModel("models/zup-axis") # load model - you can check another models in git
        # Reparent the model to render.
        self.myAxis.reparentTo(self.render) # you should attach new objects to renderer. 
        # self.myParameter = 12345.0 # Why put this line? 
        self.cam.setPos(0, -50, 0) # set camera pos 
        
        self.Teapot = self.loader.loadModel("models/teapot")
        self.Teapot.reparentTo(self.render)
        self.Teapot.setPos(0,-10,0)
        
        self.tex = p3c.Texture()
        self.tex.setup2dTexture(frame_w, frame_h, p3c.Texture.T_unsigned_byte, p3c.Texture.F_rgb) # creat new texture 
        background = OnscreenImage(image=self.tex) # Load an image object
        # background.reparentTo(self.render2dp) # if you run this line, Only 2D renderer will run, so that you can't find any axis 
        background.reparentTo(self.render) 
        
        # 추가로 LMatrix4f를 이용해서 translate과 scale을 확인하였음. 
        


app = MyApp()


def updateBg(task):
    success, frame = vid_cap.read()
    # positive y goes down in openCV, so we must flip the y coordinates
    flip_frame = cv.flip(frame, 0)
    # overwriting the memory with new frame
    app.tex.setRamImage(flip_frame)
    
    return task.cont


app.taskMgr.add(updateBg, 'video frame update')

# print(app.myParameter)
app.run()