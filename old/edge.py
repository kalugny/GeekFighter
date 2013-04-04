#! /usr/bin/env python

print "OpenCV Python version of edge"

import sys
import urllib2
import cv
from pprint import pprint
#from py

# some definitions
win_name = "Edge"
trackbar_name = "Threshold"

pos = 20

def calc_center_of_mass(points):
    

def seperate_points(edge):

    arr = []
    for i in range(edge.height):
        for j in range(edge.width):            
            if 0.0 < cv.Get1D(edge, i * edge.width + j)[0]:
                arr.append([i, j])
    return arr
    
    
def findEdges(im):
            # convert to grayscale
        gray = cv.CreateImage((im.width, im.height), 8, 1)
        edge1 = cv.CreateImage((im.width, im.height), 8, 1)
        edge2 = cv.CreateImage((im.width, im.height), 8, 1)
        edge = cv.CreateImage((im.width, im.height), 8, 1)
        cv.CvtColor(im, gray, cv.CV_BGR2GRAY)


        # create the trackbar

        # show the im
        cv.Smooth(gray, edge1, cv.CV_BLUR, 3, 3, 0)
        cv.Not(edge1, edge2)

        # run the edge dector on gray scale
        cv.Canny(edge2, edge, pos, pos * 3, 3)
        
        return edge
    
if __name__ == '__main__':
##    if len(sys.argv) > 1:
##        im = cv.LoadImage( sys.argv[1], cv.CV_LOAD_IMAGE_COLOR)
##    else:
##        url = 'https://code.ros.org/svn/opencv/trunk/opencv/samples/c/fruits.jpg'
##        filedata = urllib2.urlopen(url).read()
##        imagefiledata = cv.CreateMatHeader(1, len(filedata), cv.CV_8UC1)
##        cv.SetData(imagefiledata, filedata, len(filedata))
##        im = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)
    capture = cv.CaptureFromCAM(0)
        # create the window
    cv.NamedWindow(win_name, cv.CV_WINDOW_AUTOSIZE)

    while True:
        im = cv.QueryFrame(capture)

        edge = findEdges(im)    
        # create the output im
        col_edge = cv.CreateImage((im.width, im.height), 8, 3)


        # copy edge points
        cv.Copy(im, col_edge, edge)
        
        # show the im
        cv.ShowImage(win_name, edge)

        # wait a key pressed to end
        k = cv.WaitKey(5)
        if k == 32:
            break
 