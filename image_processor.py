import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans
import io
import base64
import os

# Max pixels fed into the clustering algorithm.
MAX_SAMPLE_PIXELS = 8_000


def compress_image(image_bytes, k, filename=None):
    """
    Takes uploaded image bytes and k clusters.
    Returns a dict containing:
      - original_b64   : base64 data URI of the TRUE original file
      - compressed_b64 : base64 data URI of the compressed image
      - width, height  : image dimensions
      - original_size  : size of the uploaded file in bytes
      - compressed_size: size of the compressed JPEG buffer in bytes
    """
    original_size = len(image_bytes)
    
    # Detect original mime type from filename or bytes
    ext = (filename or '').rsplit('.', 1)[-1].lower()
    if ext in ('jpg', 'jpeg'):
        orig_mime = 'image/jpeg'
    elif ext == 'png':
        orig_mime = 'image/png'
    elif ext == 'webp':
        orig_mime = 'image/webp'
    elif ext == 'gif':
        orig_mime = 'image/gif'
    else:
        orig_mime = 'image/jpeg'
    
    # True original as base64 (exact file, not re-encoded)
    original_b64 = f"data:{orig_mime};base64,{base64.b64encode(image_bytes).decode()}"

    # Open for processing
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    width, height = image.size
    image_array = np.array(image)
    all_pixels = image_array.reshape(-1, 3).astype(np.float32)

    # ── Step 1: sample pixels for fast centroid finding ──────────────────
    total_pixels = len(all_pixels)
    if total_pixels > MAX_SAMPLE_PIXELS:
        rng = np.random.default_rng(42)
        sample_idx = rng.choice(total_pixels, size=MAX_SAMPLE_PIXELS, replace=False)
        sample_pixels = all_pixels[sample_idx]
    else:
        sample_pixels = all_pixels

    # ── Step 2: fit MiniBatchKMeans on the sample ─────────────────────────
    kmeans = MiniBatchKMeans(
        n_clusters=k,
        random_state=42,
        n_init=3,
        max_iter=100,
        batch_size=min(2048, len(sample_pixels)),
    )
    kmeans.fit(sample_pixels)

    # ── Step 3: predict labels for ALL pixels (full resolution) ──────────
    labels = kmeans.predict(all_pixels)
    centroids = kmeans.cluster_centers_

    compressed_pixels = centroids[labels]
    compressed_array = compressed_pixels.reshape(image_array.shape).astype('uint8')
    compressed_pil = Image.fromarray(compressed_array)

    # ── Step 4: encode compressed image with adaptive quality ────────────
    # Try quality 85 first; if it's bigger than original, drop to 60
    compressed_b64, compressed_size = _encode_jpeg(compressed_pil, quality=85)
    if compressed_size > original_size and original_size > 0:
        compressed_b64, compressed_size = _encode_jpeg(compressed_pil, quality=60)

    return {
        'original_b64': original_b64,
        'compressed_b64': compressed_b64,
        'width': width,
        'height': height,
        'original_size': original_size,
        'compressed_size': compressed_size,
    }


def _encode_jpeg(img, quality=85):
    """Helper: encode PIL image as JPEG and return (base64_data_uri, size_in_bytes)."""
    buffered = io.BytesIO()
    rgb_img = img if img.mode == 'RGB' else img.convert('RGB')
    rgb_img.save(buffered, format='JPEG', quality=quality, optimize=True)
    data = buffered.getvalue()
    size = len(data)
    b64 = f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    return b64, size