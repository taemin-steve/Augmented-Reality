from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
import panda3d.core as p3c

import cv2 as cv

# vid_cap = cv.VideoCapture(0, cv.CAP_DSHOW) 
# # Check if the webcam is opened correctly
# if not vid_cap.isOpened():
#     raise IOError("Cannot open webcam")

# frame_w = int(vid_cap.get(cv.CAP_PROP_FRAME_WIDTH))
# frame_h = int(vid_cap.get(cv.CAP_PROP_FRAME_HEIGHT))


imgW = 900
imgH = 1200

class MyApp(ShowBase):

    def __init__(self): # initial start// only one time
        ShowBase.__init__(self)
        
        winprops = p3c.WindowProperties()
        winprops.setSize(imgW,imgH)
        self.win.request
        
        print("hello!") # this is for initial work, so it run only one time 
        
        # Load the environment model.
        self.myAxis = self.loader.loadModel("models/zup-axis") # load model - you can check another models in git
        # Reparent the model to render.
        self.myAxis.reparentTo(self.render) # you should attach new objects to renderer. 
        # self.myParameter = 12345.0 # Why put this line?
        self.cam.setPos(0, -50, 0) # set camera pos 
        
        self.Teapot = self.loader.loadModel("models/teapot")
        self.Teapot.reparentTo(self.render)
        # self.Teapot.setPos(0,-10,0)
        # self.tex = p3c.Texture()
        
        # background = OnscreenImage(image=self.tex) # Load an image object
        # background.reparentTo(self.render2dp) # if you run this line, Only 2D renderer will run, so that you can't find any axis 
        # background.reparentTo(self.render) 
        
        # 추가로 LMatrix4f를 이용해서 translate과 scale을 확인하였음. 
        


app = MyApp()

tex = p3c.Texture()
tex.setup2dTexture(imgW,imgH, p3c.Texture.T_unsigned_byte,p3c.Texture.F_rgb )
# tex.setRamImage() ## 진짜 그 이미지 

imgTest = cv.imread('./resized images/image5.jpg')
imgTest = cv.flip(imgTest,0)
tex.setRamImage(imgTest)

background = OnscreenImage(image=tex)
background.reparentTo(app.render2d)


app.cam2dp.node().getDisplayRegion(0).setSort(-20)
app.run()