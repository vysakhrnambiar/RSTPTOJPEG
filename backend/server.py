from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Tuple

from config import ConfigManager, CameraConfig
from camera_manager import CameraManager

app = FastAPI()
config_manager = ConfigManager()
camera_manager = CameraManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CameraConfigRequest(BaseModel):
    name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    fps: int = 30
    resolution: Tuple[int, int] = (1280, 720)

@app.post("/cameras")
async def add_camera(camera_id: str, config: CameraConfigRequest):
    camera_config = CameraConfig(**config.dict())
    config_manager.add_camera(camera_id, camera_config)
    
    if not camera_manager.add_camera(camera_id, camera_config):
        raise HTTPException(status_code=400, detail="Failed to connect to camera")
    
    return JSONResponse({"status": "success", "message": f"Camera {camera_id} added successfully"})

@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    if not config_manager.get_camera(camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera_manager.remove_camera(camera_id)
    config_manager.remove_camera(camera_id)
    return JSONResponse({"status": "success", "message": f"Camera {camera_id} removed successfully"})

@app.get("/cameras")
async def list_cameras():
    cameras = config_manager.list_cameras()
    return JSONResponse({
        camera_id: {
            "name": config.name,
            "rtsp_url": config.rtsp_url,
            "fps": config.fps,
            "resolution": config.resolution
        }
        for camera_id, config in cameras.items()
    })

@app.get("/cameras/{camera_id}/image")
async def get_camera_image(camera_id: str):
    if not config_manager.get_camera(camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")
    
    frame = camera_manager.get_frame(camera_id)
    if frame is None:
        raise HTTPException(status_code=503, detail="Failed to get camera frame")
    
    return Response(content=frame, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)