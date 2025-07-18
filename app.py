from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = "mongodb+srv://akiru:579A3IF7G2D1ELqr@akiru.mneusih.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['video_website']
views_collection = db['views']

# Video configuration
VIDEO_URL = "https://github.com/I-SHOW-AKIRU200/AKIRU-STORAGES/releases/download/video-upload/video.lv_0_20250718084307.mp4"

@app.route('/')
def index():
    # Get view count
    view_data = views_collection.find_one({'video_url': VIDEO_URL})
    view_count = view_data['count'] if view_data else 0
    
    # Increment view count
    if view_data:
        views_collection.update_one(
            {'video_url': VIDEO_URL},
            {'$inc': {'count': 1}}
        )
    else:
        views_collection.insert_one({
            'video_url': VIDEO_URL,
            'count': 1,
            'created_at': datetime.utcnow()
        })
    
    # Render the template with embedded CSS and JS
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AKIRU Video Sharing</title>
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
            <a href="/" class="logo">AKIRU VIDEO</a>
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
                <source src="{{ video_url }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="video-info">
                <h1 class="video-title">AKIRU Video</h1>
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
        <p>© 2023 AKIRU Video Sharing. All rights reserved.</p>
    </footer>
    
    <div class="toast" id="toast">Link copied to clipboard!</div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const videoUrl = '{{ video_url }}';
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
                // In a real app, you would send an AJAX request to the server
                this.innerHTML = '<i>👍</i> Liked!';
                this.classList.add('btn-success');
                this.classList.remove('btn-primary');
            });
            
            // Track video views (additional tracking beyond page load)
            const video = document.querySelector('video');
            video.addEventListener('play', function() {
                // You could send an additional view count when video is played
                // fetch('/track-view', { method: 'POST' });
            });
        });
    </script>
</body>
</html>
    ''', video_url=VIDEO_URL, view_count=view_count, share_url=request.url)

@app.route('/track-view', methods=['POST'])
def track_view():
    # Increment view count via AJAX if needed
    views_collection.update_one(
        {'video_url': VIDEO_URL},
        {'$inc': {'count': 1}},
        upsert=True
    )
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
