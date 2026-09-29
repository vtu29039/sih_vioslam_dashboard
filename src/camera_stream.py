import cv2
import yaml

class CameraStream:
    """Manages real-time webcam frame acquisition and intrinsics loading."""
    
    def __init__(self, config_path="config/camera_params.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["camera"]
            
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["width"])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["height"])
        self.cap.set(cv2.CAP_PROP_FPS, self.config["fps"])
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame, gray

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
