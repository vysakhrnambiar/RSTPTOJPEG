from dataclasses import dataclass
from typing import Dict, Optional
import json
import os

@dataclass
class CameraConfig:
    name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    fps: int = 30
    resolution: tuple[int, int] = (1280, 720)

class ConfigManager:
    def __init__(self, config_path: str = "camera_config.json"):
        self.config_path = config_path
        self.cameras: Dict[str, CameraConfig] = {}
        self.load_config()

    def load_config(self) -> None:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.cameras = {
                    cam_id: CameraConfig(**cam_data)
                    for cam_id, cam_data in data.items()
                }

    def save_config(self) -> None:
        with open(self.config_path, 'w') as f:
            json.dump(
                {
                    cam_id: {
                        'name': cam.name,
                        'rtsp_url': cam.rtsp_url,
                        'username': cam.username,
                        'password': cam.password,
                        'fps': cam.fps,
                        'resolution': cam.resolution
                    }
                    for cam_id, cam in self.cameras.items()
                },
                f,
                indent=2
            )

    def add_camera(self, camera_id: str, config: CameraConfig) -> None:
        self.cameras[camera_id] = config
        self.save_config()

    def remove_camera(self, camera_id: str) -> None:
        if camera_id in self.cameras:
            del self.cameras[camera_id]
            self.save_config()

    def get_camera(self, camera_id: str) -> Optional[CameraConfig]:
        return self.cameras.get(camera_id)

    def list_cameras(self) -> Dict[str, CameraConfig]:
        return self.cameras