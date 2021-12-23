
gst-launch-1.0 uridecodebin uri="rtsp://admin:a@192.168.1.81:554" ! nvoverlaysink overlay-w=640 overlay-h=480

gst-launch-1.0 -e uridecodebin uri=rtsp://admin:a@192.168.1.81:554/h265/ch1/main/av_stream ! nvvideoconvert ! nvv4l2h265enc ! h265parse ! matroskamux ! filesink location=cam1.mkv





gst-launch-1.0 -ev  rtspsrc location=rtsp://192.168.1.81:554/user=admin&password=&channel=1&stream=0 ! application/x-rtp, media=video, encoding-name=H264  ! queue ! rtph264depay ! h264parse ! matroskamux ! filesink location=received_h264.mkv









gst-launch-1.0 -e  rtspsrc location=rtsp://admin:b@192.168.1.81:554 ! application/x-rtp, media=video, encoding-name=H264  ! queue ! rtph264depay ! h264parse ! matroskamux ! filesink location=received_h264.mkv


rtsp://admin:a@192.168.1.81:554

gst-launch-1.0 rtspsrc location=rtsp://admin:a@192.168.1.81:554 ! decodebin ! autovideosink

gst-launch-1.0 rtspsrc location=rtsp://admin:a@192.168.1.81:554 ! queue ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! videoscale ! video/x-raw,width=640,height=480 ! autovideosink


gst-launch-1.0 rtspsrc location='rtsp://admin:a@192.168.1.81:554' ! rtph265depay ! h265parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! fakesink

gst-launch-1.0 rtspsrc location='rtsp://192.168.1.81:554/user=admin_password=a_channel=1_stream=0.sdp' ! rtph265depay ! h265parse ! nvv4l2decoder  block=false ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! fakesink





gst-launch-1.0 uridecodebin uri="rtsp://192.168.1.81:554/user=admin_password=a_channel=1_stream=0.sdp" !  encodebin  ! queue ! mp4mux  ! filesink location="aa.mp4"