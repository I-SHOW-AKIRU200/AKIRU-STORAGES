from flask import Flask, request, jsonify, send_file
from astrapy import DataAPIClient
import base64
import io
import traceback

app = Flask(__name__)

# Astra DB setup
client = DataAPIClient("AstraCS:KQtaGbjtjfWyroxBnOwnAJoZ:60c2bc256fb998419971e7260afa9301ad6e04c47493762bb6c61c508c63ec0b")
db = client.get_database_by_api_endpoint("https://dfecb377-3c46-4d76-947b-0d66cff1b2c7-us-east-2.apps.astra.datastax.com")
collection = db.get_collection("storage")

@app.route("/")
def home():
    return "🟢 Astra File Storage API Running"

@app.route("/store", methods=["POST"])
def store_file():
    try:
        folder = request.form.get("folder")
        key = request.form.get("key")
        file = request.files.get("file")

        if not folder or not key or not file:
            return jsonify({"error": "folder, key, and file required"}), 400

        content = file.read()
        encoded = base64.b64encode(content).decode("utf-8")
        doc_id = f"{folder}_{key}_{file.filename}"

        doc = {
            "_id": doc_id,
            "folder": folder,
            "key": key,
            "filename": file.filename,
            "data": encoded
        }

        collection.insert_one(doc)
        return jsonify({"success": True, "file": file.filename})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_file():
    try:
        folder = request.args.get("folder")
        key = request.args.get("key")
        filename = request.args.get("file")
        doc_id = f"{folder}_{key}_{filename}"

        doc = collection.find_one({"_id": doc_id})
        if not doc:
            return jsonify({"error": "file not found"}), 404

        file_data = base64.b64decode(doc["data"])
        return send_file(io.BytesIO(file_data), download_name=filename, as_attachment=True)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500

@app.route("/list", methods=["GET"])
def list_files():
    try:
        folder = request.args.get("folder")
        key = request.args.get("key")
        files = collection.find({"folder": folder, "key": key})
        result = [file["filename"] for file in files]
        return jsonify({"files": result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500

@app.route("/delete", methods=["POST"])
def delete_file():
    try:
        folder = request.form.get("folder")
        key = request.form.get("key")
        filename = request.form.get("file")
        doc_id = f"{folder}_{key}_{filename}"

        res = collection.delete_one({"_id": doc_id})
        if res["status"]["deletedCount"] == 0:
            return jsonify({"error": "file not found"}), 404

        return jsonify({"success": True, "file": filename})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "internal_error", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
