#!/usr/bin/env python3

# cd ~/Sumbrine/camera/
# python3 ds_main.py rtsp://admin:a@192.168.1.82:554 rtsp://admin:a@192.168.1.81 rtsp://admin:a@192.168.1.82   rtsp://admin:a@192.168.1.83 rtsp://admin:a@192.168.1.84 rtsp://admin:a@192.168.1.86

import sys
sys.path.append("../")
import pyds
from common.bus_call import bus_call
import math
from ctypes import *
import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GObject, Gst, GstRtspServer, GLib
import configparser

import argparse

from common.FPS import GETFPS

fps_streams={}

MAX_DISPLAY_LEN=64
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH=1920
MUXER_OUTPUT_HEIGHT=1080
MUXER_BATCH_TIMEOUT_USEC=4000000
TILED_OUTPUT_WIDTH=1280
TILED_OUTPUT_HEIGHT=720
GST_CAPS_FEATURES_NVMM="memory:NVMM"
OSD_PROCESS_MODE= 0
OSD_DISPLAY_TEXT= 1
pgie_classes_str= ["Vehicle", "TwoWheeler", "Person", "RoadSign"]

# tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
# and update params for drawing rectangle, object information etc.


def tiler_src_pad_buffer_probe(pad,info,u_data):
    frame_number=0
    num_rects=0
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

        frame_number=frame_meta.frame_num
        l_obj=frame_meta.obj_meta_list
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
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            try:
                l_obj=l_obj.next
            except StopIteration:
                break
        print("Frame Number=", frame_number, "Number of Objects=",num_rects,"Vehicle_count=",obj_counter[PGIE_CLASS_ID_VEHICLE],"Person_count=",obj_counter[PGIE_CLASS_ID_PERSON])

        # Get frame rate through this probe
        fps_streams["stream{0}".format(frame_meta.pad_index)].get_fps()
        try:
            l_frame=l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK



def cb_newpad(decodebin, decoder_src_pad,data):
    print("In cb_newpad\n")
    caps=decoder_src_pad.get_current_caps()
    gststruct=caps.get_structure(0)
    gstname=gststruct.get_name()
    source_bin=data
    features=caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    print("gstname=",gstname)
    if(gstname.find("video")!=-1):
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        print("features=",features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad=source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")

def decodebin_child_added(child_proxy,Object,name,user_data):
    print("Decodebin child added:", name, "\n")
    if(name.find("decodebin") != -1):
        Object.connect("child-added",decodebin_child_added,user_data)

def create_source_bin(index,uri):
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name="source-bin-%02d" %index
    print(bin_name)
    nbin=Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin=Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri",uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added",cb_newpad,nbin)
    uri_decode_bin.connect("child-added",decodebin_child_added,nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin,uri_decode_bin)
    bin_pad=nbin.add_pad(Gst.GhostPad.new_no_target("src",Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin


def make_streammux(number_sources):
    print("Creating streamux \n ")
    # Create nvstreammux instance to form batches from one or more sources.
    streammux=Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")
    streammux.set_property('live-source', 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", 4000000)        
    return streammux
    
def make_pgie(number_sources):
    print("Creating Pgie \n ")
    pgie=Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")
    pgie.set_property("config-file-path", "dstest1_pgie_config.txt")

    pgie_batch_size=pgie.get_property("batch-size")
    if pgie_batch_size != number_sources:
        print(
            "WARNING: Overriding infer-config batch-size",
            pgie_batch_size,
            " with number of sources ",
            number_sources,
            " \n",
        )
        pgie.set_property("batch-size", number_sources)        
    return pgie

def make_tiler(number_sources):
    print("Creating tiler \n ")
    tiler=Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    tiler_rows=int(math.sqrt(number_sources))
    tiler_columns=int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)        
    return tiler    

def make_nvvidconv():
    print("Creating nvvidconv \n ")
    nvvidconv=Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")
    return nvvidconv

def make_nvosd():
    print("Creating nvosd \n ")
    nvosd=Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
    nvosd.set_property('process-mode',OSD_PROCESS_MODE)
    nvosd.set_property('display-text',OSD_DISPLAY_TEXT)        
    return nvosd

def make_nvvidconv_post():
    nvvidconv_postosd=Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")
    return nvvidconv_postosd    

def make_caps():
    # Create a caps filter
    caps=Gst.ElementFactory.make("capsfilter", "filter")
    caps.set_property(
        "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
    )
    return caps

def make_rtppay():
    # Make the payload-encode video into RTP packets
    rtppay=Gst.ElementFactory.make("rtph264pay", "rtppay")
    print("Creating H264 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")
    return rtppay
    


def make_nvtransform():
    print("Creating nvtransform")
    transform=Gst.ElementFactory.make("nvegltransform","nvegltransform")
    if not transform:
        sys.stderr.write("  Unable to create nvegltransform")
    return transform

def make_mp4mux():
    print("Creating mp4mux")
    mux=Gst.ElementFactory.make("mp4mux","mp4mux")
    if not mux:
        sys.stderr.write("  Unable to create mp4mux")
    return mux

def make_encoder():
    # Make the encoder
    print("Creating H265 Encoder")
    encoder=Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")
    # encoder.set_property("bitrate", bitrate)
    # encoder.set_property("preset-level", 1)
    # encoder.set_property("insert-sps-pps", 1)
    # encoder.set_property("bufapi-version", 1)
    return encoder

def make_h264parse():
    print("Creating H265 parse")
    parse=Gst.ElementFactory.make("h265parse","parse")
    if not parse:
        sys.stderr.write("  Unable to create parse")
    return parse

def make_mkvmux():
    print("Creating mkvmux")    
    mux=Gst.ElementFactory.make("matroskamux","matroskamux")
    if not mux:
        sys.stderr.write("  Unable to create matroskamux")
    return mux

def make_file_sink(filename):
    print("Creating filesink")
    sink=Gst.ElementFactory.make("filesink", "filesink")
    if not sink:
        sys.stderr.write("  Unable to create filesink")
    sink.set_property("location",filename)
    return sink

def make_nveglglessink():
    print("Creating nveglessink")
    sink=Gst.ElementFactory.make("nveglglessink","nveglglesink")
    if not sink:
        sys.stderr.write("  Unable to create nveglglessink")
    return sink

def make_udp_sink(updsink_port_num):
    # Make the UDP sink
    print("Creating udp sink")
    sink=Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")

    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", updsink_port_num)
    sink.set_property("async", False)
    sink.set_property("sync", 1)
    sink.set_property("qos", 0)
    return sink
    


def main(uris, finnal_sink):
    # Check input arguments
    for i in range(0, len(uris)):
        fps_streams["stream{0}".format(i)]=GETFPS(i)
    number_sources=len(uris)

    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    print("Adding elements to Pipeline \n")
    # pipeline.add(pgie)

    if finnal_sink == 'SCREEN':
        nvosd = make_nvosd()
        transform = make_nvtransform()
        nvsink = make_nveglglessink()

        pipeline.add(nvvidconv)
        # pipeline.add(uri_decode_bin)
        pipeline.add(nvosd)
        pipeline.add(transform)
        pipeline.add(nvsink)

        # uri_decode_bin.link(nvvidconv)
        nvvidconv.link(nvosd)
        nvosd.link(transform)
        transform.link(nvsink)

    if finnal_sink == "FILE":
        # command = ("uridecodebin uri=rtsp://admin:a@192.168.1.81 ! "
#     "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam1.mkv")
        uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
        if not uri_decode_bin:
            sys.stderr.write("   Unable to create uridecodebin")
        uri_decode_bin.set_property("uri","rtsp://admin:a@192.168.1.82")
        nvvidconv=make_nvvidconv()
        encoder=make_encoder()        
        parse=make_h264parse()
        mkvmux = make_mkvmux()
        filesink=make_file_sink("cam81.mkv")

        pipeline.add(uri_decode_bin)
        pipeline.add(nvvidconv)
        pipeline.add(encoder)
        pipeline.add(parse)
        pipeline.add(mkvmux)
        pipeline.add(filesink)

        # a = uri_decode_bin.link(nvvidconv)
        # if not a:
        #     print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        b= nvvidconv.link(encoder)
        c=encoder.link(parse)
        d=parse.link(mkvmux)
        e=mkvmux.link(filesink)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   ",b,c,d,e)



    # create an event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)





    # start play back and listen to events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except BaseException:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)



def set_global_var():
    global codec
    global bitrate
    global stream_path
    global gie
    gie="nvinfer"
    codec="H264"
    bitrate=4000000
    stream_path=""
    return stream_path    

class VideoCenter:
    def __init__(self) -> None:
        self.uris=list()
        for i in range(1):
            self.uris.append('')
        # self.uris[0]="rtsp://admin:a@192.168.1.81:554/h265/ch1/main/av_stream"
        self.uris[0]="rtsp://admin:a@192.168.1.81"
        # self.uris[1]="rtsp://admin:a@192.168.1.82"
        # self.uris[2]="rtsp://admin:a@192.168.1.83"
        # self.uris[3]="rtsp://admin:a@192.168.1.84"
        # self.uris[4]="rtsp://admin:a@192.168.1.86"
        # self.uris[5]="rtsp://admin:a@192.168.1.86"

    def StartStop(self, cameras):
        for i in range(6):
            if cameras[i]:
                pass
            else:
                pass

if __name__ == '__main__':
    set_global_var()
    videoCenter=VideoCenter()
    # sys.exit(main(videoCenter.uris, "SCREEN"))
    sys.exit(main(videoCenter.uris, "FILE"))
    # sys.exit(main(videoCenter.uris, "RTSP"))