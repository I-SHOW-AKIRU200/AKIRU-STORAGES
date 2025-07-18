from flask import Flask, render_template_string, Response, send_from_directory
from pymongo import MongoClient
from gridfs import GridFS
from io import BytesIO
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = "mongodb+srv://AKIRU:1234@cluster0.yrhcncv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "your_database_name"  # Replace with your actual database name
VIDEO_FILE_ID = "6879dcb962a88ddc898f7e7"  # Your video file ID
APP_NAME = "AKIRU VIDEO"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    fs = GridFS(db)
    mongo_connected = True
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    mongo_connected = False
    logger.error(f"MongoDB connection failed: {e}")

# HTML Templates
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #166088;
            --accent-color: #4fc3f7;
            --dark-color: #1a2639;
            --light-color: #f0f4f8;
            --success-color: #4caf50;
            --danger-color: #f44336;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--light-color);
            color: var(--dark-color);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            text-decoration: none;
            color: white;
        }
        
        .video-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 30px 0;
        }
        
        video {
            width: 100%;
            max-height: 70vh;
            display: block;
            outline: none;
        }
        
        .video-info {
            padding: 20px;
        }
        
        .video-title {
            font-size: 24px;
            margin-bottom: 10px;
            color: var(--dark-color);
        }
        
        .video-stats {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            color: #666;
        }
        
        .views-count {
            margin-right: 20px;
            display: flex;
            align-items: center;
        }
        
        .views-count i, .like-button i {
            margin-right: 5px;
            color: var(--primary-color);
        }
        
        .video-actions {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: var(--secondary-color);
        }
        
        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--primary-color);
            color: var(--primary-color);
        }
        
        .btn-outline:hover {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-success {
            background-color: var(--success-color);
            color: white;
        }
        
        .btn-danger {
            background-color: var(--danger-color);
            color: white;
        }
        
        .share-container {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .share-container.active {
            display: block;
        }
        
        .share-options {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .share-input {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .copy-btn {
            padding: 8px 12px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .copy-btn:hover {
            background-color: var(--secondary-color);
        }
        
        .social-share {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .social-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-decoration: none;
            font-size: 18px;
            transition: transform 0.3s ease;
        }
        
        .social-icon:hover {
            transform: translateY(-3px);
        }
        
        .facebook {
            background-color: #3b5998;
        }
        
        .twitter {
            background-color: #1da1f2;
        }
        
        .whatsapp {
            background-color: #25d366;
        }
        
        .telegram {
            background-color: #0088cc;
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--success-color);
            color: white;
            padding: 12px 24px;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            color: #666;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
                gap: 10px;
            }
            
            .video-actions {
                flex-wrap: wrap;
            }
            
            .share-options {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <a href="/" class="logo">{{ app_name }}</a>
            <div class="video-stats">
                <span class="views-count">
                    <i>👁️</i> <span id="viewsCount">{{ view_count }}</span> views
                </span>
            </div>
        </div>
    </header>
    
    <main class="container">
        <div class="video-container">
            <video controls autoplay>
                <source src="/video/{{ video_id }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="video-info">
                <h1 class="video-title">{{ app_name }}</h1>
                <div class="video-actions">
                    <button class="btn btn-primary" id="likeBtn">
                        <i>👍</i> Like
                    </button>
                    <button class="btn btn-outline" id="shareBtn">
                        <i>🔗</i> Share
                    </button>
                </div>
                
                <div class="share-container" id="shareContainer">
                    <h3>Share this video</h3>
                    <div class="share-options">
                        <input type="text" class="share-input" id="shareLink" value="{{ share_url }}" readonly>
                        <button class="copy-btn" id="copyBtn">Copy</button>
                    </div>
                    <div class="social-share">
                        <a href="#" class="social-icon facebook" id="facebookShare">f</a>
                        <a href="#" class="social-icon twitter" id="twitterShare">t</a>
                        <a href="#" class="social-icon whatsapp" id="whatsappShare">w</a>
                        <a href="#" class="social-icon telegram" id="telegramShare">tg</a>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer>
        <p>© {{ current_year }} {{ app_name }}. All rights reserved.</p>
    </footer>
    
    <div class="toast" id="toast">Link copied to clipboard!</div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const shareUrl = window.location.href;
            const shareBtn = document.getElementById('shareBtn');
            const shareContainer = document.getElementById('shareContainer');
            const copyBtn = document.getElementById('copyBtn');
            const shareLink = document.getElementById('shareLink');
            const toast = document.getElementById('toast');
            const likeBtn = document.getElementById('likeBtn');
            
            // Social share buttons
            document.getElementById('facebookShare').href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
            document.getElementById('twitterShare').href = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=Check%20out%20this%20video`;
            document.getElementById('whatsappShare').href = `https://wa.me/?text=${encodeURIComponent(`Check out this video: ${shareUrl}`)}`;
            document.getElementById('telegramShare').href = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=Check%20out%20this%20video`;
            
            // Toggle share container
            shareBtn.addEventListener('click', function() {
                shareContainer.classList.toggle('active');
            });
            
            // Copy link to clipboard
            copyBtn.addEventListener('click', function() {
                shareLink.select();
                document.execCommand('copy');
                
                // Show toast notification
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            });
            
            // Like button functionality
            likeBtn.addEventListener('click', function() {
                this.innerHTML = '<i>👍</i> Liked!';
                this.classList.add('btn-success');
                this.classList.remove('btn-primary');
            });
            
            // Track video views when played
            const video = document.querySelector('video');
            video.addEventListener('play', function() {
                fetch('/track-view', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ video_id: '{{ video_id }}' })
                })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        const viewsCount = document.getElementById('viewsCount');
                        viewsCount.textContent = parseInt(viewsCount.textContent) + 1;
                    }
                });
            });
        });
    </script>
</body>
</html>
'''

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} - Error</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .error-container {
            max-width: 600px;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #dc3545;
            margin-bottom: 1rem;
        }
        p {
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        footer {
            margin-top: 2rem;
            font-size: 0.9rem;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Oops! Something went wrong</h1>
        <p>{{ error_message if error_message else "We're experiencing technical difficulties. Please try again later." }}</p>
        <a href="/">← Return to home page</a>
        <footer>
            <p>© {{ current_year }} {{ app_name }}</p>
        </footer>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    try:
        if not mongo_connected:
            return render_template_string(ERROR_TEMPLATE, 
                                      app_name=APP_NAME,
                                      current_year=datetime.now().year,
                                      error_message="Database connection failed"), 500
        
        # Get view count (simplified example)
        view_count = db.views.count_documents({'video_id': VIDEO_FILE_ID}) if mongo_connected else 0
        
        return render_template_string(MAIN_TEMPLATE, 
                                  app_name=APP_NAME,
                                  view_count=view_count,
                                  video_id=VIDEO_FILE_ID,
                                  share_url=request.url,
                                  current_year=datetime.now().year)
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template_string(ERROR_TEMPLATE, 
                                  app_name=APP_NAME,
                                  current_year=datetime.now().year), 500

@app.route('/video/<video_id>')
def stream_video(video_id):
    try:
        if not mongo_connected:
            return "Database connection failed", 500

        # Get video file from GridFS
        video_file = fs.get(video_id)
        
        # Create a byte stream from the video data
        video_data = BytesIO(video_file.read())
        
        # Determine content type (adjust if using different video formats)
        content_type = 'video/mp4'
        
        # Stream the video with correct headers
        return Response(
            video_data,
            mimetype=content_type,
            direct_passthrough=True
        )
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        return "Video not found", 404

@app.route('/track-view', methods=['POST'])
def track_view():
    try:
        if not mongo_connected:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        # Get video ID from request
        video_id = request.json.get('video_id', VIDEO_FILE_ID)
        
        # Update view count in database
        db.views.update_one(
            {'video_id': video_id},
            {'$inc': {'count': 1}},
            upsert=True
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except:
        return "", 404

@app.errorhandler(404)
def not_found(error):
    return render_template_string(ERROR_TEMPLATE, 
                               app_name=APP_NAME,
                               current_year=datetime.now().year,
                               error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string(ERROR_TEMPLATE, 
                               app_name=APP_NAME,
                               current_year=datetime.now().year,
                               error_message="Internal server error"), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=False)
