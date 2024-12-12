from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time
import threading

# 1. start server: python3 -m http.server 8000
# 2. open stream: ffplay http://192.168.0.58:8000/stream.m3u8
# drawback: creates a lot of files

def start_stream():
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (1280, 720)})
    picam2.configure(video_config)

    # ffmpeg HLS Output
    output = FfmpegOutput(
        "-f hls "
        "-hls_time 4 "
        "-hls_list_size 5 "
        "-hls_flags delete_segments "
        "-hls_allow_cache 0 "
        "stream.m3u8"
    )

    encoder = H264Encoder()

    picam2.start_recording(encoder, output)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        picam2.stop_recording()

if __name__ == "__main__":
    # Starten des Streams in einem separaten Thread
    stream_thread = threading.Thread(target=start_stream)
    stream_thread.start()
