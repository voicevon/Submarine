#!/usr/bin/env python3

from elements_jetson import ElementJetson
from gi.repository import Gst


class FileSaver:
    filesink = None

    @staticmethod
    def CreatePipilineBranch(pipeline: Gst.Pipeline, tee):
        # nvosd = VideoCenter.make_nvosd()
        # transform = VideoCenter.make_nvtransform()
        q2 = ElementJetson.make_queue("q2")
        pipeline.add(q2)
        nvvidconv_postosd = ElementJetson.make_nvvidconv("nvvideoconvert_post")
        caps = ElementJetson.make_caps()
        encoder = ElementJetson.make_encoder()        
        parse = ElementJetson.make_h264parse()
        # mp4mux = make_mp4mux()
        # filesink = make_file_sink()
        mkvmux = ElementJetson.make_mkvmux()
        FileSaver.filesink = ElementJetson.make_file_sink()
        FileSaver.filesink.set_property("location","~/tempvideo.mkv")
        FileSaver.filesink.set_property("async", False)
        # VideoCenter.pipeline.add(nvosd)
        # VideoCenter.pipeline.add(transform)
        pipeline.add(nvvidconv_postosd)
        pipeline.add(caps)
        pipeline.add(encoder)
        pipeline.add(parse)
        # pipeline.add(mp4mux)
        pipeline.add(mkvmux)
        pipeline.add(FileSaver.filesink)

        source_pad1 = tee.get_request_pad('src_1')
        if not source_pad1:
            print("   Unable to get_request_pad(1) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        sink_pad1 = nvvidconv_postosd.get_static_pad("sink")  
        if not sink_pad1:
            print("   Unable to get_static_pad(1) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        a = source_pad1.link(sink_pad1)   
        if a != Gst.PadLinkReturn.OK:
            print("outout to file link      source_pad.link(sinkpad)= ", a)

            # a = b = tee.link(q2)
        # c = q2.link(nvvidconv_postosd)
        b=c=d = nvvidconv_postosd.link(caps)
        e = caps.link(encoder)

        f = encoder.link(parse)
        # g = parse.link(mp4mux)
        # h = mp4mux.link(filesink)
        g = parse.link(mkvmux)
        h = mkvmux.link(FileSaver.filesink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  output to file links ",a,b,c,d,e,f,g,h)
        # time.sleep(2)  
    
    @staticmethod
    def UpdateFileLocation(path_name):
        FileSaver.filesink.set_property("location", path_name)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   File will be saved as ", path_name)

