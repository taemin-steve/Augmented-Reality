import numpy as np
import cv2 as cv


def make_2D_points():
    img_list = []
    points_array_2d = []
    fontFace = cv.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0, 255, 0)
    thickness = 2
    lineType = cv.LINE_AA

    for i in range(10):
        # road image 
        img = cv.imread('C:/AR/Augmented-Reality/circle_images/' + str(i + 1)+ '_Color.png', cv.IMREAD_GRAYSCALE)
        img = cv.medianBlur(img,5)
        cimg = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,1,50,param1=50,param2=30,minRadius=19,maxRadius= 30)
        circles = np.uint16(np.around(circles))
        center_pos_list = []
        for j in circles[0,:]:
            # draw the outer circle
            cv.circle(cimg,(j[0],j[1]),j[2],(0,255,0),2)
            # draw the center of the circle
            cv.circle(cimg,(j[0],j[1]),2,(0,0,255),3)
            # save center of the circle
            center_pos_list.append([j[0],j[1]])
            cv.putText(cimg, str(j[0]) + "," + str(j[1]),(j[0],j[1]), fontFace, fontScale, color, thickness, lineType)

        # cv.imshow('detected circles' + str(i + 1),cimg)
        # print("Centers of " + str(i+1)+".jpg's Circles")
        # for k in center_pos_list:
        #     print(k)

        # print(len(center_pos_list))
        points_array_2d.append(center_pos_list)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return np.array(points_array_2d).astype(np.float32)


