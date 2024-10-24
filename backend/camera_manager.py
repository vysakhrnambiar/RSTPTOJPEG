import cv2
from typing import Dict, Optional
from config import CameraConfig, ConfigManager
import threading
import time

class CameraManager:
    def __init__(self):
        self.cameras: Dict[str, 'CameraStream'] = {}
        self._lock = threading.Lock()
        # Initialize existing cameras from config
        self._init_from_config()
    
    def _init_from_config(self):
        """Initialize cameras from saved configuration on startup"""
        config_manager = ConfigManager()
        for camera_id, config in config_manager.list_cameras().items():
            self.add_camera(camera_id, config)
            print(f"Initialized camera: {camera_id} ({config.name})")

    def add_camera(self, camera_id: str, config: CameraConfig) -> bool:
        with self._lock:
            if camera_id in self.cameras:
                # If camera exists, stop it first
                self.cameras[camera_id].stop()
            
            camera = CameraStream(config)
            if camera.connect():
                self.cameras[camera_id] = camera
                print(f"Successfully connected to camera: {camera_id}")
                return True
            print(f"Failed to connect to camera: {camera_id}")
            return False

    def remove_camera(self, camera_id: str) -> bool:
        with self._lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].stop()
                del self.cameras[camera_id]
                print(f"Removed camera: {camera_id}")
                return True
            return False

    def get_frame(self, camera_id: str) -> Optional[bytes]:
        with self._lock:
            if camera_id in self.cameras:
                return self.cameras[camera_id].get_jpeg_frame()
            return None

    def __del__(self):
        """Cleanup all cameras on shutdown"""
        for camera_id in list(self.cameras.keys()):
            self.remove_camera(camera_id)

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
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
        
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
                time.sleep(1)  # Wait before retry
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
        """Stop the camera stream and release resources"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)  # Wait up to 1 second for thread to finish
        if self.cap:
            self.cap.release()
        print(f"Stopped camera stream: {self.config.name}")