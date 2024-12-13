import asyncio
import json
import cv2
import numpy as np
from aiohttp import web
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

pcs = set()

class WebcamVideoTrack(VideoStreamTrack):
    def __init__(self, device_index=0):
        super().__init__()
        self.cap = cv2.VideoCapture(device_index)
        # Optionally configure camera settings here, e.g.:
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()

        if not ret:
            # If we fail to read a frame, return a black frame or handle error
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        from av import VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame


async def handle_offer(request):
    params = await request.json()
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    def on_ice_state_change():
        print("ICE state:", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            asyncio.ensure_future(pc.close())
            pcs.discard(pc)

    # Set the remote description
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    await pc.setRemoteDescription(offer)

    # Add a webcam video track instead of a synthetic one
    # Make sure a webcam is connected and accessible on device index 0
    webcam_track = WebcamVideoTrack(device_index=0)
    pc.addTrack(webcam_track)

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),
    )

async def handle_status(request):
    data = {"status": "ok", "message": "Server is running and webcam feed is accessible"}
    return web.json_response(data)

async def on_shutdown(app):
    # Close all peer connections on shutdown
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

app = web.Application()
app.on_shutdown.append(on_shutdown)

# Add routes for WebRTC offer and a status endpoint
app.router.add_post("/offer", handle_offer)
app.router.add_get("/status", handle_status)

# Set up CORS
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*"
    )
})

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == "__main__":
    web.run_app(app, port=8080)
