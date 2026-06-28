from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from image_processor import compress_image

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_size(size_bytes):
    """Convert bytes to human-readable KB / MB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        flash('No image uploaded')
        return redirect(url_for('index'))
    
    file = request.files['image']
    k = request.form.get('k', 30)
    
    if file.filename == '':
        flash('No image selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an image (PNG, JPG, JPEG, WEBP, GIF).')
        return redirect(url_for('index'))
    
    try:
        k = int(k)
        if k < 1 or k > 50:
            flash('K value must be between 1 and 50')
            return redirect(url_for('index'))
    except ValueError:
        flash('Invalid K value')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        file.seek(0)
        image_bytes = file.read()

        result = compress_image(image_bytes, k, filename)

        original_size = result['original_size']
        compressed_size = result['compressed_size']
        savings = original_size - compressed_size
        ratio = (savings / original_size * 100) if original_size > 0 else 0

        return render_template('result.html',
                               original_image=result['original_b64'],
                               compressed_image=result['compressed_b64'],
                               filename=filename,
                               width=result['width'],
                               height=result['height'],
                               original_size=format_size(original_size),
                               compressed_size=format_size(compressed_size),
                               savings=format_size(savings),
                               ratio=round(ratio, 1),
                               k=k)
    except Exception as e:
        flash(f'Error processing image: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)