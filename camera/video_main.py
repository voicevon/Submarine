#!/usr/bin/env python3

from cv2 import convertScaleAbs
from stream_cv import CvStream
from stream_ds import DsStream


if __name__ == "__main__":
    cv = CvStream()
    ds = DsStream()
    DsStream.CreatePipline(ds.uris, out_to_screen=True, out_to_file=True, out_to_opencv=False, out_to_rtsp=False )
    CvStream.CreatePipline(cv.uris, out_to_screen=True, out_to_opencv=True)
    DsStream.Start("abc.mkv")
    cv.Start("Bottom Camera")
    cc = 1
    while True:
        CvStream.SpinOnce()
        cc += 1
        if cc > 25 * 25:
            break
            # pass

    CvStream.Stop()
