import cv2
import numpy as np
import yaml

class DynaFusionEngine:
    """Simulates dynamic feature segmentation and feature filtering (DynaFusion-VIO)."""
    
    def __init__(self, config_path="config/camera_params.yaml"):
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)["dynafusion"]
            
        self.prev_gray = None

    def process_frame(self, frame, gray):
        mask_display = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        annotated_frame = frame.copy()
        
        static_features = []
        dynamic_pixels = 0
        motion_centroid_x = 320

        if self.prev_gray is not None:
            diff = cv2.absdiff(gray, self.prev_gray)
            _, motion_mask = cv2.threshold(
                diff, self.cfg["optical_flow_diff_thresh"], 255, cv2.THRESH_BINARY
            )

            mask_display[motion_mask == 255] = [0, 0, 255]
            dynamic_pixels = np.sum(motion_mask == 255)

            corners = cv2.goodFeaturesToTrack(
                gray, 
                maxCorners=self.cfg["max_corners"], 
                qualityLevel=self.cfg["quality_level"], 
                minDistance=self.cfg["min_distance"]
            )

            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel()
                    ix, iy = int(x), int(y)
                    
                    if motion_mask[iy, ix] == 0:
                        static_features.append((ix, iy))
                        cv2.circle(annotated_frame, (ix, iy), 3, (0, 255, 0), -1)
                    else:
                        cv2.circle(annotated_frame, (ix, iy), 4, (0, 0, 255), 1)

            M = cv2.moments(motion_mask)
            if M["m00"] > 0:
                motion_centroid_x = int(M["m10"] / M["m00"])

        self.prev_gray = gray.copy()
        return annotated_frame, mask_display, len(static_features), dynamic_pixels, motion_centroid_x
