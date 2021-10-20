import gi

from camera.cam_gs_nolink import message

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject


class SingleCamera:
    def __init__(self, id:int, command:str ) -> None:
        self.id = id
        GObject.threads_init()
        Gst.init(None)   #?? Feng
        self.command = command
        self.pipiline = []
        self.bus = [] 
        self.__CreatePipeline()


    def __CreatePipeline(self) -> None:
        # print("Creating pipline camera", self.id)
        self.pipeline = [] 
        self.pipeline.append(Gst.parse_launch(self.command))
        self.loop = GObject.MainLoop()   #?? Feng
        self.bus.append(self.pipeline[0].get_bus())
        self.bus[0].connect("message", message, self.loop)

    def StartPipelineRecording(self):
        print("________________________________Starting pipline____________________________")
        self.pipeline[0].set_state(Gst.State.PLAYING)
        self.loop.run()


    def StopPipelineRecording(self):
        self.pipeline[0].set_state(Gst.State.NULL)   

    def BridgeMessage(bus: Gst.Bus, message: Gst.Message, loop: GObject.MainLoop):
        message_type = message.type
        if message_type == Gst.MessageType.EOS:
            loop.quit()
        elif message_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            loop.quit()
        elif message_type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()   
        return True
        


class CameraFactory:
    def __init__(self) -> None:
        pass

    def CreateSingleCamera(self, id:int) -> SingleCamera:
        if id == 1:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.10:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera1.mkv")
            newCamera = SingleCamera(1,command)

        if id == 2:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.20:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera2.mkv")
            newCamera = SingleCamera(2,command)

        if id == 3:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.30:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera3.mkv")
            newCamera = SingleCamera(3,command)

        if id == 4:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.40:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera4.mkv")
            newCamera = SingleCamera(4,command)

        if id == 5:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.50:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera5.mkv")
            newCamera = SingleCamera(5,command)

        if id == 6:
            command =("uridecodebin uri=rtsp://admin:123456@192.168.129.60:554/h265/ch1/main/av_stream ! "
                "nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=camera6.mkv")
            newCamera = SingleCamera(6,command)





