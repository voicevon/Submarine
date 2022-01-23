#!/usr/bin/env python3

from camera.elements_jetson import ElementJetson
from gi.repository import Gst
import numpy
import cv2
import cvzone   #pip3 install cvzone
# from cvzone.SelfiSegmentationModule import SelfiSegmentation




frame = None
frame_laser_on = None
frame_laser_off = None
# segmentor = SelfiSegmentation()                     

class AppOpenCV:
    cv_counter = 0
    window_title="OpenCV"

    # def __init__(self) -> None:
    #     self.window_title="OpenCV"

    @staticmethod
    def gst_to_opencv(sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()
        format = caps.get_structure(0).get_value('format')
        height = caps.get_structure(0).get_value('height')
        width = caps.get_structure(0).get_value('width')
        buffer_size = buf.get_size()
        # print ("format, width, height, buffer_size =  ", format, width, height, buffer_size)
        arr = numpy.ndarray(
            (height, width, 4),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=numpy.uint8)
        # arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        return arr

    @staticmethod
    def new_buffer(sink, data):
        AppOpenCV.cv_counter += 1
        if AppOpenCV.cv_counter < 1:
            return Gst.FlowReturn.OK
        AppOpenCV.cv_counter = 0  
        global frame
        sample = sink.emit("pull-sample")
        frame = AppOpenCV.gst_to_opencv(sample)
        # This doesn't work, Might because threading
        # if image_arr is not None:   
        #     cv2.imshow("appsink image arr", image_arr)
        #     cv2.waitKey(1)  

        return Gst.FlowReturn.OK

    @staticmethod
    def CreatePiplineBranch(pipeline, tee):
        # https://gist.github.com/cbenhagen/76b24573fa63e7492fb6
        # https://stackoverflow.com/questions/10403588/adding-opencv-processing-to-gstreamer-application
        # http://lifestyletransfer.com/how-to-use-gstreamer-appsink-in-python/
        # https://forums.developer.nvidia.com/t/feeding-nv12-into-opencv2/167626
        # https://forums.developer.nvidia.com/t/convert-nv12-to-rgb-in-deepstream-pipeline/169957/8
        # https://gist.github.com/CasiaFan/684ec8c36624fb5ff61360c71ee9e4ec
        #       https://gist.github.com/Tutorgaming/55490ac88a3d91302be1d8fd44ac8055

        # nvosd_cv = VideoCenter.make_nvosd("osd_cv")
        # transform_cv = VideoCenter.make_nvtransform("transform_cv")
        appsink = ElementJetson.make_app_sink()
        pipeline.add(appsink)
        # VideoCenter.pipeline.add(nvosd_cv)
        # VideoCenter.pipeline.add(transform_cv)
        nvvidconv = ElementJetson.make_nvvidconv("nvvidconv_cv")
        pipeline.add(nvvidconv)
        # videorate=Gst.ElementFactory.make("videorate","videorate")
        # if not videorate:
        #     print(" Unable to create videorate......")
        #     time.sleep(10)
        # VideoCenter.pipeline.add(videorate)


        source_pad = tee.get_request_pad('src_4')
        if not source_pad:
            print("   Unable to get_request_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")

        # sink_pad = videorate.get_static_pad("sink")  
        sink_pad = nvvidconv.get_static_pad("sink")  
        if not sink_pad:
            print("   Unable to get_static_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        a = source_pad.link(sink_pad)
        if a != Gst.PadLinkReturn.OK:
            print("output to screen link      source_pad.link(sinkpad)= ", a)
        # videorate.set_property("rate",1)
        # b=c=videorate.link(nvvidconv)
        # a = tee.link(q1) 
        # b = nvvidconv.link(nvvidconv)
        # nvvidconv.set_property("format")
        # caps = Gst.caps_from_string("video/x-raw,format=BGRA,width=640,height=480")
        # nvvidconv.set_property("caps", caps)
        

        appsink.set_property("max-buffers", 2)
        appsink.set_property("drop", True)
        # # sink.set_property("sync", False)
        # caps = Gst.caps_from_string("video/x-raw, format=(string){BGR, GRAY8}; video/x-bayer,format=(string){rggb,bggr,grbg,gbrg}")
        caps = Gst.caps_from_string("video/x-raw,format=RGBA,width=640,height=480")
        # caps = Gst.caps_from_string("video/x-raw,format=RGBA,width=640,height=480 framerate=1/5")
        # caps = Gst.caps_from_string("video/x-raw,format=BGR,width=640,height=480")
        appsink.set_property("caps", caps)
        appsink.set_property("emit-signals", True)
        appsink.set_property("async", False)
        appsink.connect("new-sample", AppOpenCV.new_buffer, appsink)   


        b=c=d=e = nvvidconv.link(appsink)
        # d = nvosd_cv.link(transform_cv)
        # e = transform_cv.link(appsink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>> To opencv links   ", a,b,"  c= ",c,d,e)
        # time.sleep(6) 
        AppOpenCV.CreateHsvAdjuster()

    @staticmethod
    def CreateHsvAdjuster():
        cv2.namedWindow("adjuster")
        cv2.moveWindow("adjuster",100,0)

        cv2.createTrackbar("lowH","adjuster",109,180, AppOpenCV.callback_do_nothing)
        cv2.createTrackbar("upH","adjuster",145,180,AppOpenCV.callback_do_nothing)
        cv2.createTrackbar("lowS","adjuster",0,255,AppOpenCV.callback_do_nothing)
        cv2.createTrackbar("upS","adjuster",190,255,AppOpenCV.callback_do_nothing)
        cv2.createTrackbar("lowV","adjuster",198,255,AppOpenCV.callback_do_nothing)
        cv2.createTrackbar("upV","adjuster",255,255,AppOpenCV.callback_do_nothing)        

    @staticmethod
    def callback_do_nothing(value):
            pass

    @staticmethod
    def GetHsvRange():
        lowH = cv2.getTrackbarPos("lowH", "adjuster")
        upH = cv2.getTrackbarPos("upH", "adjuster")
        lowS = cv2.getTrackbarPos("lowS", "adjuster")
        upS = cv2.getTrackbarPos("upS", "adjuster")
        lowV = cv2.getTrackbarPos("lowV", "adjuster")
        upV = cv2.getTrackbarPos("upV", "adjuster")
        return [lowH,lowS,lowV], [upH,upS,upV]

    @staticmethod
    def ShowHsv(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        cv2.imshow("h",h)
        cv2.imshow("s",s)
        cv2.imshow("v",v)

    @staticmethod
    def ProcessCvZone(frame):
        global segmentor
        imgForeground = segmentor.removeBG(frame,(255.0,0))
        cv2.imshow("cvzone", imgForeground)

    @staticmethod
    def ProcessFrame(laser_is_on):
        global frame
        global frame_laser_on
        global frame_laser_off
        cv2.waitKey(1000)
        if frame is None:
            return
        
        # AppOpenCV.ShowHsv(frame)
        AppOpenCV.ProcessCvZone(frame)
        return

        cv2.imshow("frame",frame)
        ksize = (2,2)
        blur = cv2.blur(frame, ksize) 
        cv2.imshow('blur',blur)

        if laser_is_on:
            frame_laser_on = blur
            
        else:
            frame_laser_off = blur

        if frame_laser_off is None:
            return
        if frame_laser_on is None:
            return
        print("diff..............................")
        # https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
        cv2.imshow("on", frame_laser_on)
        cv2.imshow("off", frame_laser_off)
        diff = frame_laser_on - frame_laser_off
        cv2.imshow("diff", diff)
        frame = None
        return


        if frame is not None:   
            # print("-----",image_arr,"----------------")
            ksize = (2,2)
            blur = cv2.blur(frame, ksize) 
            cv2.imshow('blur',blur)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            if False:
                red, green, blue = cv2.split(blur)
                cv2.imshow("red",red)
                cv2.imshow("green",green)
                cv2.imshow("blue",blue)
                lower_red = numpy.array([210])
                upper_red = numpy.array([255])
                
                mask = cv2.inRange(red, lower_red, upper_red)
                res = cv2.bitwise_and(blur,blur, mask= mask)

                # cv2.imshow(AppOpenCV.window_title, frame)
                # # cv2.imshow("hsv",hsv)
                # cv2.imshow('blur',blur)
                cv2.imshow('mask',mask)
                cv2.imshow('result',res)
            low, up = AppOpenCV.GetHsvRange()
            low_bound = numpy.array(low)
            up_bound = numpy.array(up)
            if laser_is_on:
                mask_on = cv2.inRange(hsv,low_bound,up_bound)
                cv2.imshow("mask_on", mask_on)
            else:
                mask_off = cv2.inRange(hsv,low_bound,up_bound)
                cv2.imshow("mask_off", mask_off)
                # Cn = mask_on - mask_off


        frame = None
        cv2.waitKey(50)  