import cv2
from typing import Dict, Optional
from config import CameraConfig
import threading
import time

class CameraManager:
    def __init__(self):
        self.cameras: Dict[str, 'CameraStream'] = {}
        self._lock = threading.Lock()

    def add_camera(self, camera_id: str, config: CameraConfig) -> bool:
        with self._lock:
            if camera_id in self.cameras:
                return False
            
            camera = CameraStream(config)
            if camera.connect():
                self.cameras[camera_id] = camera
                return True
            return False

    def remove_camera(self, camera_id: str) -> bool:
        with self._lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].stop()
                del self.cameras[camera_id]
                return True
            return False

    def get_frame(self, camera_id: str) -> Optional[bytes]:
        with self._lock:
            if camera_id in self.cameras:
                return self.cameras[camera_id].get_jpeg_frame()
            return None

class CameraStream:
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.last_frame = None
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        url = self.config.rtsp_url
        if self.config.username and self.config.password:
            # Insert credentials into URL if needed
            url = url.replace('rtsp://', f'rtsp://{self.config.username}:{self.config.password}@')
        
        self.cap = cv2.VideoCapture(url)
        if not self.cap.isOpened():
            return False
        
        self.running = True
        self._thread = threading.Thread(target=self._update_frame)
        self._thread.daemon = True
        self._thread.start()
        return True

    def _update_frame(self):
        while self.running:
            if self.cap is None:
                break
                
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(1)
                continue

            with self._lock:
                self.last_frame = frame

            time.sleep(1/self.config.fps)

    def get_jpeg_frame(self) -> Optional[bytes]:
        with self._lock:
            if self.last_frame is None:
                return None
            
            ret, jpeg = cv2.imencode('.jpg', self.last_frame)
            if not ret:
                return None
            
            return jpeg.tobytes()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        if self.cap:
            self.cap.release()