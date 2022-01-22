#!/usr/bin/env python3

from camera.elements_jetson import ElementJetson
from gi.repository import Gst


class ScreenPlayer:

    @staticmethod
    def CreatePipelineBranch(pipeline, tee, OSD_PROCESS_MODE,OSD_DISPLAY_TEXT):
        nvosd = ElementJetson.make_nvosd("nvosd",OSD_PROCESS_MODE, OSD_DISPLAY_TEXT)
        transform = ElementJetson.make_nvtransform("transform")
        q1 =  ElementJetson.make_queue("q1")
        nvsink = ElementJetson.make_nveglglessink()
        pipeline.add(nvsink)
        pipeline.add(q1)
        pipeline.add(nvosd)
        pipeline.add(transform)
        nvvidconv = ElementJetson.make_nvvidconv("nvvidconv")
        pipeline.add(nvvidconv)


        source_pad = tee.get_request_pad('src_2')
        if not source_pad:
            print("   Unable to get_request_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        sink_pad = q1.get_static_pad("sink")  
        if not sink_pad:
            print("   Unable to get_static_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        a = source_pad.link(sink_pad)
        if a != Gst.PadLinkReturn.OK:
            print("output to screen link      source_pad.link(sinkpad)= ", a)
        # a = tee.link(q1) 
        b = q1.link(nvvidconv)
        
        c=nvvidconv.link(nvosd)
        d=nvosd.link(transform)
        e=transform.link(nvsink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>> To screen links   ", a,b,c,d,e)
        # time.sleep(6)      