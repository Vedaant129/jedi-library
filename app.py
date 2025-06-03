from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'books'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    books = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', books=books)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['book']
        if file and file.filename.endswith('.pdf'):
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/read/<filename>')
def read(filename):
    return render_template('read.html', filename=filename)

@app.route('/books/<filename>')
def get_book(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
