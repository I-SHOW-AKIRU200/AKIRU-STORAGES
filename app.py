import os
from flask import Flask, request, jsonify, send_from_directory
from astrapy.db import AstraDB
from werkzeug.utils import secure_filename

# === Config ===
ASTRA_DB_API_ENDPOINT = "https://dfecb377-3c46-4d76-947b-0d66cff1b2c7-us-east-2.apps.astra.datastax.com"
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:uIddIKexjvPfOCnXtBzXXFgH:2cf7545fd693b4ec97dd8b1100fba7f0fbe1ff6db7c47ef0773dc585f6e84cf3"
ASTRA_DB_KEYSPACE = "default_keyspace"
COLLECTION_NAME = "movie_reviews"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Astra Setup ===
db = AstraDB(
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
    namespace=ASTRA_DB_KEYSPACE
)
collection = db.collection(COLLECTION_NAME)

# === Flask App ===
app = Flask(__name__)

# === Upload File ===
@app.route('/store', methods=['POST'])
def store_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    file = request.files.get('file')

    if not folder or not key or not file:
        return jsonify({'error': 'folder, key, and file are required'}), 400

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
        return jsonify({"status": "uploaded", "file": filename})
    except Exception as e:
        return jsonify({"error": "failed to save in db", "detail": str(e)}), 500

# === Download File ===
@app.route('/download', methods=['GET'])
def download_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    filename = request.args.get('file')

    if not folder or not key or not filename:
        return jsonify({"error": "folder, key and file are required"}), 400

    doc = collection.find_one({
        "folder": folder,
        "key": key,
        "filename": filename
    })

    if not doc:
        return jsonify({"error": "file not found or invalid key"}), 404

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
        return jsonify({"error": "folder and key required"}), 400

    files = collection.find({"folder": folder, "key": key})
    return jsonify({"files": [doc['filename'] for doc in files]})

# === Delete File ===
@app.route('/delete', methods=['GET'])
def delete_file():
    folder = request.args.get('folder')
    key = request.args.get('key')
    filename = request.args.get('file')

    if not folder or not key or not filename:
        return jsonify({"error": "folder, key and file required"}), 400

    doc = collection.find_one({
        "folder": folder,
        "key": key,
        "filename": filename
    })

    if not doc:
        return jsonify({"error": "file not found or invalid key"}), 404

    try:
        os.remove(os.path.join(UPLOAD_FOLDER, secure_filename(folder), filename))
    except:
        pass

    collection.delete_one({
        "folder": folder,
        "key": key,
        "filename": filename
    })

    return jsonify({"status": "deleted", "file": filename})


# === Start Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
