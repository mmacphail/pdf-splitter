# PDF Splitter - Claude Code Guide

## Project Overview
Web app that splits PDFs by their bookmarks/outlines into individual chapter files, served as a ZIP download.

## Stack
- **Backend**: Python 3 + Flask
- **PDF processing**: pypdf (`PdfReader` for bookmarks, `PdfWriter` for splitting)
- **Frontend**: Vanilla HTML/CSS/JS (no build step)

## Project Structure
```
app.py              # Flask server - all API routes and PDF logic
templates/index.html # Single-page frontend (includes inline JS)
static/style.css    # Styles
requirements.txt    # Dependencies: flask, pypdf
```

## Running
```
pip install -r requirements.txt
python app.py
```
Server runs on `http://localhost:5000` with debug mode.

## API Routes
- `GET /` — serves the frontend
- `POST /api/upload` — accepts PDF file upload, returns JSON with `file_id` and detected chapters
- `POST /api/split` — accepts `file_id` + selected chapters, returns a ZIP file

## Key Implementation Details
- Uploaded PDFs are stored in a temp directory (`tempfile.mkdtemp()`) identified by a random `file_id`
- Bookmarks are read from `reader.outline` and flattened recursively (nested sub-chapters supported)
- Page ranges: each chapter runs from its bookmark page to the next bookmark's page - 1
- Max upload size: 200 MB
- Filenames in the ZIP are sanitized and numbered (e.g., `01 - Chapter Title.pdf`)

## Common Tasks
- **Add a new API route**: add to `app.py` with `@app.route()`
- **Change styles**: edit `static/style.css`
- **Modify frontend behavior**: JS is inline at the bottom of `templates/index.html`
