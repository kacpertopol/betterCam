#!/usr/bin/env python

import argparse
import configparser
import cv2
import os
import numpy
import sys

class camData:

    def show(self , frame):
        cv2.imshow(self.name , frame)

    def get(self):
        ret, frame = self.cap.read()
        if(ret):
            if((not self.matrix is None) and (not self.distortion is None)):
                # sauce: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
                h,  w = frame.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.matrix, self.distortion, (w,h), 1, (w,h))
                frame = cv2.undistort(frame, self.matrix, self.distortion, None, newcameramtx)
                if(self.crop):
                    x, y, w, h = roi
                    frame = frame[y:y+h, x:x+w]
            #print(frame.shape)
            if(\
                self.res[1] != frame.shape[0] or \
                self.res[0] != frame.shape[1] or \
                frame.shape[0] != self.white.shape[0] or \
                frame.shape[1] != self.white.shape[1]\
                ):
                self.res[1] = frame.shape[0]
                self.res[0] = frame.shape[1]
                self.ones = numpy.ones((self.res[1] , self.res[0]) , numpy.uint8)
                self.black = 0 * self.ones
                self.white = 255 * self.ones
                self.whitef32 = self.white.astype("float32")
            return frame
        else:
            return None

    def nextCam(self):
        if(len(self.cameras) != 0):

            self.current_cam = (self.current_cam + 1) % (len(self.cameras) + 1)

            cam = None
            if(self.current_cam < len(self.cameras)):
                cam = self.cameras[self.current_cam]

            # for undistorting
            self.matrix = None
            self.distortion = None
            
            # getting camera
            if(cam == None):
                self.camera = 0
            else:
                self.camera = int(self.config[cam]["number"])
                if("matrix" in self.config[cam]):
                    self.matrix = numpy.array(list(map(lambda x : float(x) , self.config[cam]["matrix"].split()))).reshape((3 , 3))
                if("distortion" in self.config[cam]):
                    self.distortion = numpy.array(list(map(lambda x : float(x) , self.config[cam]["distortion"].split()))).reshape((1 , 5))

            self.crop = False

            if(not cam is None):
                if("crop" in self.config[cam]):
                    self.crop = self.config[cam]["crop"].strip().lower() == "true"

            self.cap.release()
            self.cap = cv2.VideoCapture(self.camera)

            if(cam == None):
                self.res = [int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) , int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
            else:
                self.res = list(map(lambda x : int(x) , self.config[cam]["aspectratio"].split("x")))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
            
            self.m_avg = None
    
    def __init__(self , cam = None , sve = None):

        # script directory
        self.script_path = os.path.dirname(os.path.realpath(__file__)) #REGULAR_VERSION#
        #PYINSTALLER_VERSION#self.script_path = os.path.dirname(os.path.realpath(sys.executable)) 

        self.infoImage = cv2.imread(os.path.join(self.script_path , "info.png"))

        # reading configuration file 
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.script_path , "betterCam_config"))
       
        self.save_dir = os.getcwd()
        if(not sve is None):
            self.save_dir = sve
        elif("paths" in self.config):
            if("save" in self.config["paths"]):
                self.save_dir = self.config["paths"]["save"]

        self.buff = int(self.config["perspectiveMatrix"]["buffer"])
        
        self.k_pix = int(self.config["fragment"]["k_pix"])
        self.f_buff = int(self.config["smooth"]["f_buff"])
        self.l_col = float(self.config["levels1"]["l_col"])

        self.cameras = []
        for k in self.config:
            if(\
                    k != "DEFAULT" and \
                    k != "perspectiveMatrix" and \
                    k != "levels1" and \
                    k != "fragment" and \
                    k != "paths" and \
                    k != "smooth"):
                self.cameras.append(k)
        self.current_cam = 0

        if(cam in self.cameras):
            self.current_cam = self.cameras.index(cam)

        # for undistorting
        self.matrix = None
        self.distortion = None

        # getting camera
        if(cam == None):
            self.camera = 0
        else:
            self.camera = int(self.config[cam]["number"])
            if("matrix" in self.config[cam]):
                self.matrix = numpy.array(list(map(lambda x : float(x) , self.config[cam]["matrix"].split()))).reshape((3 , 3))
            if("distortion" in self.config[cam]):
                self.distortion = numpy.array(list(map(lambda x : float(x) , self.config[cam]["distortion"].split()))).reshape((1 , 5))

        self.crop = False

        if(not cam is None):
            if("crop" in self.config[cam]):
                self.crop = self.config[cam]["crop"].strip().lower() == "true"

        self.cap = cv2.VideoCapture(self.camera)

        if(cam == None):
            self.res = [int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) , int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
        else:
            self.res = list(map(lambda x : int(x) , self.config[cam]["aspectratio"].split("x")))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])

        # perspective matrix

        self.m_avg = None
        
        # window for cv
        if(cam == None):
            self.name = "frame"
            cv2.namedWindow('frame' , cv2.WINDOW_GUI_NORMAL)
        else:
            self.name = cam
            cv2.namedWindow(cam , cv2.WINDOW_GUI_NORMAL)

        # for freazing
        self.freeze = False
        self.ret = None
        self.frame = None

        # for denoising 
        self.ones = numpy.ones((self.res[1] , self.res[0]) , numpy.uint8)
        self.black = 0 * self.ones
        self.white = 255 * self.ones
        self.whitef32 = self.white.astype("float32")
        
        self.blur_kernel = numpy.ones((self.k_pix , self.k_pix) , dtype = numpy.float32) 
        self.blur_kernel = self.blur_kernel / numpy.sum(self.blur_kernel.flatten())

        # list of perspecive matrixes
        self.m_list = []

        # list of frames for smoothing
        self.frame_buff = []
        self.avg = False

        # points surrounfing the QR code available
        self.got_points = False

        # points surrounfing the QR code
        self.pointsglob = None

        # aruco markers
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
        self.parameters =  cv2.aruco.DetectorParameters_create()

def applyDenoise(warped , aux):

    if(warped is None):
        return (warped , aux)

    hls = cv2.cvtColor(warped , cv2.COLOR_BGR2HLS)

    gray = cv2.cvtColor(warped , cv2.COLOR_BGR2GRAY) 
    gray = 255 - gray
    gray = gray.astype("float32")

    gray[0:3 , :] = 0.0
    gray[gray.shape[0] - 3 : gray.shape[0] , :] = 0.0
    gray[: , 0:3] = 0.0
    gray[: , gray.shape[1] - 3 : gray.shape[1]] = 0.0

    blured_gray = cv2.filter2D(gray , -1 , aux.blur_kernel)
    
    stdv = numpy.sqrt(numpy.mean(((gray - blured_gray) * (gray - blured_gray)).flatten()))

    h_res = hls[: , : , 0]
    l_res = numpy.where((gray - blured_gray) > aux.l_col * stdv , hls[: , : , 1] , aux.white)
    s_res = hls[: , : , 2]
    

    warped = cv2.cvtColor(cv2.merge((h_res , l_res , s_res)) , cv2.COLOR_HLS2BGR)
    
    return (warped , aux)

# TODO
#def applyContours(warped , aux):
#
#    hls = cv2.cvtColor(warped , cv2.COLOR_BGR2HLS)
#
#    gray = cv2.cvtColor(warped , cv2.COLOR_BGR2GRAY) 
#    gray = 255 - gray
#    gray = gray.astype("float32")
#
#    gray[0:3 , :] = 0.0
#    gray[gray.shape[0] - 3 : gray.shape[0] , :] = 0.0
#    gray[: , 0:3] = 0.0
#    gray[: , gray.shape[1] - 3 : gray.shape[1]] = 0.0
#
#    blured_gray = cv2.filter2D(gray , -1 , aux.blur_kernel)
#    
#    stdv = numpy.sqrt(numpy.mean(((gray - blured_gray) * (gray - blured_gray))))
#
#    l_res = numpy.where((gray - blured_gray) > aux.l_col * stdv , aux.white , aux.black)
#
#    contours, hierar = cv2.findContours(l_res, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#
#    # TODO fix hierarchy
#
#    h_res = hls[: , : , 0]
#    l_res = hls[: , : , 1]
#    s_res = hls[: , : , 2]
#
#    h_new = 0 * aux.ones
#    l_new = 255 * aux.ones
#    s_new = 0 * aux.ones
#
#    for icr in range(len(contours)):
#        mask = 0.0 * aux.ones
#        cv2.drawContours(mask , contours , icr , 1.0 , -1 , hierarchy = hierar , maxLevel = 0)
#        mask_volume = numpy.sum(mask.flatten())
#        h_avg = numpy.sum((mask * h_res)) / mask_volume
#        l_avg = numpy.sum((mask * l_res)) / mask_volume
#        s_avg = numpy.sum((mask * s_res)) / mask_volume
#        cv2.drawContours(h_new , contours , icr , int(h_avg) , -1 , hierarchy = hierar , maxLevel = 0)
#        cv2.drawContours(l_new , contours , icr , int(l_avg) , -1 , hierarchy = hierar , maxLevel = 0)
#        cv2.drawContours(s_new , contours , icr , int(s_avg) , -1 , hierarchy = hierar , maxLevel = 0)
#
#    wh = cv2.cvtColor(cv2.merge((h_new , l_new , s_new)) , cv2.COLOR_HLS2BGR)
#
#    return (wh , aux)

def getFrame(frame , aux):
    fr = aux.get()

    if(fr is None):
        return (frame , aux)
    
    return (fr , aux)

def getFrameHelp(frame , aux):
    fr = aux.get()

    if(fr is None):
        return (frame , aux)

    if(not fr is None):
        #if(fr.shape[0] > 400 and fr.shape[1] > 400):
        x_of = int((fr.shape[0] - 400) / 2)
        y_of = int((fr.shape[1] - 400) / 2)
        fr[x_of : x_of + 400 , y_of : y_of + 400 , :] = aux.infoImage[: , : , :]
        cv2.putText(fr , 
                "To configure change 'betterCam_config' in:" , 
                (20 , fr.shape[0] - 25) , 
                fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL ,
                fontScale = 0.6,
                color = (125 , 125 , 125),
                thickness = 1)
        cv2.putText(fr , 
                "'" + aux.script_path + "'." , 
                (20 , fr.shape[0] - 10) , 
                fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL ,
                fontScale = 0.6,
                color = (125 , 125 , 125),
                thickness = 1)
        return (fr , aux)
    else:
        return None

def getFrameAvg(frame , aux):
    warped = aux.get()

    if(warped is None):
        return (warped , aux)

    aux.frame_buff.append(warped)
    if(len(aux.frame_buff) > aux.f_buff):
        aux.frame_buff.pop(0)
   
    smooth = numpy.zeros(warped.shape , numpy.float32)

    for f in aux.frame_buff:
        smooth = smooth + f

    smooth = smooth / len(aux.frame_buff)
    smooth = smooth.astype(warped.dtype)
    warped = smooth
    return (warped , aux)

def doNothing(warped , aux):
    return (warped , aux)

def invertColors(frame , aux):

    if(frame is None):
        return (frame , aux)
    
    warped = 255 - frame
    return (warped , aux)

def getMarkers(frame , aux):

    if(frame is None):
        return (frame , aux)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aux.aruco_dict, parameters=aux.parameters)
   
    pts = None

    ok = True
    
    if(len(corners) == 4):
        allids = [0 , 1 , 2 , 3]
        pts = [None , None , None , None]
        for i in range(4):
            if(ids[i][0] <= 3 and ids[i][0] >= 0):
                pts[ids[i][0]] = [
                        (int(corners[i][0][0][0]) , int(corners[i][0][0][1])) ,
                        (int(corners[i][0][1][0]) , int(corners[i][0][1][1])) ,
                        (int(corners[i][0][2][0]) , int(corners[i][0][2][1])) ,
                        (int(corners[i][0][3][0]) , int(corners[i][0][3][1]))
                        ];

        ok = ok and (not None in pts)
    else:
        ok = False

    # update matrix
    if(ok):
        aux.pointsglob = pts
        src = numpy.array([aux.pointsglob[0][2] , aux.pointsglob[1][3] , aux.pointsglob[3][0] , aux.pointsglob[2][1]] , numpy.float32)
        dst = numpy.array([[frame.shape[1] , frame.shape[0]] , [0.0 , frame.shape[0]] , [0.0 , 0.0] , [frame.shape[1] , 0.0]] , numpy.float32)
        m = cv2.getPerspectiveTransform(src , dst)
        aux.m_list.append(m)
        if(len(aux.m_list) > aux.buff):
            aux.m_list.pop(0)
        aux.m_avg = numpy.zeros(m.shape , dtype = m.dtype)
        for mm in aux.m_list:
            aux.m_avg = aux.m_avg + mm
        aux.m_avg = aux.m_avg / float(len(aux.m_list))
    
    if(aux.m_avg is None):
        return (frame , aux)
    else:
        warped = cv2.warpPerspective(frame , aux.m_avg , (frame.shape[1] , frame.shape[0]))
        return (warped , aux)

def main(args):
    parser = argparse.ArgumentParser(description = """
    Use web cam as blackboard.

    Keyboard shortcuts:

    h - print help information;
    q - quit;
    s - save frame to png file;
    p - pause image;
    w - display camera picture directly;
    i - using averaged camera frames, zoom to the inside of ARUCO markers, denoise and invert colors;
    d - using averaged camera frames, zoom to the inside of ARUCO markers, denoise;
    o - using regular camera frames, zoom to the inside of ARUCO markers, denoise and invert colors;
    f - using regular camera frames, zoom to the inside of ARUCO markers, denoise; 
    r - using averaged frames, zoom to the inside of ARUCO markers;
    t - using regular frames, zoom to the inside of ARUCO markers; 
    y - using averaged frames, zoom to the inside of ARUCO markers, invert colors;
    u - using regular frames, zoom to the inside of ARUCO markers, invert colors; 
    + - increase threshold for denoising;
    - - decrease threshold for denoising;
""")
    parser.add_argument("--camera" , "-c" , help = "Camera to use. Each camera name should be a section in the config file with an associated number and aspectratio.")
    parser.add_argument("--save" , "-s" , help = "Path to directory for saving frames.")
    args = parser.parse_args(args) 
   
    mainAux = camData(cam = args.camera , sve = args.save)
    tools = [getFrameHelp]
    storedFrame = None
    frame = None
    pauseAll = False

    # main loop

    try: 
        while(True):

            if(not pauseAll):

                for t in tools:
                    frame , mainAux = t(frame , mainAux)

                    if(frame is not None):
                        mainAux.show(frame)

            key = cv2.waitKey(1)
            if(key == ord('q')):
                break
            elif(key == ord('s')):
                maxPng = 0
                for f in os.listdir(mainAux.save_dir):
                    if(f[-4:] == ".png" and f[:-4].isdigit() and len(f) == 8):
                        if(int(f[:-4]) > maxPng):
                            maxPng = int(f[:-4])
                cv2.imwrite(os.path.join(mainAux.save_dir , str(maxPng + 1).zfill(4) + ".png") , frame)
            elif(key == ord('w')):
                # operations performed once:
                mainAux.m_avg = None
                mainAux.m_list = []
                # operations performed in each loop:
                tools = [getFrame]
            elif(key == ord('h')):
                # operations performed once:
                mainAux.m_avg = None
                mainAux.m_list = []
                # operations performed in each loop:
                tools = [getFrameHelp]
            elif(key == ord('i')):
                # operations performed in each loop:
                tools = [getFrameAvg , getMarkers , applyDenoise , invertColors]
            elif(key == ord('d')):
                # operations performed in each loop:
                tools = [getFrameAvg , getMarkers , applyDenoise]
            elif(key == ord('r')):
                # operations performed in each loop:
                tools = [getFrameAvg , getMarkers]
            elif(key == ord('y')):
                # operations performed in each loop:
                tools = [getFrameAvg , getMarkers , invertColors]
            elif(key == ord('o')):
                # operations performed in each loop:
                tools = [getFrame , getMarkers , applyDenoise , invertColors]
            elif(key == ord('t')):
                # operations performed in each loop:
                tools = [getFrame , getMarkers]
            elif(key == ord('u')):
                # operations performed in each loop:
                tools = [getFrame , getMarkers , invertColors]
            elif(key == ord('f')):
                # operations performed in each loop:
                tools = [getFrame , getMarkers , applyDenoise]
            elif(key == ord('p')):
                # operations performed once:
                pauseAll = not pauseAll
            elif(key == ord('9')):
                # operations performed once:
                storedFrame = frame
            elif(key == ord('0')):
                if(not storedFrame is None):
                    # operations performed once:
                    frame = storedFrame
                    # operations performed in each loop:
                    tools = [doNothing]
            elif(key == ord('n')):
                # operations performed once:
                mainAux.nextCam() 
            elif(key == ord('+')):
                # operations performed once:
                mainAux.l_col += 0.1
            elif(key == ord('-')):
                # operations performed once:
                mainAux.l_col -= 0.1
                if(mainAux.l_col < 0.2):
                    mainAux.l_col = 0.2

    finally:

        mainAux.cap.release()
        cv2.destroyAllWindows()

