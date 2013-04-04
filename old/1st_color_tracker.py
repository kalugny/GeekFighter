#first color tracing experiment

import sys
from cv import *
# Create a Window
NamedWindow("Original Image", 1)
NamedWindow("Masked Image", 2)
# Connect to the camera
capture = CreateCameraCapture(1)
while 1:
    frame = QueryFrame(capture)
    ShowImage("Original Image", frame)
    color_mask = CreateImage(GetSize(frame),8, 1)
    color_mask_2 = CreateImage(GetSize(frame),8, 1)
    color_mask_temp = CreateImage(GetSize(frame),8, 1)
    B = CreateStructuringElementEx(10,10,9,9,CV_SHAPE_RECT)
    # Specify the minimum / maximum colors to look for:
    min_color = (50, 50, 150)
    max_color = (100, 100, 255)

    #Find the pixels within the color-range, and put the output in the color_mask
    InRangeS(frame, Scalar(*min_color), Scalar(*max_color), color_mask)
    MorphologyEx(color_mask, color_mask_2, color_mask_temp, B, CV_MOP_CLOSE, 1);
    storage = CreateMemStorage(0)
    ##c_count, contours =
    c_count = FindContours(color_mask, storage, CV_RETR_LIST, CV_CHAIN_APPROX_NONE)
    ##TODO: find an iterable object of contours to iterate upon, so contuors can be filtered and, boxed and presented
    for contour in  storage:
        print(c_count)
##    for contour in len(storage):
##   # Do some filtering
##    # Get the size of the contour
##        TARGET_SIZE = 30 #??
##        big_contours = []
##        size = abs(ContourArea(contour))
##        for contour in storage:
##            size = abs(ContourArea(contour))
##            if size > TARGET_SIZE:
##                big_contours.append(contour)
##    # Is convex (i think most of our shapes aren't so its not so relevant)
##    is_convex = CheckContourConvexity(contour)
##    # Find the bounding-box of the contour - important
##    bbox = BoundingRect( contour, 0 )
##    # Calculate the x and y coordinate of center
##    x, y = bbox.x+bbox.width*0.5, bbox.y+bbox.height*0.5

    ShowImage("Masked Image", color_mask)
    key = WaitKey(10)
    if key == 27: ##Escape key
      break 
##while 1:
##  # Grab the current frame from the camera
##  frame = QueryFrame(capture)
##  # Show the current image in MyWindow
##  ShowImage("Original Image", frame)
##  # Wait a bit and check any keys has been pressed
##  color_mask = CreateImage(GetSize(frame), IPL_DEPTH_8U, 1)
##  pile = frame
##  ShowImage("Masked Image", pile)
##  key = WaitKey(10)
##  if key == 27:
##      break 

### Create a 8-bit 1-channel image with same size as the frame
##color_mask = CreateImage(GetSize(frame), 8, 1)
##
### Specify the minimum / maximum colors to look for:
##min_color = (180, 20, 200)
##max_color = (255, 255, 255)
##
### Find the pixels within the color-range, and put the output in the color_mask
##InRangeS(frame, Scalar(*min_color), Scalar(*max_color), color_mask)
##
##storage = CreateMemStorage(0)
##c_count, contours = FindContours (color_mask, storage, d=CV_CHAIN_APPROX_NONE)
### Go trough each contour
##for contour in contours.hrange():
##   # Do some filtering
##    # Get the size of the contour
##    size = abs(ContourArea(contour))
##
##    # Is convex
##    is_convex = CheckContourConvexity(contour)
##    # Find the bounding-box of the contour
##    bbox = BoundingRect( contour, 0 )

##    # Calculate the x and y coordinate of center
##    x, y = bbox.x+bbox.width*0.5, bbox.y+bbox.height*0.5
   