import gi
import configparser
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
from gi.repository import GLib
import time

Gst.init(None)

pipeline = Gst.Pipeline()


uri_decode_bin=Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
uri_decode_bin.set_property("uri",'rtsp://admin:123456@192.168.123.20:554/h264/ch1/main/av_stream')

nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")

nvenc = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")

parse = Gst.ElementFactory.make("h264parse", "parse")

mkvmux = Gst.ElementFactory.make("matroskamux", "Stream-muxer")

sink = Gst.ElementFactory.make("filesink", "file")
sink.set_property("location", "cam1.mkv")

pipeline.add( uri_decode_bin)
pipeline.add( nvvidconv )
pipeline.add( nvenc )
pipeline.add( parse )
pipeline.add( mkvmux )
pipeline.add( sink )

uri_decode_bin.link( nvvidconv )
nvvidconv.link( nvenc )
nvenc.link( parse )
parse.link( mkvmux )
mkvmux.link( sink )

pipeline.set_state(Gst.State.PLAYING)
time.sleep(50)
pipeline.set_state(Gst.State.NULL)