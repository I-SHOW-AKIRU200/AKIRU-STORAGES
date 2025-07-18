from flask import Flask, render_template_string, request, send_from_directory, Response
from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime
import os
import logging
from bson.objectid import ObjectId
from io import BytesIO
import requests

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = "mongodb+srv://AKIRU:1234@cluster0.yrhcncv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "video_db"
APP_NAME = "AKIRU VIDEO"
VIDEO_SOURCE = "https://github.com/I-SHOW-AKIRU200/AKIRU-STORAGES/releases/download/video-upload/video.lv_0_20250718084307.mp4"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    fs = GridFS(db)
    mongo_connected = True
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Could not connect to MongoDB: {e}")
    mongo_connected = False

def initialize_video():
    """Store the video in MongoDB if it doesn't exist"""
    if not mongo_connected:
        return None
        
    # Check if video already exists
    existing_file = db.fs.files.find_one({"filename": "main_video"})
    if existing_file:
        return existing_file["_id"]
    
    # Download and store the video
    try:
        logger.info("Downloading video from source...")
        response = requests.get(VIDEO_SOURCE, stream=True)
        
        if response.status_code == 200:
            file_id = fs.put(BytesIO(response.content), 
                           filename="main_video",
                           content_type="video/mp4")
            logger.info(f"Video stored in MongoDB with ID: {file_id}")
            return file_id
        else:
            logger.error(f"Failed to download video. Status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error initializing video: {e}")
        return None

# Initialize video on startup
video_id = initialize_video()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico', 
                            mimetype='image/vnd.microsoft.icon')

@app.route('/video')
def stream_video():
    """Stream video directly from MongoDB"""
    if not mongo_connected or not video_id:
        return "Video service unavailable", 503
        
    grid_out = fs.get(video_id)
    
    def generate():
        chunk_size = 8192  # 8KB chunks
        while True:
            chunk = grid_out.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    return Response(generate(), 
                  mimetype=grid_out.content_type,
                  headers={
                      "Content-Length": str(grid_out.length),
                      "Accept-Ranges": "bytes"
                  })

@app.route('/track-view', methods=['POST'])
def track_view():
    """Increment view count via AJAX"""
    if not mongo_connected or not video_id:
        return jsonify({"status": "error", "message": "Database unavailable"}), 500
    
    try:
        result = db.views.update_one(
            {"video_id": str(video_id)},
            {"$inc": {"count": 1}},
            upsert=True
        )
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/')
def index():
    """Main page with video player"""
    try:
        # Get view count
        view_count = 0
        if mongo_connected and video_id:
            view_data = db.views.find_one({"video_id": str(video_id)})
            view_count = view_data["count"] if view_data else 0
        
        return render_template_string(TEMPLATE, 
                                  app_name=APP_NAME,
                                  view_count=view_count,
                                  current_year=datetime.now().year)
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template_string(ERROR_TEMPLATE,
                                  app_name=APP_NAME,
                                  error_message="Service unavailable",
                                  current_year=datetime.now().year), 500

# HTML Templates
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --accent: #4895ef;
            --dark: #1a1a2e;
            --light: #f8f9fa;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background: var(--light);
            color: var(--dark);
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: var(--primary);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .video-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
            margin: 30px 0;
        }
        video {
            width: 100%;
            display: block;
            background: black;
        }
        .video-info {
            padding: 20px;
        }
        .video-stats {
            display: flex;
            align-items: center;
            gap: 20px;
            margin: 15px 0;
            color: #555;
        }
        .video-actions {
            display: flex;
            gap: 15px;
            margin: 20px 0;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.3s;
        }
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        .btn-primary:hover {
            background: var(--secondary);
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <h1>{{ app_name }}</h1>
            <div class="video-stats">
                <span id="viewsCount">{{ view_count }}</span> views
            </div>
        </div>
    </header>

    <main class="container">
        <div class="video-container">
            <video controls autoplay id="mainVideo">
                <source src="/video" type="video/mp4">
                Your browser does not support HTML5 video.
            </video>
            <div class="video-info">
                <div class="video-actions">
                    <button class="btn btn-primary" id="likeBtn">
                        <span>👍</span> Like
                    </button>
                    <button class="btn btn-primary" id="shareBtn">
                        <span>🔗</span> Share
                    </button>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <p>© {{ current_year }} {{ app_name }}. All rights reserved.</p>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const video = document.getElementById('mainVideo');
            const viewsCount = document.getElementById('viewsCount');
            const likeBtn = document.getElementById('likeBtn');
            
            // Track when video is played
            video.addEventListener('play', function() {
                fetch('/track-view', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if(data.status === 'success') {
                            viewsCount.textContent = parseInt(viewsCount.textContent) + 1;
                        }
                    });
            });

            // Like button functionality
            likeBtn.addEventListener('click', function() {
                this.innerHTML = '<span>👍</span> Liked!';
                this.style.backgroundColor = '#4CAF50';
            });

            // Share button functionality
            document.getElementById('shareBtn').addEventListener('click', function() {
                navigator.clipboard.writeText(window.location.href)
                    .then(() => alert('Link copied to clipboard!'))
                    .catch(() => prompt('Copy this link:', window.location.href));
            });
        });
    </script>
</body>
</html>
'''

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ app_name }} - Error</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f8f9fa;
            color: #333;
        }
        .error-container {
            text-align: center;
            padding: 2rem;
            max-width: 500px;
        }
        h1 {
            color: #d9534f;
            margin-bottom: 1rem;
        }
        a {
            color: #4361ee;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Error</h1>
        <p>{{ error_message }}</p>
        <a href="/">Return to home page</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    # Create static directory if needed
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Run the app
    app.run(host='0.0.0.0', port=5000)
