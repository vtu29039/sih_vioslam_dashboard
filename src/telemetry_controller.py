import yaml

class TelemetryController:
    """Computes real-time risk scores, obstacle distances, and steering corrections."""
    
    def __init__(self, config_path="config/camera_params.yaml"):
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)["risk_thresholds"]

    def compute_telemetry(self, dynamic_pixel_count, motion_centroid_x, frame_width=640):
        if dynamic_pixel_count > 12000:
            distance_m = max(0.4, 3.5 - (dynamic_pixel_count / 8000))
        else:
            distance_m = 3.5

        distance_m = round(distance_m, 2)

        if distance_m <= self.cfg["critical_dist_m"]:
            risk_level = "CRITICAL (OBSTACLE)"
            risk_color = "off"
        elif distance_m <= self.cfg["warning_dist_m"]:
            risk_level = "WARNING (SWAY)"
            risk_color = "normal"
        else:
            risk_level = "CLEAR"
            risk_color = "inverse"

        center_x = frame_width / 2.0
        pixel_offset = motion_centroid_x - center_x
        steering_angle = round(-pixel_offset / 12.0, 1)

        return {
            "risk_level": risk_level,
            "risk_color": risk_color,
            "distance_m": distance_m,
            "steering_angle": steering_angle,
        }
