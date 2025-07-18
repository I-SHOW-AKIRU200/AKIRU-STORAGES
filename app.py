from flask import Flask, request, jsonify
from astrapy import DataAPIClient
import base64

app = Flask(__name__)

# Astra DB config
ASTRA_DB_ID = "dfecb377-3c46-4d76-947b-0d66cff1b2c7"
ASTRA_DB_REGION = "us-east-2"
ASTRA_API_ENDPOINT = f"https://{ASTRA_DB_ID}-{ASTRA_DB_REGION}.apps.astra.datastax.com"
ASTRA_API_TOKEN = "AstraCS:KQtaGbjtjfWyroxBnOwnAJoZ:60c2bc256fb998419971e7260afa9301ad6e04c47493762bb6c61c508c63ec0b"

# Astra client setup
client = DataAPIClient(ASTRA_API_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_API_ENDPOINT)
collection = db.get_collection("storage")  # Use your created collection name

@app.route('/')
def index():
    return jsonify({"message": "Astra File Storage API is live."})

@app.route('/store', methods=['POST'])
def store_file():
    if 'folder' not in request.form or 'key' not in request.form or 'file' not in request.files:
        return jsonify({"error": "folder, key, and file required"}), 400

    folder = request.form['folder']
    key = request.form['key']
    file = request.files['file']
    filename = file.filename
    file_data = base64.b64encode(file.read()).decode("utf-8")

    try:
        doc_id = f"{folder}_{key}_{filename}"
        doc = {
            "_id": doc_id,
            "folder": folder,
            "key": key,
            "filename": filename,
            "content": file_data
        }
        collection.insert_one(doc)
        return jsonify({"success": True, "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/list', methods=['GET'])
def list_files():
    folder = request.args.get("folder")
    key = request.args.get("key")

    if not folder or not key:
        return jsonify({"error": "folder and key required"}), 400

    docs = collection.find({"folder": folder, "key": key})
    files = [doc["filename"] for doc in docs]
    return jsonify({"files": files})

@app.route('/download', methods=['GET'])
def download_file():
    folder = request.args.get("folder")
    key = request.args.get("key")
    filename = request.args.get("file")

    if not folder or not key or not filename:
        return jsonify({"error": "folder, key, and file required"}), 400

    doc_id = f"{folder}_{key}_{filename}"
    doc = collection.find_one({"_id": doc_id})

    if not doc:
        return jsonify({"error": "file not found"}), 404

    return jsonify({
        "filename": filename,
        "content_base64": doc["content"]
    })

@app.route('/delete', methods=['GET'])
def delete_file():
    folder = request.args.get("folder")
    key = request.args.get("key")
    filename = request.args.get("file")

    if not folder or not key or not filename:
        return jsonify({"error": "folder, key, and file required"}), 400

    doc_id = f"{folder}_{key}_{filename}"
    result = collection.delete_one({"_id": doc_id})

    return jsonify({"deleted": result.deleted_count == 1})
