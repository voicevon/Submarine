#!/usr/bin/env python3

# cd ~/Sumbrine/camera/
# python3 ds_main.py rtsp://admin:a@192.168.1.82:554 rtsp://admin:a@192.168.1.81 rtsp://admin:a@192.168.1.82   rtsp://admin:a@192.168.1.83 rtsp://admin:a@192.168.1.84 rtsp://admin:a@192.168.1.86

import sys
sys.path.append("../")
import pyds
from common.bus_call import bus_call
# from common.is_aarch_64 import is_aarch64
# import platform
import math
import time
from ctypes import *
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GObject, Gst, GstRtspServer, GLib
import configparser

import argparse

from common.FPS import GETFPS
import cv2
import numpy


fps_streams = {}

MAX_DISPLAY_LEN = 64
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 4000000
TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
OSD_PROCESS_MODE =  0
OSD_DISPLAY_TEXT =  1
pgie_classes_str =  ["Vehicle", "TwoWheeler", "Person", "RoadSign"]

image_arr = None

# tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
# and update params for drawing rectangle, object information etc.
class VideoCenter:
    pipeline = None  # Gst.Pipeline()
    recording_start_at = 0
    filesink = None
    cv_counter = 0

    def __init__(self) -> None:
        self.uris = list()
        for i in range(5):
            self.uris.append('')
        self.uris[0] = "rtsp://admin:a@192.168.1.81"
        self.uris[1] = "rtsp://admin:a@192.168.1.82"
        self.uris[2] = "rtsp://admin:a@192.168.1.83"
        self.uris[3] = "rtsp://admin:a@192.168.1.84"
        self.uris[4] = "rtsp://admin:a@192.168.1.86"
        # self.uris[5] = "rtsp://admin:a@192.168.1.86"

    def StartStop(self, cameras):
        for i in range(6):
            if cameras[i]:
                pass
            else:
                pass
    
    @staticmethod
    def tiler_src_pad_buffer_probe(pad,info,u_data):
        frame_number = 0
        num_rects = 0
        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            return

        # Retrieve batch metadata from the gst_buffer
        # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        l_frame = batch_meta.frame_meta_list
        while l_frame is not None:
            try:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            frame_number = frame_meta.frame_num
            l_obj = frame_meta.obj_meta_list
            num_rects = frame_meta.num_obj_meta
            obj_counter = {
                PGIE_CLASS_ID_VEHICLE:0,
                PGIE_CLASS_ID_PERSON:0,
                PGIE_CLASS_ID_BICYCLE:0,
                PGIE_CLASS_ID_ROADSIGN:0
            }
            while l_obj is not None:
                try:
                    # Casting l_obj.data to pyds.NvDsObjectMeta
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                obj_counter[obj_meta.class_id] += 1
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break
            print("Frame Number = ", frame_number, "Number of Objects = ",num_rects,"Vehicle_count = ",obj_counter[PGIE_CLASS_ID_VEHICLE],"Person_count = ",obj_counter[PGIE_CLASS_ID_PERSON])

            # Get frame rate through this probe
            fps_streams["stream{0}".format(frame_meta.pad_index)].get_fps()
            try:
                l_frame = l_frame.next
            except StopIteration:
                break

        return Gst.PadProbeReturn.OK



    @staticmethod
    def cb_newpad(decodebin, decoder_src_pad,data):
        print("In cb_newpad\n")
        caps = decoder_src_pad.get_current_caps()
        gststruct = caps.get_structure(0)
        gstname = gststruct.get_name()
        source_bin = data
        features = caps.get_features(0)

        # Need to check if the pad created by the decodebin is for video and not
        # audio.
        print("gstname = ",gstname)
        if gstname.find("video")!= -1:
            # Link the decodebin pad only if decodebin has picked nvidia
            # decoder plugin nvdec_*. We do this by checking if the pad caps contain
            # NVMM memory features.
            print("features = ",features)
            if features.contains("memory:NVMM"):
                # Get the source bin ghost pad
                bin_ghost_pad = source_bin.get_static_pad("src")
                if not bin_ghost_pad.set_target(decoder_src_pad):
                    sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")
            else:
                sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")

    @staticmethod
    def decodebin_child_added(child_proxy,Object,name,user_data):
        print("Decodebin child added:", name, "\n")
        if(name.find("decodebin") !=  -1):
            Object.connect("child-added",VideoCenter.decodebin_child_added,user_data)

    @staticmethod
    def create_source_bin(index,uri):
        print("Creating source bin")

        # Create a source GstBin to abstract this bin's content from the rest of the
        # pipeline
        bin_name = "source-bin-%02d" %index
        print(bin_name)
        nbin = Gst.Bin.new(bin_name)
        if not nbin:
            sys.stderr.write(" Unable to create source bin \n")

        # Source element for reading from the uri.
        # We will use decodebin and let it figure out the container format of the
        # stream and the codec and plug the appropriate demux and decode plugins.
        uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
        if not uri_decode_bin:
            sys.stderr.write(" Unable to create uri decode bin \n")
        # We set the input uri to the source element
        uri_decode_bin.set_property("uri",uri)
        # Connect to the "pad-added" signal of the decodebin which generates a
        # callback once a new pad for raw data has beed created by the decodebin
        uri_decode_bin.connect("pad-added", VideoCenter.cb_newpad,nbin)
        uri_decode_bin.connect("child-added", VideoCenter.decodebin_child_added,nbin)

        # We need to create a ghost pad for the source bin which will act as a proxy
        # for the video decoder src pad. The ghost pad will not have a target right
        # now. Once the decode bin creates the video decoder and generates the
        # cb_newpad callback, we will set the ghost pad target to the video decoder
        # src pad.
        Gst.Bin.add(nbin,uri_decode_bin)
        bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src",Gst.PadDirection.SRC))
        if not bin_pad:
            sys.stderr.write(" Failed to add ghost pad in source bin \n")
            return None
        return nbin


    @staticmethod
    def make_streammux(number_sources):
        print("Creating streamux \n ")
        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")
        streammux.set_property('live-source', 1)
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batch-size", number_sources)
        streammux.set_property("batched-push-timeout", 4000000)        
        return streammux
        
    @staticmethod
    def make_pgie(number_sources):
        print("Creating Pgie \n ")
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")
        pgie.set_property("config-file-path", "dstest1_pgie_config.txt")

        pgie_batch_size = pgie.get_property("batch-size")
        if pgie_batch_size !=  number_sources:
            print(
                "WARNING: Overriding infer-config batch-size",
                pgie_batch_size,
                " with number of sources ",
                number_sources,
                " \n",
            )
            pgie.set_property("batch-size", number_sources)        
        return pgie

    @staticmethod
    def make_tiler(number_sources):
        print("Creating tiler \n ")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            sys.stderr.write(" Unable to create tiler \n")
        tiler_rows = int(math.sqrt(number_sources))
        tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
        tiler.set_property("rows", tiler_rows)
        tiler.set_property("columns", tiler_columns)
        tiler.set_property("width", TILED_OUTPUT_WIDTH)
        tiler.set_property("height", TILED_OUTPUT_HEIGHT)        
        return tiler    

    @staticmethod
    def make_nvvidconv(name):
        print("Creating nvvidconv \n ")
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", name)
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvidconv \n")
        return nvvidconv

    @staticmethod
    def make_nvosd(name):
        print("Creating nvosd \n ")
        nvosd = Gst.ElementFactory.make("nvdsosd", name)
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")
        nvosd.set_property('process-mode',OSD_PROCESS_MODE)
        nvosd.set_property('display-text',OSD_DISPLAY_TEXT)        
        return nvosd

    @staticmethod
    def make_caps():
        # Create a caps filter
        caps = Gst.ElementFactory.make("capsfilter", "filter")
        caps.set_property(
            "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
        )
        return caps

    @staticmethod
    def make_rtppay():
        # Make the payload-encode video into RTP packets
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        print("Creating H264 rtppay")
        if not rtppay:
            sys.stderr.write(" Unable to create rtppay")
        return rtppay
        
    @staticmethod
    def make_encoder():
        # Make the encoder
        print("Creating H264 Encoder")
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        if not encoder:
            sys.stderr.write(" Unable to create encoder")
        encoder.set_property("bitrate", 4000000)
        encoder.set_property("preset-level", 1)
        encoder.set_property("insert-sps-pps", 1)
        encoder.set_property("bufapi-version", 1)
        return encoder

    @staticmethod
    def make_nvtransform(name):
        print("Creating nvtransform")
        transform = Gst.ElementFactory.make("nvegltransform",name)
        if not transform:
            sys.stderr.write("  Unable to create nvegltransform")
        return transform

    @staticmethod
    def make_mp4mux():
        print("Creating mp4mux")
        mux = Gst.ElementFactory.make("mp4mux","mp4mux")
        if not mux:
            sys.stderr.write("  Unable to create mp4mux")
        return mux

    @staticmethod
    def make_mkvmux():
        print("Creating mkvmux")
        mux = Gst.ElementFactory.make("matroskamux","matroskamux")
        if not mux:
            sys.stderr.write("  Unable to create matroskamux")
        return mux


    @staticmethod
    def make_h264parse():
        print("Creating H264 parse")
        parse = Gst.ElementFactory.make("h264parse","parse")
        if not parse:
            sys.stderr.write("  Unable to create h264parse")
        return parse

    @staticmethod
    def make_nveglglessink():
        print("Creating nveglessink")
        sink = Gst.ElementFactory.make("nveglglessink","nveglglesink")
        if not sink:
            sys.stderr.write("  Unable to create nveglglessink")
        return sink

    @staticmethod
    def make_udp_sink(updsink_port_num):
        # Make the UDP sink
        print("Creating udp sink")
        sink = Gst.ElementFactory.make("udpsink", "udpsink")
        if not sink:
            sys.stderr.write(" Unable to create udpsink")

        sink.set_property("host", "224.224.255.255")
        sink.set_property("port", updsink_port_num)
        sink.set_property("async", False)
        sink.set_property("sync", 1)
        sink.set_property("qos", 0)
        return sink
        
    @staticmethod
    def make_file_sink():
        print("Creating filesink")
        sink = Gst.ElementFactory.make("filesink", "filesink")
        if not sink:
            sys.stderr.write("  Unable to create filesink")
        return sink

    @staticmethod
    def make_app_sink():
        print("Creating appsink")
        sink = Gst.ElementFactory.make("appsink", "appsink")
        if not sink:
            sys.stderr.write("  Unable to create appsink")
        return sink        

    @staticmethod
    def make_tee():
        print("Creating tee")
        tee = Gst.ElementFactory.make("tee", "tee")
        if not tee:
            sys.stderr.write("  Unable to create tee")
        return tee

    @staticmethod
    def make_queue(name):
        print("Creating queue")
        q = Gst.ElementFactory.make("tee", name)
        if not q:
            sys.stderr.write("  Unable to create tee, name=", name)
        return q

    @staticmethod
    def link_output_screen(tee):
        nvosd = VideoCenter.make_nvosd("nvosd")
        transform = VideoCenter.make_nvtransform("transform")
        q1 =  VideoCenter.make_queue("q1")
        nvsink = VideoCenter.make_nveglglessink()
        VideoCenter.pipeline.add(nvsink)
        VideoCenter.pipeline.add(q1)
        VideoCenter.pipeline.add(nvosd)
        VideoCenter.pipeline.add(transform)
        nvvidconv = VideoCenter.make_nvvidconv("nvvidconv")
        VideoCenter.pipeline.add(nvvidconv)


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

    @staticmethod
    def link_ouput_file(tee):
        # nvosd = VideoCenter.make_nvosd()
        # transform = VideoCenter.make_nvtransform()
        q2 = VideoCenter.make_queue("q2")
        VideoCenter.pipeline.add(q2)
        nvvidconv_postosd = VideoCenter.make_nvvidconv("nvvideoconvert_post")
        caps = VideoCenter.make_caps()
        encoder = VideoCenter.make_encoder()        
        parse = VideoCenter.make_h264parse()
        # mp4mux = make_mp4mux()
        # filesink = make_file_sink()
        mkvmux = VideoCenter.make_mkvmux()
        VideoCenter.filesink = VideoCenter.make_file_sink()
        VideoCenter.filesink.set_property("location","~/tempvideo.mkv")
        VideoCenter.filesink.set_property("async", False)
        # VideoCenter.pipeline.add(nvosd)
        # VideoCenter.pipeline.add(transform)
        VideoCenter.pipeline.add(nvvidconv_postosd)
        VideoCenter.pipeline.add(caps)
        VideoCenter.pipeline.add(encoder)
        VideoCenter.pipeline.add(parse)
        # pipeline.add(mp4mux)
        VideoCenter.pipeline.add(mkvmux)
        VideoCenter.pipeline.add(VideoCenter.filesink)

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
        h = mkvmux.link(VideoCenter.filesink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  output to file links ",a,b,c,d,e,f,g,h)
        # time.sleep(2)        



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
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        return arr

    @staticmethod
    def new_buffer(sink, data):
        VideoCenter.cv_counter += 1
        if VideoCenter.cv_counter < 1:
            return Gst.FlowReturn.OK
        VideoCenter.cv_counter = 0  
        global image_arr
        sample = sink.emit("pull-sample")
        image_arr = VideoCenter.gst_to_opencv(sample)
        # if image_arr is not None:   
        #     # print("-----",image_arr,"----------------")
        #     cv2.imshow("appsink image arr", image_arr)
        #     cv2.waitKey(1)  

        return Gst.FlowReturn.OK

    @staticmethod
    def link_output_opencv(tee):
        # https://gist.github.com/cbenhagen/76b24573fa63e7492fb6
        # https://stackoverflow.com/questions/10403588/adding-opencv-processing-to-gstreamer-application
        # http://lifestyletransfer.com/how-to-use-gstreamer-appsink-in-python/
        # https://forums.developer.nvidia.com/t/feeding-nv12-into-opencv2/167626
        # https://forums.developer.nvidia.com/t/convert-nv12-to-rgb-in-deepstream-pipeline/169957/8
        # https://gist.github.com/CasiaFan/684ec8c36624fb5ff61360c71ee9e4ec
        #       https://gist.github.com/Tutorgaming/55490ac88a3d91302be1d8fd44ac8055

        # nvosd_cv = VideoCenter.make_nvosd("osd_cv")
        # transform_cv = VideoCenter.make_nvtransform("transform_cv")
        appsink = VideoCenter.make_app_sink()
        VideoCenter.pipeline.add(appsink)
        # VideoCenter.pipeline.add(nvosd_cv)
        # VideoCenter.pipeline.add(transform_cv)
        nvvidconv = VideoCenter.make_nvvidconv("nvvidconv_cv")
        VideoCenter.pipeline.add(nvvidconv)
        # videorate=Gst.ElementFactory.make("videorate","videorate")
        # if not videorate:
        #     print(" Unable to create videorate......")
        #     time.sleep(10)
        # VideoCenter.pipeline.add(videorate)


        source_pad = tee.get_request_pad('src_3')
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
        appsink.connect("new-sample", VideoCenter.new_buffer, appsink)   


        b=c=d=e = nvvidconv.link(appsink)
        # d = nvosd_cv.link(transform_cv)
        # e = transform_cv.link(appsink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>> To opencv links   ", a,b,"  c= ",c,d,e)
        # time.sleep(6) 
        
    @staticmethod
    def CreatePipline(uris, out_to_screen=True, out_to_file=True, out_to_opencv=True,out_to_rtsp=False):
        for i in range(0, len(uris)):
            fps_streams["stream{0}".format(i)] = GETFPS(i)
        number_sources = len(uris)

        GObject.threads_init()
        Gst.init(None)

        print("Creating Pipeline \n ")
        VideoCenter.pipeline = Gst.Pipeline()
        if not VideoCenter.pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")

        streammux = VideoCenter.make_streammux(number_sources)
        VideoCenter.pipeline.add(streammux)
        for i in range(number_sources):
            print("Creating source_bin ",i," \n ")
            uri_name = uris[i]
            source_bin = VideoCenter.create_source_bin(i, uri_name)
            if not source_bin:
                sys.stderr.write("Unable to create source bin \n")
            VideoCenter.pipeline.add(source_bin)
            padname = "sink_%u" %i
            sinkpad =  streammux.get_request_pad(padname)
            if not sinkpad:
                sys.stderr.write("Unable to create sink pad bin \n")
            srcpad = source_bin.get_static_pad("src")
            if not srcpad:
                sys.stderr.write("Unable to create src pad bin \n")
            srcpad.link(sinkpad)

        pgie = VideoCenter.make_pgie(number_sources)
        tiler = VideoCenter.make_tiler(number_sources)
        tee = VideoCenter.make_tee()


        print("Adding elements to Pipeline \n")
        # pipeline.add(pgie)
        VideoCenter.pipeline.add(tiler)
        VideoCenter.pipeline.add(tee)

        streammux.link(tiler)
        tiler.link(tee)

        if out_to_screen:
            videoCenter.link_output_screen(tee)

        if out_to_rtsp:
            updsink_port_num = 5400
            transform = VideoCenter.make_nvtransform()

            nvvidconv_postosd = VideoCenter.make_nvvidconv("nvvideoconvert_post_rtsp")
            caps = VideoCenter.make_caps()
            encoder = VideoCenter.make_encoder()        
            parse = VideoCenter.make_h264parse()
            rtppay  = VideoCenter.make_rtppay()
            udp_sink = VideoCenter.make_udp_sink(updsink_port_num)

            VideoCenter.pipeline.add(transform)
            VideoCenter.pipeline.add(nvvidconv_postosd)
            VideoCenter.pipeline.add(caps)
            VideoCenter.pipeline.add(encoder)
            VideoCenter.pipeline.add(parse)
            VideoCenter.pipeline.add(rtppay)
            VideoCenter.pipeline.add(udp_sink)

            streammux.link(nvvidconv)
            nvvidconv.link(tiler)
            tiler.link(nvvidconv_postosd)
            nvvidconv_postosd.link(caps)
            caps.link(encoder)
            encoder.link(rtppay)
            rtppay.link(udp_sink)

        if out_to_file:
            VideoCenter.link_ouput_file(tee)
            
        if out_to_opencv:
            VideoCenter.link_output_opencv(tee)


        # create an event loop and feed gstreamer bus mesages to it
        loop = GObject.MainLoop()
        bus = VideoCenter.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect ("message", bus_call, loop)

        tiler_src_pad = pgie.get_static_pad("src")
        if not tiler_src_pad:
            sys.stderr.write(" Unable to get src pad \n")
        else:
            tiler_src_pad.add_probe(Gst.PadProbeType.BUFFER, VideoCenter.tiler_src_pad_buffer_probe, 0)

        if out_to_rtsp:
            # Start streaming
            rtsp_port_num = 8554

            server = GstRtspServer.RTSPServer.new()
            server.props.service = "%d" % rtsp_port_num
            server.attach(None)

            factory = GstRtspServer.RTSPMediaFactory.new()
            factory.set_launch(
                '( udpsrc name = pay0 port = %d buffer-size = 524288 caps = "application/x-rtp, media = video, clock-rate = 90000, encoding-name = (string)%s, payload = 96 " )'
                % (updsink_port_num, "H264")
            )
            factory.set_shared(True)
            server.get_mount_points().add_factory("/ds-test", factory)

            print(
                "\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n\n"
                % rtsp_port_num
            )
    @staticmethod
    def Start(filesink_location):
        print("Starting pipeline \n")
        if VideoCenter.filesink:
            VideoCenter.filesink.set_property("location", filesink_location)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   File will be saved as ", filesink_location)
            # time.sleep(3)
        x = VideoCenter.pipeline.set_state(Gst.State.PLAYING)
        print("================================================================",x)
        VideoCenter.recording_start_at = 0

    @staticmethod
    def Stop():
        VideoCenter.pipeline.set_state(Gst.State.NULL)


    def SpinOnce(self):
        now = 100
        start_timestamp = VideoCenter.recording_start_at
        if now - start_timestamp > 120:
            VideoCenter.Stop()

if __name__ == '__main__':
    videoCenter = VideoCenter()
    VideoCenter.CreatePipline(videoCenter.uris, out_to_screen=True, out_to_file=True, out_to_opencv=True, out_to_rtsp=False )
    videoCenter.Start("abc.mkv")
    while True:
        if image_arr is not None:   
            # print("-----",image_arr,"----------------")
            cv2.imshow("appsink image arr", image_arr)
            cv2.waitKey(50)  
      
    time.sleep(50)
    videoCenter.Stop()

