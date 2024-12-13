from CameraFactory import CameraFactory

if __name__ == "__main__":
    try:
        camera_factory = CameraFactory(device="/dev/video0", width=640, height=480)
        camera = camera_factory.get_camera()  # Returns an ICameraInterface implementation

        frame = camera.get_frame()
        if frame is not None:
            print(f"Captured a frame of shape: {frame.shape}")
        else:
            print("No frame captured.")

        camera.release()
    except RuntimeError as e:
        print(str(e))
