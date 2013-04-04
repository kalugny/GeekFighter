import cv
import math
from array import array

def contour_iterator(contour, min_contour_vertex_count_to_dicard):
    while contour:
        if len(contour) > min_contour_vertex_count_to_dicard:
            yield contour
        contour = contour.h_next()

def find_center_of_mass(c):
    cMoments = cv.Moments(c)
    m00 = cv.GetSpatialMoment(cMoments, 0, 0)
    if m00 == 0:
        return 0, 0
    m01 = cv.GetSpatialMoment(cMoments, 0, 1)
    m10 = cv.GetSpatialMoment(cMoments, 1, 0)
    return (m10 / m00, m01 / m00)

def find_right_most_point(c):
    Vertices = sorted(c, key = lambda x:x[0])
    return Vertices[-1]

def find_left_most_point(c):
    Vertices = sorted(c, key = lambda x:x[0])
    return Vertices[0]

def find_contour_height(c):
    yCoor = sorted([y for (x,y) in c])
    return (yCoor[-1] - yCoor[0])

def get_motion_params(cMArr, aPArr, hArr, tTagArr):
    # Fuck, man, you got to put some comments here...
    vAPArr = sorted([(abs(cMArr[i + 1][0] - aPArr[i + 1][0]) - abs(cMArr[i][0] - aPArr[i][0])) / (tTagArr[i + 1] - tTagArr[i]) for i in range(len(cMArr) - 1)])
    xAPArr = sorted([abs(cMArr[i][0] - aPArr[i][0]) for i in range(len(aPArr))])
    yAPArr = sorted([cMArr[i][1] - aPArr[i][1] for i in range(len(aPArr))])
    vHArr = sorted([(hArr[i + 1] - hArr[i]) / (tTagArr[i + 1] - tTagArr[i]) for i in range(len(hArr) - 1)])
    midIndex = len(hArr) / 2
    return (xAPArr[midIndex], yAPArr[midIndex], vAPArr[midIndex], vHArr[midIndex], hArr[midIndex])

def get_current_state(xAP, yAP, vAP, vH, h, PreviousState = 'Idle', standHeight = 200, hitDis = 40, hitV = 100, highHitDis = 80):
    if PreviousState=='Idle' :
        if xAP > hitDis and vAP > hitV:
            if yAP > 0:
                return 'Punch'
            else:
                return 'Kick'
        if h > highHitDis and vH > hitV:
            return 'High Punch'
        if h < standHeight:
            return 'Crouch'
        return 'Idle'

    if PreviousState=='Crouch' :
        if h > standHeight:
            return 'Idle'
        if xAP > hitDis and vAP > hitV and h < standHeight:
            return 'Low Punch'
        return 'Crouch'

    if PreviousState=='Low Punch' :
        if (xAP < hitDis and h < standHeight) or vAP < -hitV:
            return 'Crouch'
        if  h > standHeight :
            return 'Idle'
        return 'Low Punch'

    if standHeight < h < highHitDis and (xAP < hitDis or vAP < -hitV):
        return 'Idle'
    if h < standHeight :
        return 'Crouch'
    else:
        return PreviousState
    

def drawDifference(img_size, c1, cm1, ap1, c2 = None, cm2 = None, ap2 = None):
    blue = cv.CV_RGB(0, 0, 255)
    red = cv.CV_RGB(255, 0, 0)

    really_final_image = cv.CreateImage(img_size, 8, 3)
    cv.Set(really_final_image, cv.CV_RGB(255, 255, 255))

    if c1:
        cv.DrawContours(really_final_image, c1, red, red, 0, cv.CV_FILLED)
        cv.Circle(really_final_image, cm1, 5, blue)
        cv.Circle(really_final_image, ap1, 5, blue)

    if c2:
        cv.DrawContours(really_final_image, c2, blue, blue, 0, cv.CV_FILLED)
        cv.Circle(really_final_image, cm2, 5, red)
        cv.Circle(really_final_image, ap2, 5, red)

    return really_final_image

def findDifference(image1, image2, threshold, widthLim, min_contour_vertex_count_to_dicard):

##    checkRes = 1.5
##    image1Cut = cv.GetCols(image1,checkRes-1,image1.width-checkRes+1)
##    image1Cut = cv.GetRows(image1Cut,checkRes-1,image1.height-checkRes+1)
    # initialize structures
    tempDiff = cv.CreateImage(cv.GetSize(image1), image1.depth, image1.channels)
    diffImage, redImg, greenImg, blueImg = [cv.CreateImage(cv.GetSize(image1), 8, 1) for i in range(4)]


##    for i in range(2 * checkRes - 2) :
##    image2CutCols = cv.GetCols(image2, i, i + image2.width - 2 * checkRes + 2)
##        for j in range(2 * checkRes - 2) :
##    image2Cut = cv.GetRows(image2CutCols, j, j + image2CutCols.height -2 * checkRes + 2)

    # find the minimum distance between     
    cv.AbsDiff(image1, image2, tempDiff)
    cv.Split(tempDiff, redImg, greenImg, blueImg, None)
    cv.Add(redImg, greenImg, diffImage)
    cv.Add(diffImage, blueImg, diffImage)

    # A little processing to get rid of line-like noise
    finalImage = cv.CloneImage(diffImage)
    finalImage = cv.GetCols(finalImage, widthLim - 1, finalImage.width - widthLim + 1)
    finalImage = cv.GetRows(finalImage, widthLim - 1, finalImage.height - widthLim + 1)
    for i in range(2 * widthLim - 2):
        finalImageCutCols = cv.GetCols(diffImage, i, i + diffImage.width - 2 * widthLim + 2)
        for j in range(2 * widthLim - 2) :
            finalImageCut = cv.GetRows(finalImageCutCols, j, j + finalImageCutCols.height - 2 * widthLim + 2)
            cv.Min(finalImage, finalImageCut, finalImage)
    
    cv.Threshold(finalImage, finalImage, threshold, 255, cv.CV_THRESH_BINARY)

    # Find contours
    stor = cv.CreateMemStorage()
    cont = cv.FindContours(finalImage,
            stor,
            cv.CV_RETR_LIST,
            cv.CV_CHAIN_APPROX_NONE,
            (0, 0))

    all_contours = [c for c in contour_iterator(cont, min_contour_vertex_count_to_dicard)]
    
    if len(all_contours) == 0:
        return 4 * [None]

    # find the two biggest area contours
    c2 = cm2 = None
    contours_and_areas = sorted([(c, cv.ContourArea(c)) for c in all_contours], key = lambda x: x[1])
    if len(contours_and_areas) > 1:
        c2, MaxArea2 = contours_and_areas[-2]
        
    c1, MaxArea1 = contours_and_areas[-1]

    # find centers of mass for the two contours    
    cm1 = find_center_of_mass(c1)

    if c2:
        cm2 = find_center_of_mass(c2)        

        # make sure the 2nd contour is always to the right of the first one
        if cm1[0] > cm2[0] :
            c1, c2 = c2, c1
            cm1, cm2 = cm2, cm1      

    return c1, cm1, c2, cm2

def get_action_points(c1, c2):
    actionPoint1 = actionPoint2 = None
    if c2:
        actionPoint2 = find_left_most_point(c2)
    if c1:
        actionPoint1 = find_right_most_point(c1)
    return actionPoint1, actionPoint2

##def change_contour_perspective(c, transform_mat):
##    c_vec = cv.CreateMat(len(c), 1, cv.CV_32FC2)
##    c_out = cv.CreateMat(len(c), 1, cv.CV_32FC2)
##    for i, p in enumerate(c):
##        cv.Set1D(c_vec, i, p)
##    cv.PerspectiveTransform(c_vec, c_out, transform_mat)
##    ret_val = []
##    for i in range(len(c)):
##        ret_val.append(cv.Get1D(c_out, i))
##    return ret_val, c_out

def change_pos(slider_pos):
    global g_slider_pos
    g_slider_pos = slider_pos

def change_vertex_pos(slider_pos):
    global g_vertex_pos 
    g_vertex_pos = slider_pos

def change_width_pos(slider_pos):
    global g_width_pos 
    g_width_pos = slider_pos




if __name__=='__main__':

    g_slider_pos = 45
    g_vertex_pos = 100
    g_width_pos = 6 
    
    cv.NamedWindow("Success?") # don't know if a '?' in the name is supported
    cv.CreateTrackbar("Threshold", "Success?", g_slider_pos, 255, change_pos)
    cv.CreateTrackbar("Vertex#", "Success?", g_vertex_pos, 500, change_vertex_pos)
    cv.CreateTrackbar("Widthlim", "Success?", g_width_pos, 20, change_width_pos)
    
    capture = cv.CaptureFromCAM(0)
    cv.WaitKey()
    im1 = cv.QueryFrame(capture)
    cv.SaveImage('RefImg/RefImage.jpg',im1)
    im1 = cv.LoadImage('RefImg/RefImage.jpg')
    cv.ShowImage("Success?", im1)
    cv.WaitKey()
    while True :
        im2 = cv.QueryFrame(capture)
        (c1, cm1, c2, cm2) = findDifference(im1, im2, g_slider_pos, g_width_pos, g_vertex_pos)
        (ap1,ap2) = get_action_points(c1, c2)
        im3 = drawDifference(cv.GetSize(im2),c1, cm1, ap1, c2, cm2, ap2)
        cv.ShowImage('Success?',im3)
        if cv.WaitKey(10) == 27:
            break