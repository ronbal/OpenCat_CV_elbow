import numpy as np
import cv2
import math
import time
from ardSerial import *
from Py_commander import *

def find_lowest_pixel(frame,coordinates):
    top=coordinates[0][0]+2
    down=coordinates[1][0]-2
    left=coordinates[0][1]+2
    right=coordinates[1][1]-2
 
    myimg=frame[left:right,top:down]
    cv2.imshow("Captured area",myimg)
    avg_color_per_row = np.average(myimg, axis=0)
    avg=np.average(avg_color_per_row, axis=0)
    it=0.3
    itsa=6
    return [(avg[0]-itsa,int(avg[1]*(1-it)),10),(avg[0]+itsa,int(avg[1]*(1+it)),225)]

def skin_finder(cap):
    while(True):
        ret, frame = cap.read()
        upper_left_coord=(frame.shape[1]//2-12,frame.shape[0]//4-12)
        lower_righ_coord=(frame.shape[1]//2+12,frame.shape[0]//4+12)
        cv2.rectangle(frame,upper_left_coord,lower_righ_coord,(255,255,255),1)
        cv2.putText(frame,'Put your skin in the rectangle above and press s',(10,450),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,0),2,cv2.LINE_AA)
        HSVimage=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        res = np.hstack((frame,HSVimage))
        cv2.imshow("Image ", res)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            return find_lowest_pixel(HSVimage, (upper_left_coord,lower_righ_coord))
            break

def pythagorous_theorem(point1,point2):
        return math.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    ang-=90
    if ang < -70:
        ang=-70
    elif ang>70:
        ang==70
    return ang

def greatest_line_drawer(centroid,pts,frame):
        dist=0
        pnt=centroid
        for point in pts:
                if pythagorous_theorem(centroid,point)>dist:
                        pnt=point
                        dist=pythagorous_theorem(centroid,point)
        cv2.line(frame,centroid,pnt,(255,0,0),10)
        new_pointx=frame.shape[1]
#        if centroid[1]-pnt[1]<0:
#                new_pointx*=-1
        angle=getAngle(pnt,centroid,(new_pointx,centroid[1]))
        cv2.line(frame,centroid,(new_pointx,centroid[1]),(255,0,0),10)
        cv2.putText(frame,str(int(angle)),(10,450),cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,0,0),2,cv2.LINE_AA)
        return int(angle)

def angle_finder(cap,skin_value,port):
    while(True):
        ret, frame = cap.read()
        frame=cv2.GaussianBlur(frame,(11,11),11)
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame=cv2.inRange(frame,skin_value[0],skin_value[1])#-50,255,cv2.THRESH_BINARY)

        kernel = np.ones((5,5),np.uint64)
        close = cv2.morphologyEx(frame,cv2.MORPH_CLOSE, kernel)
        close = cv2.dilate(close,kernel,iterations = 5)

        close = cv2.Laplacian(close,cv2.CV_8UC1)
        angle=0
        contours,hierarchy = cv2.findContours(close,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours)!=0:
                cnt = contours[0]
                M = cv2.moments(cnt)
                if M['m00']!=0:
                        centroid_x = int(M['m10']/M['m00'])
                        centroid_y = int(M['m01']/M['m00'])
                        cv2.circle(close,(centroid_x,centroid_y),10,[100,0,0],-1)
                        leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                        rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
                        topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                        bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
                        cv2.circle(close,leftmost,10,[100,0,0],-1)
                        cv2.circle(close,rightmost,10,[100,0,0],-1)
                        cv2.circle(close,topmost,10,[100,0,0],-1)
                        cv2.circle(close,bottommost,10,[100,0,0],-1)
                        angle=greatest_line_drawer((centroid_x,centroid_y),(topmost,bottommost,leftmost,rightmost),close)
        cv2.imshow("close",close)
        for i in range(8,16):
        #        wrapper(port,['i',[8,angle,9,angle,10,angle,11,angle,12,angle,13,angle,14,angle,15,angle],0.002])#....wrapper(['k',['k','balance'],0])
                wrapper(port,['m',[i,angle],0.005])#....wrapper(['k',['k','balance'],0])
#                port.write('m{} {}'.format(i,angle))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():

    port=Port_Opener("UsbSerial");
    time.sleep(2)
    cap = cv2.VideoCapture(0)
    skin_values=skin_finder(cap);
    cv2.destroyAllWindows()
    angle_finder(cap,skin_values,port);
    cap.release()
    cv2.destroyAllWindows()

main()