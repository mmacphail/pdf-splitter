# PDF Splitter

A simple web app to split PDF files by their bookmarks (table of contents) into individual chapter files.

## Features

- **Drag & drop** or file picker to upload a PDF
- **Automatic detection** of bookmarks/outlines (chapters, sections, etc.)
- **Selective splitting** — choose which chapters to extract via checkboxes
- **ZIP download** — get all selected chapters as individually named PDF files
- No external services — everything runs locally

## Requirements

- Python 3.8+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

1. Drop a PDF onto the upload zone (or click to browse)
2. Review the list of detected chapters
3. Uncheck any chapters you don't need
4. Click **Split and download**
5. A ZIP file containing one PDF per chapter is downloaded

## How It Works

The app reads the PDF's bookmark/outline metadata using [pypdf](https://github.com/py-pdf/pypdf). Each bookmark maps to a page number — the app uses consecutive bookmarks to determine page ranges, then extracts each range into a separate PDF file.

If a PDF has no bookmarks, the app will display a warning message.

## Project Structure

```
pdfsplitter/
├── app.py               # Flask server and PDF processing logic
├── templates/
│   └── index.html       # Web interface
├── static/
│   └── style.css        # Styles
└── requirements.txt     # Python dependencies
```

## Limitations

- Only works with PDFs that have bookmarks/outlines embedded
- Uploaded files are stored temporarily in memory — not suited for production deployment without cleanup
- No authentication or multi-user session management
