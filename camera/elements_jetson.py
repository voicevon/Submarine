#!/usr/bin/env python3

import sys
import math
from gi.repository import  Gst
import time

class ElementJetson:
    ErrorMessage_WattingSeconds = 10
    @staticmethod
    def make_streammux(number_sources):
        print("Creating streamux \n ")
        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

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
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

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
    def make_tiler(number_sources,TILED_OUTPUT_WIDTH=1024,TILED_OUTPUT_HEIGHT=768):
        print("Creating tiler \n ")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            sys.stderr.write(" Unable to create tiler \n")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

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
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return nvvidconv

    @staticmethod
    def make_nvosd(name,OSD_PROCESS_MODE,OSD_DISPLAY_TEXT):
        print("Creating nvosd \n ")
        nvosd = Gst.ElementFactory.make("nvdsosd", name)
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

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
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return rtppay
        
    @staticmethod
    def make_encoder():
        # Make the encoder
        print("Creating H264 Encoder")
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        if not encoder:
            sys.stderr.write(" Unable to create encoder")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

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
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return transform

    @staticmethod
    def make_mp4mux():
        print("Creating mp4mux")
        mux = Gst.ElementFactory.make("mp4mux","mp4mux")
        if not mux:
            sys.stderr.write("  Unable to create mp4mux")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return mux

    @staticmethod
    def make_mkvmux():
        print("Creating mkvmux")
        mux = Gst.ElementFactory.make("matroskamux","matroskamux")
        if not mux:
            sys.stderr.write("  Unable to create matroskamux")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return mux


    @staticmethod
    def make_h264parse():
        print("Creating H264 parse")
        parse = Gst.ElementFactory.make("h264parse","parse")
        if not parse:
            sys.stderr.write("  Unable to create h264parse")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return parse

    @staticmethod
    def make_nveglglessink():
        print("Creating nveglessink")
        sink = Gst.ElementFactory.make("nveglglessink","nveglglesink")
        if not sink:
            sys.stderr.write("  Unable to create nveglglessink")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return sink

    @staticmethod
    def make_udp_sink(updsink_port_num):
        # Make the UDP sink
        print("Creating udp sink")
        sink = Gst.ElementFactory.make("udpsink", "udpsink")
        if not sink:
            sys.stderr.write(" Unable to create udpsink")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)


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
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return sink

    @staticmethod
    def make_app_sink():
        print("Creating appsink")
        sink = Gst.ElementFactory.make("appsink", "appsink")
        if not sink:
            sys.stderr.write("  Unable to create appsink")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return sink        

    @staticmethod
    def make_tee():
        print("Creating tee")
        tee = Gst.ElementFactory.make("tee", "tee")
        if not tee:
            sys.stderr.write("  Unable to create tee")
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return tee

    @staticmethod
    def make_queue(name):
        print("Creating queue")
        q = Gst.ElementFactory.make("tee", name)
        if not q:
            sys.stderr.write("  Unable to create tee, name=", name)
            time.sleep(ElementJetson.ErrorMessage_WattingSeconds)

        return q
