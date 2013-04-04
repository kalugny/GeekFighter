import imcompare
import cv
import time
import threading

def add_to_array(a, o, arr_len):
    a.insert(len(a), o)
    if len(a) > arr_len:
        a.pop(0)
    return a

def standHeight_change(pos):
    global CROUCH_RATIO
    CROUCH_RATIO = pos / 100.0

def hitDis_change(pos):
    global HIT_DISTANCE_RATIO
    HIT_DISTANCE_RATIO = pos / 100.0

def hitV_change(pos):
    global HIT_SPEED_RATIO
    HIT_SPEED_RATIO = pos / 100.0

def highHitDis_change(pos):
    global HIGH_HIT_RATIO
    HIGH_HIT_RATIO = pos / 100.0

def arr_len_change(pos):
    global arr_len
    arr_len = pos



# THREADS COMMUNICATION
pixBuf = []     # Shared data between webcam thread and main thread
newPix = False  # Inform main thread that new data is available
waitPix = True  # Inform webcam thread that new data is needed
lock = threading.Lock() # Resources lock

# These are the coordinates of the "inner" chessboard that FindChessboardCorners finds in Calibration_Grid2.png
screen_rect = ((140, 140), (940, 140), (140, 596), (940, 596))

def seperate_points(edge):

    arr = []
    for i in range(edge.height):
        for j in range(edge.width):            
            if 0.0 < cv.Get1D(edge, i * edge.width + j)[0]:
                arr.append([j, i])
    return arr

def findEdges(im):
        pos = 20
        # convert to grayscale
        gray = cv.CreateImage((im.width, im.height/2), 8, 1)
        edge1 = cv.CreateImage((im.width, im.height/2), 8, 1)
        edge2 = cv.CreateImage((im.width, im.height/2), 8, 1)
        edge = cv.CreateImage((im.width, im.height/2), 8, 1)
        cv.CvtColor(im, gray, cv.CV_BGR2GRAY)


        # create the trackbar

        # show the im
        cv.Smooth(gray, edge1, cv.CV_BLUR, 3, 3, 0)
        cv.Not(edge1, edge2)

        # run the edge dector on gray scale
        cv.Canny(edge2, edge, pos, pos * 3, 3)
        
        return edge


class MyFeed ( threading.Thread ):
        def __init__(self, capture):
            print "Starting webcam"
            self.cap = capture
            # Set width/height
##            cv.SetCaptureProperty( self.cap, cv.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
##            cv.SetCaptureProperty( self.cap, cv.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT )
            # Acquire one image, will throw one exeption in case of no webcam present
            self.running = True
            self.readyToStop = False
            threading.Thread.__init__ ( self )
        
        def stop(self):
            if self.running:
                # Normal stop
                self.running = False
                if self.cap == None:
                    print "No webcam to stop"
                else:
                    print "Waiting for webcam to stop...",
                    while not self.readyToStop:
                        pass
                    print "ok"
            else:
                # In case stop in called when already stopped
                return None
            
        def run ( self ):
            # Check if we may run
            if self.cap == None:
                print "No webcam present, aborting thread"
                return True
            # We may run!
            global pixBuf,newPix,waitPix,lock
            while self.running:
                if waitPix:
                    # Acquire image
                    img = cv.QueryFrame(self.cap)
                    # Do not process if abort in progress
                    if not self.running:
                        break
                    lock.acquire()
                    pixBuf = img
                    newPix = True
                    waitPix = False
                    lock.release()
                else:
                    time.sleep(0.05)

            # Once loop is finished, thread may be terminated
            self.readyToStop = True

def main():

    g_slider_pos = 45
    g_vertex_pos = 100
    g_width_pos = 2
    arr_len = 5
    global CROUCH_RATIO, HIT_DISTANCE_RATIO, HIT_SPEED_RATIO, HIGH_HIT_RATIO
    CROUCH_RATIO = 0.9
    HIT_DISTANCE_RATIO = 0.25
    HIT_SPEED_RATIO = 0.50
    HIGH_HIT_RATIO = 1.1
    
    cv.NamedWindow("win") # don't know if a '?' in the name is supported    
    cv.MoveWindow("win", -30, -20)


    cap = cv.CaptureFromCAM(0)

    calib_img = cv.LoadImage(r'images\Calibration_Grid3.png')
    cv.ShowImage("win", calib_img)

    # this is actually the dimensions of the "inner chessboard" (see FindChessboardCorners documentation)
    chessboard_dim = ( 8, 5 )

    # The camera's auto-focus needs time to adjust
    cv.WaitKey(5000)
    # For some reason the first capture doesn't get the chessboard (even though it's there 5 secs!) and the second one sometimes comes out blurry.
    whole_view = cv.QueryFrame(cap)
    whole_view = cv.QueryFrame(cap)

    # converting our image to grayscale. Might be unnecessary.
    whole_view_gs = cv.CreateImage(cv.GetSize(whole_view), whole_view.depth, 1)
    cv.CvtColor(whole_view, whole_view_gs, cv.CV_BGR2GRAY)
    found_all, corners = cv.FindChessboardCorners( whole_view_gs, chessboard_dim )

    if found_all:
        cv.DrawChessboardCorners( whole_view, chessboard_dim, corners, found_all )
    
    cv.ShowImage("win", whole_view);
    key = cv.WaitKey()

    # these are the bounding 4 points of the inner chessboard.
    bounding_rect = (corners[39], corners[32], corners[7], corners[0])
    
    transform_mat = cv.CreateMat(3, 3, cv.CV_32F)
    cv.GetPerspectiveTransform(bounding_rect, screen_rect, transform_mat)

    cv.WarpPerspective(whole_view, calib_img, transform_mat)

    cv.ShowImage("win", calib_img)

    cv.CreateTrackbar("Crouch", "win", CROUCH_RATIO * 100, 100, standHeight_change)
    cv.CreateTrackbar("HitDistance", "win", HIT_DISTANCE_RATIO * 100, 100, hitDis_change)
    cv.CreateTrackbar("HitSpeed", "win", HIT_SPEED_RATIO * 100, 100, hitV_change)
    cv.CreateTrackbar("HighHit", "win", HIGH_HIT_RATIO * 100, 200, highHitDis_change)
    cv.WaitKey()
    cv.Set(calib_img, cv.CV_RGB(255, 255, 255))
##    cv.ShowImage("win", calib_img)
##    cv.WaitKey()
    reference_img = cv.QueryFrame(cap)
    reference_img = cv.QueryFrame(cap)
    reference_img_warped = cv.CreateImage(cv.GetSize(calib_img), 8, 3)
    cv.WarpPerspective(reference_img, reference_img_warped, transform_mat, 0)
        
    cv.SaveImage('RefImg/RefImage2.jpg',reference_img_warped)
    reference_img_warped = cv.LoadImage('RefImg/RefImage2.jpg')
    cv.ShowImage("win", reference_img_warped)    

    cv.WaitKey()
    
    feed = MyFeed(cap)
    feed.start()

    prev_state = state = 'Idle'
    cms = []
    aps = []
    hs = []
    times = []
    base_height = 0
    while True :
        frame = None
        global pixBuf,newPix,waitPix,lock
        if newPix:
            lock.acquire()
            frame = pixBuf
            # Tell next frameStarted that this image was already taken into account
            newPix = False
            # Tell thread to acquire a new image
            waitPix = True
            lock.release()
        #frame = cv.QueryFrame(cap)
        #cv.ShowImage("win2", im)
        # warp the image to include only the synced part
        if frame:
            warped_frame = cv.CreateImage(cv.GetSize(calib_img), 8, 3)
            cv.WarpPerspective(frame, warped_frame, transform_mat, 0)        

            (c1, cm1, c2, cm2) = imcompare.findDifference(reference_img_warped, warped_frame, g_slider_pos, g_width_pos, g_vertex_pos)
            if c1 and c2:
                (ap1,ap2) = imcompare.get_action_points(c1, c2)

                cms = add_to_array(cms, cm1, arr_len)
                aps = add_to_array(aps, ap1, arr_len)
                hs = add_to_array(hs, imcompare.find_contour_height(c1), arr_len)
                times = add_to_array(times, time.time(), arr_len)
                warped_frame = imcompare.drawDifference(cv.GetSize(warped_frame),c1, cm1, ap1, c2, cm2, ap2)

                if len(cms) == arr_len:
                    xAP, yAP, vAP, vH, h = imcompare.get_motion_params(cms, aps, hs, times)
                    standHeight = base_height * CROUCH_RATIO
                    hitDis = base_height * HIT_DISTANCE_RATIO
                    hitV = base_height * HIT_SPEED_RATIO
                    highHitDis = base_height * HIGH_HIT_RATIO
                    state = imcompare.get_current_state(xAP, yAP, vAP, vH, h, prev_state, standHeight, hitDis, hitV, highHitDis)
                    if prev_state != state:
                        print state
                    prev_state = state

            cv.ShowImage('win', warped_frame)
            key = cv.WaitKey(10)
            if  key == 27:
                break
            if key == 32:
                if c1:
                    base_height = imcompare.find_contour_height(c1)
                    print base_height
    feed.stop()

if __name__ == "__main__":
    main()