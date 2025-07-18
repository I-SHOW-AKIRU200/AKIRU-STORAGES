from flask import Flask, render_template_string, Response, send_from_directory, request, jsonify
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
DB_NAME = "video_db"  # Change to your actual database name
VIDEO_FILE_ID = "6879dcb962a88ddc898f7e7"  # Your video file ID
APP_NAME = "AKIRU VIDEO"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    fs = GridFS(db)
    mongo_connected = True
    logger.info("Successfully connected to MongoDB")
    
    # Create views collection if it doesn't exist
    if 'views' not in db.list_collection_names():
        db.create_collection('views')
except Exception as e:
    mongo_connected = False
    logger.error(f"MongoDB connection failed: {e}")
    local_view_count = 0

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
        /* [Keep all your existing CSS styles] */
    </style>
</head>
<body>
    <!-- [Keep all your existing HTML structure] -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // [Keep all your existing JavaScript]
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
        /* [Keep your existing error page CSS] */
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
        
        # Get view count
        view_count = db.views.count_documents({'video_id': VIDEO_FILE_ID})
        
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
                                  current_year=datetime.now().year,
                                  error_message=str(e)), 500

@app.route('/video/<video_id>')
def stream_video(video_id):
    try:
        if not mongo_connected:
            return "Database connection failed", 500

        # Get video file from GridFS
        video_file = fs.get(video_id)
        
        # Create a byte stream from the video data
        video_data = BytesIO(video_file.read())
        
        # Stream the video with correct headers
        return Response(
            video_data,
            mimetype='video/mp4',
            direct_passthrough=True
        )
    except Exception as e:
        logger.error(f"Error streaming video: {e}")
        return render_template_string(ERROR_TEMPLATE, 
                                   app_name=APP_NAME,
                                   current_year=datetime.now().year,
                                   error_message="Video not found"), 404

@app.route('/track-view', methods=['POST'])
def track_view():
    try:
        if not mongo_connected:
            return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
        
        # Update view count in database
        db.views.update_one(
            {'video_id': VIDEO_FILE_ID},
            {'$inc': {'count': 1}},
            upsert=True
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        logger.error(f"Favicon not found: {e}")
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
