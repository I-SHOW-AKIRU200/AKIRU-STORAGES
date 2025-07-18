import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from astrapy import DataAPIClient

# === Config ===
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:KQtaGbjtjfWyroxBnOwnAJoZ:60c2bc256fb998419971e7260afa9301ad6e04c47493762bb6c61c508c63ec0b"
ASTRA_DB_API_ENDPOINT = "https://dfecb377-3c46-4d76-947b-0d66cff1b2c7-us-east-2.apps.astra.datastax.com"
COLLECTION_NAME = "movie_reviews"
UPLOAD_FOLDER = "uploads"

# === Astra DB Setup ===
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
collection = db.get_collection(COLLECTION_NAME)

# === Flask App Setup ===
app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Upload File ===
@app.route('/store', methods=['POST'])
def upload_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    file = request.files.get('file')

    if not folder or not key or not file:
        return jsonify({'error': 'folder, key, and file required'}), 400

    user_folder = os.path.join(UPLOAD_FOLDER, secure_filename(folder))
    os.makedirs(user_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    doc = {
        "folder": folder,
        "key": key,
        "filename": filename,
        "path": filepath
    }

    try:
        collection.insert_one(doc)
        return jsonify({'status': 'uploaded', 'file': filename})
    except Exception as e:
        return jsonify({'error': 'DB insert failed', 'detail': str(e)}), 500

# === Download File ===
@app.route('/download', methods=['GET'])
def download_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    filename = request.args.get('file')

    if not folder or not key or not filename:
        return jsonify({'error': 'folder, key, file required'}), 400

    doc = collection.find_one({
        "folder": folder,
        "key": key,
        "filename": filename
    })

    if not doc:
        return jsonify({'error': 'file not found or invalid key'}), 404

    return send_from_directory(
        os.path.join(UPLOAD_FOLDER, secure_filename(folder)),
        filename,
        as_attachment=True
    )

# === List Files ===
@app.route('/list', methods=['GET'])
def list_files():
    folder = request.args.get('folder')
    key = request.args.get('key')

    if not folder or not key:
        return jsonify({'error': 'folder and key required'}), 400

    docs = collection.find({"folder": folder, "key": key})
    return jsonify({'files': [doc['filename'] for doc in docs]})

# === Delete File ===
@app.route('/delete', methods=['GET'])
def delete_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    filename = request.args.get('file')

    if not folder or not key or not filename:
        return jsonify({'error': 'folder, key, file required'}), 400

    doc = collection.find_one({
        "folder": folder,
        "key": key,
        "filename": filename
    })

    if not doc:
        return jsonify({'error': 'file not found or invalid key'}), 404

    try:
        os.remove(os.path.join(UPLOAD_FOLDER, secure_filename(folder), filename))
    except:
        pass

    collection.delete_one({"_id": doc["_id"]})
    return jsonify({'status': 'deleted', 'file': filename})

# === Run App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
