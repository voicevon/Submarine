#!/usr/bin/env python3


import sys

sys.path.append("../")
import pyds
from common.bus_call import bus_call
import time
from ctypes import *
import gi
gi.require_version("Gst", "1.0")

from gi.repository import GObject, Gst, GLib

from common.FPS import GETFPS
# import cv2
# import numpy

from elements_jetson import ElementJetson
from br_file_saver import FileSaver
from br_output_on_screen import ScreenPlayer
from br_opencv import AppOpenCV
from br_rtsp_out import RtspOutput

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

# image_arr = None


# tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
# and update params for drawing rectangle, object information etc.
class VideoCenter:
    pipeline = None  # Gst.Pipeline()
    recording_start_at = 0
    # filesink = None
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

        streammux = ElementJetson.make_streammux(number_sources)
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

        pgie = ElementJetson.make_pgie(number_sources)
        tiler = ElementJetson.make_tiler(number_sources)
        tee = ElementJetson.make_tee()


        print("Adding elements to Pipeline \n")
        # pipeline.add(pgie)
        VideoCenter.pipeline.add(tiler)
        VideoCenter.pipeline.add(tee)

        streammux.link(tiler)
        tiler.link(tee)

        if out_to_screen:
            # videoCenter.link_output_screen(tee)
            ScreenPlayer.CreatePipelineBranch(VideoCenter.pipeline, tee, OSD_PROCESS_MODE, OSD_DISPLAY_TEXT)


        if out_to_rtsp:
            RtspOutput.CreatePipelineBranch(VideoCenter.pipeline,tee)
        if out_to_file:
            FileSaver.CreatePipilineBranch(VideoCenter.pipeline, tee)
            
        if out_to_opencv:
            AppOpenCV.CreatePiplineBranch(VideoCenter.pipeline, tee)


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
            RtspOutput.StartStreaming()
    @staticmethod
    def Start(file_path_name_to_be_saved):
        print("Starting pipeline \n")
        FileSaver.UpdateFileLocation(file_path_name_to_be_saved)
        x = VideoCenter.pipeline.set_state(Gst.State.PLAYING)
        print("================================================================",x)
        VideoCenter.recording_start_at = 0

    @staticmethod
    def Stop():
        VideoCenter.pipeline.set_state(Gst.State.NULL)

    @staticmethod
    def SpinOnce():
        AppOpenCV.SpinOnce()
        # cv2.waitKey(50)  
    
if __name__ == '__main__':
    videoCenter = VideoCenter()
    VideoCenter.CreatePipline(videoCenter.uris, out_to_screen=True, out_to_file=True, out_to_opencv=True, out_to_rtsp=False )
    videoCenter.Start("abc.mkv")
    cc = 1
    while True:
        VideoCenter.SpinOnce()
        cc += 1
        if cc > 25 * 100:
            break
            # pass
    # start_timestamp = VideoCenter.recording_start_at
    # if now - start_timestamp > 120:
    #     VideoCenter.Stop()
    videoCenter.Stop()

