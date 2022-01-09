#!/usr/bin/env python3



from elements_jetson import ElementJetson
from gi.repository import Gst
import gi
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GstRtspServer

class RtspOutput:

    updsink_port_num = 5400
    rtsp_port_num = 8554

    @staticmethod
    def CreatePipelineBranch(pipeline, tee):
        transform = ElementJetson.make_nvtransform("transform_rtsp")

        nvvidconv_postosd = ElementJetson.make_nvvidconv("nvvideoconvert_post_rtsp")
        caps = ElementJetson.make_caps()
        encoder = ElementJetson.make_encoder()        
        parse = ElementJetson.make_h264parse()
        rtppay  = ElementJetson.make_rtppay()
        udp_sink = ElementJetson.make_udp_sink(RtspOutput.updsink_port_num)

        pipeline.add(transform)
        pipeline.add(nvvidconv_postosd)
        pipeline.add(caps)
        pipeline.add(encoder)
        pipeline.add(parse)
        pipeline.add(rtppay)
        pipeline.add(udp_sink)


        source_pad = tee.get_request_pad('src_3')
        if not source_pad:
            print("   Unable to get_request_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        # sink_pad = videorate.get_static_pad("sink")  
        sink_pad = nvvidconv_postosd.get_static_pad("sink")  
        if not sink_pad:
            print("   Unable to get_static_pad() XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        a = source_pad.link(sink_pad)
        if a != Gst.PadLinkReturn.OK:
            print("output to screen link      source_pad.link(sinkpad)= ", a)


        # streammux.link(nvvidconv)
        # nvvidconv.link(tiler)
        tee.link(nvvidconv_postosd)
        nvvidconv_postosd.link(caps)
        caps.link(encoder)
        encoder.link(rtppay)
        rtppay.link(udp_sink)

    @staticmethod
    def StartStreaming():
        # Start streaming
        server = GstRtspServer.RTSPServer.new()
        server.props.service = "%d" % RtspOutput.rtsp_port_num
        server.attach(None)

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(
            '( udpsrc name = pay0 port = %d buffer-size = 524288 caps = "application/x-rtp, media = video, clock-rate = 90000, encoding-name = (string)%s, payload = 96 " )'
            % (RtspOutput.updsink_port_num, "H264")
        )
        factory.set_shared(True)
        server.get_mount_points().add_factory("/ds-test", factory)

        print(
            "\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n\n"
            % RtspOutput.rtsp_port_num
        )    