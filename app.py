from flask import Flask, request, jsonify
from astrapy import DataAPIClient
from werkzeug.utils import secure_filename

# === Astra Config ===
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:KQtaGbjtjfWyroxBnOwnAJoZ:60c2bc256fb998419971e7260afa9301ad6e04c47493762bb6c61c508c63ec0b"
ASTRA_DB_API_ENDPOINT = "https://dfecb377-3c46-4d76-947b-0d66cff1b2c7-us-east-2.apps.astra.datastax.com"
COLLECTION_NAME = "movie_reviews"

# === Connect to Astra DB ===
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
collection = db.get_collection(COLLECTION_NAME)

# === Flask app ===
app = Flask(__name__)

@app.route('/store', methods=['POST'])
def upload_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    file = request.files.get('file')

    if not folder or not key or not file:
        return jsonify({'error': 'folder, key, and file required'}), 400

    file_content = file.read()
    filename = secure_filename(file.filename)

    try:
        doc = {
            "folder": folder,
            "key": key,
            "filename": filename,
            "file_data": file_content.decode(errors='ignore')  # You can base64 or encode binary
        }
        collection.insert_one(doc)
        return jsonify({'status': 'uploaded', 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list', methods=['GET'])
def list_files():
    folder = request.args.get('folder')
    key = request.args.get('key')

    docs = collection.find({"folder": folder, "key": key})
    filenames = [doc["filename"] for doc in docs]
    return jsonify({"files": filenames})

@app.route('/delete', methods=['GET'])
def delete_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    filename = request.args.get('file')

    doc = collection.find_one({"folder": folder, "key": key, "filename": filename})
    if doc:
        collection.delete_one({"_id": doc["_id"]})
        return jsonify({"status": "deleted"})
    return jsonify({"error": "File not found"}), 404

@app.route('/')
def index():
    return "✅ Astra DB file API is running!"
