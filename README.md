# RTSP Camera Manager

This project provides a complete solution for managing and viewing RTSP camera feeds with a FastAPI backend and Flask frontend.

## Features

- Configure and manage multiple RTSP camera streams
- Beautiful web interface for camera management
- Single image endpoint for each camera
- Persistent camera configuration
- Thread-safe camera handling

## Setup

1. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Install frontend dependencies:
```bash
pip install -r frontend/requirements.txt
```

3. Start the backend server:
```bash
python backend/server.py
```

4. Start the frontend server:
```bash
python frontend/app.py
```

5. Open your browser and navigate to:
   - Frontend UI: `http://localhost:5000`
   - Backend API: `http://localhost:8000`

## API Endpoints

- `POST /cameras` - Add a new camera
- `DELETE /cameras/{camera_id}` - Remove a camera
- `GET /cameras` - List all configured cameras
- `GET /cameras/{camera_id}/image` - Get current camera image

## Usage

1. Open the web interface at `http://localhost:5000`
2. Use the "Add Camera" button to configure new cameras
3. View all configured cameras on the main page
4. Each camera image refreshes automatically every second
5. Use the delete button to remove cameras

## API Image Example

To get a single image from a camera:
```bash
curl http://localhost:8000/cameras/cam1/image > image.jpg
```