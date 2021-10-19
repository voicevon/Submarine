import gi
from time import time, sleep
import threading
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

def message(bus: Gst.Bus, message: Gst.Message, loop: GObject.MainLoop):

    message_type = message.type

    if message_type == Gst.MessageType.EOS:

        loop.quit()

    elif message_type == Gst.MessageType.ERROR:

        err, debug = message.parse_error()

        loop.quit()

    elif message_type == Gst.MessageType.WARNING:

        err, debug = message.parse_warning()
        
    return True
       
def gst_cam1(self):
    
    GObject.threads_init()

    Gst.init(None)

   
    bus_1 = [] * 10

    pipeline_1 = [] 

    print("Creating piplinecam1")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.10:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam1.mkv")


    pipeline_1.append(Gst.parse_launch(command))


    loop1 = GObject.MainLoop()

    bus_1.append(pipeline_1[0].get_bus())

    bus_1[0].connect("message", message, loop1)

    print("________________________________Starting pipline1____________________________")
    
    pipeline_1[0].set_state(Gst.State.PLAYING)

    loop1.run()
    
    pipeline_1[0].set_state(Gst.State.NULL)
    

def gst_cam2(self):
    GObject.threads_init()

    Gst.init(None)

    bus_2 = [] * 10

    pipeline_2 = [] * 10

    print("Creating piplinecam2")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.20:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam2.mkv")

    pipeline_2.append(Gst.parse_launch(command))
    

    loop2 = GObject.MainLoop()

    bus_2.append(pipeline_2[0].get_bus())

    bus_2[0].connect("message", message, loop2)

    print("________________________________Starting pipline2____________________________")
    
    pipeline_2[0].set_state(Gst.State.PLAYING)
    
    loop2.run()
    
    pipeline_2[0].set_state(Gst.State.NULL)
    
def gst_cam3(self):
    GObject.threads_init()

    Gst.init(None)

    bus_3 = [] * 10

    pipeline_3 = [] * 10

    print("Creating piplinecam3")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.30:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam3.mkv")

    pipeline_3.append(Gst.parse_launch(command))


    loop3 = GObject.MainLoop()

    bus_3.append(pipeline_3[0].get_bus())

    bus_3[0].connect("message", message, loop3)

    print("________________________________Starting pipline3____________________________")
    
    pipeline_3[0].set_state(Gst.State.PLAYING)
    
    loop3.run()
    
    pipeline_3[0].set_state(Gst.State.NULL)

def gst_cam4(self):
    GObject.threads_init()

    Gst.init(None)

    bus_4 = [] * 10

    pipeline_4 = [] * 10

    print("Creating piplinecam4")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.40:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam4.mkv")

    pipeline_4.append(Gst.parse_launch(command))


    loop4 = GObject.MainLoop()

    bus_4.append(pipeline_4[0].get_bus())

    bus_4[0].connect("message", message, loop4)

    print("________________________________Starting pipline4____________________________")
    
    pipeline_4[0].set_state(Gst.State.PLAYING)
    
    loop4.run()
    
    pipeline_4[0].set_state(Gst.State.NULL)

def gst_cam5(self):
    GObject.threads_init()

    Gst.init(None)

    bus_5 = [] * 10

    pipeline_5 = [] * 10

    print("Creating piplinecam5")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.50:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam5.mkv")

    pipeline_5.append(Gst.parse_launch(command))

    loop5 = GObject.MainLoop()

    bus_5.append(pipeline_5[0].get_bus())

    bus_5[0].connect("message", message, loop5)

    print("________________________________Starting pipline5____________________________")
    
    pipeline_5[0].set_state(Gst.State.PLAYING)
    
    loop5.run()
    
    pipeline_5[0].set_state(Gst.State.NULL)

def gst_cam6(self):
    GObject.threads_init()

    Gst.init(None)

    bus_6 = [] * 10

    pipeline_6 = [] * 10

    print("Creating piplinecam6")

    command = ("uridecodebin uri=rtsp://admin:123456@192.168.129.60:554/h265/ch1/main/av_stream ! "
            "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam6.mkv")

    pipeline_6.append(Gst.parse_launch(command))

    loop6 = GObject.MainLoop()

    bus_6.append(pipeline_6[0].get_bus())

    bus_6[0].connect("message", message, loop6)

    print("________________________________Starting pipline6____________________________")
    
    pipeline_6[0].set_state(Gst.State.PLAYING)
    
    loop6.run()
    
    pipeline_6[0].set_state(Gst.State.NULL)

if __name__ == '__main__':
    cam_1 = threading.Thread(target = gst_cam1,args = ("cam1_record",))

    cam_2 = threading.Thread(target = gst_cam2,args = ("cam2_record",))

    cam_3 = threading.Thread(target = gst_cam3,args = ("cam3_record",))

    cam_4 = threading.Thread(target = gst_cam4,args = ("cam4_record",))

    cam_5 = threading.Thread(target = gst_cam5,args = ("cam5_record",))

    cam_6 = threading.Thread(target = gst_cam6,args = ("cam6_record",))

    cam_1.start()

    cam_2.start()

    cam_3.start()

    cam_4.start()

    cam_5.start()

    cam_6.start()