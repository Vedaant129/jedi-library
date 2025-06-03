from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
BOOKS_FILE = 'books.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load books from JSON
def load_books():
    if not os.path.exists(BOOKS_FILE):
        return []
    with open(BOOKS_FILE, 'r') as f:
        return json.load(f)

# Save books to JSON
def save_books(books):
    with open(BOOKS_FILE, 'w') as f:
        json.dump(books, f, indent=2)

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    selected_category = request.args.get('category', '')
    tag_filter = request.args.get('tag', '')
    sort_by = request.args.get('sort', '')

    books = load_books()

    if query:
        books = [b for b in books if query in b['title'].lower() or query in b['author'].lower()]

    if selected_category:
        books = [b for b in books if b['category'] == selected_category]

    if tag_filter:
        books = [b for b in books if tag_filter in b.get('tags', [])]

    if sort_by == 'title':
        books.sort(key=lambda x: x['title'].lower())
    elif sort_by == 'author':
        books.sort(key=lambda x: x['author'].lower())
    elif sort_by == 'year':
        books.sort(key=lambda x: x.get('year', 0), reverse=True)

    categories = sorted(set(b['category'] for b in load_books() if b.get('category')))
    return render_template('index.html', books=books, categories=categories, selected_category=selected_category)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = int(request.form['year'])
        category = request.form['category']
        tags = [t.strip() for t in request.form['tags'].split(',') if t.strip()]
        file = request.files['file']

        if file and title and author:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            books = load_books()
            books.append({
                'title': title,
                'author': author,
                'year': year,
                'category': category,
                'tags': tags,
                'filename': filename
            })
            save_books(books)

            return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
