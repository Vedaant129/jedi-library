from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
METADATA_FILE = os.path.join(os.path.dirname(__file__), 'metadata.json')
ALLOWED_EXTENSIONS = {'pdf', 'epub', 'mobi'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_books():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_books(books):
    with open(METADATA_FILE, 'w') as f:
        json.dump(books, f, indent=2)

@app.route("/")
def index():
    books = load_books()
    search_query = request.args.get('q', '').lower()
    category_filter = request.args.get('category', '')
    filtered_books = []

    for book in books:
        matches_search = search_query in book['title'].lower() or search_query in book['author'].lower()
        matches_category = (category_filter == '' or book['category'] == category_filter)
        if matches_search and matches_category:
            filtered_books.append(book)

    categories = sorted(set(book['category'] for book in books))
    return render_template("index.html", books=filtered_books, categories=categories, selected_category=category_filter, search_query=search_query)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get('file')
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        summary = request.form.get('summary')
        category = request.form.get('category')
        tags = request.form.get('tags', '')

        if not file or not allowed_file(file.filename):
            return "Invalid or missing file", 400

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        books = load_books()
        books.append({
            "filename": filename,
            "title": title,
            "author": author,
            "year": int(year) if year.isdigit() else None,
            "summary": summary,
            "tags": [tag.strip() for tag in tags.split(',') if tag.strip()],
            "category": category
        })
        save_books(books)
        return redirect(url_for('index'))

    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

