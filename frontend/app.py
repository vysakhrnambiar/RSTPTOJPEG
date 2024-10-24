from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

API_BASE_URL = 'http://localhost:8000'

@app.route('/')
def index():
    # Get list of cameras from the API
    try:
        response = requests.get(f"{API_BASE_URL}/cameras")
        cameras = response.json()
    except requests.RequestException:
        cameras = {}
        flash('Failed to fetch cameras', 'error')
    
    return render_template('index.html', cameras=cameras)

@app.route('/add_camera', methods=['GET', 'POST'])
def add_camera():
    if request.method == 'POST':
        camera_data = {
            'name': request.form['name'],
            'rtsp_url': request.form['rtsp_url'],
            'username': request.form['username'] or None,
            'password': request.form['password'] or None,
            'fps': int(request.form['fps']),
            'resolution': [int(x.strip()) for x in request.form['resolution'].split(',')]
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/cameras",
                params={'camera_id': request.form['camera_id']},
                json=camera_data
            )
            if response.status_code == 200:
                flash('Camera added successfully', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Failed to add camera: {response.json()["detail"]}', 'error')
        except requests.RequestException as e:
            flash(f'Failed to add camera: {str(e)}', 'error')
    
    return render_template('add_camera.html')

@app.route('/delete_camera/<camera_id>', methods=['POST'])
def delete_camera(camera_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/cameras/{camera_id}")
        if response.status_code == 200:
            flash('Camera deleted successfully', 'success')
        else:
            flash(f'Failed to delete camera: {response.json()["detail"]}', 'error')
    except requests.RequestException as e:
        flash(f'Failed to delete camera: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)