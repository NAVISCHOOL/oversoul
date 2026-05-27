import os, json, time, hashlib
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

MANUSCRIPT = os.path.join(os.path.dirname(__file__), "final_content.md")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), ".editor_backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def read_file():
    with open(MANUSCRIPT, "r", encoding="utf-8") as f:
        return f.read()

def write_file(content):
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(BACKUP_DIR, f"final_content_{ts}.md")
    with open(backup, "w", encoding="utf-8") as f:
        f.write(read_file())
    with open(MANUSCRIPT, "w", encoding="utf-8") as f:
        f.write(content)

def file_hash():
    return hashlib.md5(read_file().encode()).hexdigest()

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "editor.html")

@app.route("/api/content", methods=["GET"])
def get_content():
    return jsonify({"content": read_file(), "hash": file_hash()})

@app.route("/api/content", methods=["POST"])
def save_content():
    data = request.get_json()
    write_file(data["content"])
    return jsonify({"ok": True, "hash": file_hash()})

@app.route("/api/patch", methods=["POST"])
def patch_content():
    data = request.get_json()
    old = data.get("old", "")
    new = data.get("new", "")
    content = read_file()
    if old not in content:
        return jsonify({"ok": False, "error": "old string not found"}), 404
    content = content.replace(old, new, 1)
    write_file(content)
    return jsonify({"ok": True, "content": content, "hash": file_hash()})

@app.route("/api/hash", methods=["GET"])
def get_hash():
    return jsonify({"hash": file_hash()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
