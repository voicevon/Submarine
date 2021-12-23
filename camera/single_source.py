#!/usr/bin/env python3

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

Gst.init(None)
a = 0

def on_pad_added( src, pad, des):
    vpad = des.get_static_pad("sink")
    pad.link(vpad)

pipe = Gst.Pipeline.new("test")

src = Gst.ElementFactory.make("rtspsrc", "src")
src1 = Gst.ElementFactory.make("rtspsrc", "src1")
depayv = Gst.ElementFactory.make("rtph264depay", "depayv")
depaya = Gst.ElementFactory.make("rtppcmadepay", "depaya")
#tee = Gst.ElementFactory.make("tee", "tee")
queuev = Gst.ElementFactory.make("queue", "queuev")
queuea = Gst.ElementFactory.make("queue", "queuea")
src.connect("pad-added", on_pad_added, queuev)
src1.connect("pad-added", on_pad_added, queuea)

vfilter = Gst.ElementFactory.make("capsfilter", "flt")
caps = Gst.Caps.from_string("video/x-h264, width=(int)1280, height=(int)720")
vfilter.set_property("caps", caps)

afilter = Gst.ElementFactory.make("capsfilter", "aflt")
audio_caps = Gst.Caps.from_string("audio/x-alaw, channels=(int)1, rate=(int)8000")
afilter.set_property("caps", audio_caps)

muxer = Gst.ElementFactory.make("matroskamux", "muxer")
sink = Gst.ElementFactory.make("filesink", "sinka")

rstp = 'rtsp://192.168.1.81:554/user=admin&password=&channel=1&stream=0'
src.set_property("location", rstp)
src1.set_property("location", rstp)
pipe.add(src)
pipe.add(src1)
pipe.add(depayv)
pipe.add(depaya)
pipe.add(queuev)
pipe.add(vfilter)
pipe.add(afilter)
pipe.add(queuea)
pipe.add(sink)
pipe.add(muxer)

queuev.link(depayv)
depayv.link(vfilter)
queuea.link(depaya)
depaya.link(afilter)

vmuxpad = muxer.get_request_pad("video_%u")
vsrcpad = vfilter.get_static_pad("src")
vsrcpad.link(vmuxpad)

amuxpad = muxer.get_request_pad("audio_%u")
asrcpad = afilter.get_static_pad("src")
asrcpad.link(amuxpad)
muxer.link(sink)
print("aaaaaaaaaaa",sink.get_property("location"))
sink.set_property("location",'artspAV2.mkv')

print(sink.get_property("location"))
pipe.set_state(Gst.State.PLAYING)

mainloop = GLib.MainLoop()
mainloop.run()
import time
time.sleep(20)
exit()
