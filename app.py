import io
import os
import re
import tempfile
import zipfile

from flask import Flask, jsonify, render_template, request, send_file
from pypdf import PdfReader, PdfWriter

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB max upload

UPLOAD_DIR = tempfile.mkdtemp()


def get_top_level_bookmarks(outline, reader):
    """Extract only top-level bookmarks (skip nested sub-chapters)."""
    bookmarks = []
    for item in outline:
        if isinstance(item, list):
            # Nested bookmarks (sub-chapters) — skip them
            continue
        try:
            page_num = reader.get_destination_page_number(item)
            bookmarks.append({"title": item.title, "page": page_num})
        except Exception:
            continue
    return bookmarks


def sanitize_filename(name):
    """Sanitize a string for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.strip(". ")
    if not name:
        name = "chapter"
    return name[:100]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file"}), 400

    pdf_bytes = file.read()

    # Save for later splitting
    file_id = os.urandom(8).hex()
    filepath = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {e}"}), 400

    total_pages = len(reader.pages)

    if not reader.outline:
        return jsonify({
            "file_id": file_id,
            "filename": file.filename,
            "total_pages": total_pages,
            "chapters": [],
        })

    bookmarks = get_top_level_bookmarks(reader.outline, reader)

    # Deduplicate consecutive bookmarks on the same page with the same title
    deduped = []
    for bm in bookmarks:
        if deduped and deduped[-1]["title"] == bm["title"] and deduped[-1]["page"] == bm["page"]:
            continue
        deduped.append(bm)
    bookmarks = deduped

    # Compute page ranges
    chapters = []
    for i, bm in enumerate(bookmarks):
        start = bm["page"]
        end = bookmarks[i + 1]["page"] - 1 if i + 1 < len(bookmarks) else total_pages - 1
        if end < start:
            end = start
        chapters.append({
            "index": i,
            "title": bm["title"],
            "start_page": start,
            "end_page": end,
            "page_count": end - start + 1,
        })

    return jsonify({
        "file_id": file_id,
        "filename": file.filename,
        "total_pages": total_pages,
        "chapters": chapters,
    })


@app.route("/api/split", methods=["POST"])
def split():
    data = request.get_json()
    if not data or "file_id" not in data or "chapters" not in data:
        return jsonify({"error": "Missing file_id or chapters"}), 400

    file_id = data["file_id"]
    selected = data["chapters"]  # list of chapter objects with title, start_page, end_page

    if not selected:
        return jsonify({"error": "No chapters selected"}), 400

    filepath = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found. Please re-upload."}), 404

    try:
        reader = PdfReader(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {e}"}), 500

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, chapter in enumerate(selected):
            writer = PdfWriter()
            start = chapter["start_page"]
            end = chapter["end_page"]

            for page_num in range(start, min(end + 1, len(reader.pages))):
                writer.add_page(reader.pages[page_num])

            pdf_buffer = io.BytesIO()
            writer.write(pdf_buffer)
            pdf_buffer.seek(0)

            safe_title = sanitize_filename(chapter["title"])
            filename = f"{i + 1:02d} - {safe_title}.pdf"
            zf.writestr(filename, pdf_buffer.read())

    zip_buffer.seek(0)

    # Use original filename as base for ZIP name
    original_name = data.get("filename", "split")
    zip_name = os.path.splitext(original_name)[0] + "_chapters.zip"

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=zip_name,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
