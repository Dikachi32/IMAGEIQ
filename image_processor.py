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


# ═══════════════════════════════════════════════════════════════════════════
# LOSSLESS COMPRESSION PIPELINE — Smart Format Selection
# ═══════════════════════════════════════════════════════════════════════════

def compress_lossless(image_bytes, filename=None):
    """
    Lossless compression pipeline with smart format selection.

    Strategy:
      - If original is PNG/GIF/WebP → re-encode as optimized PNG (lossless)
      - If original is JPEG → re-encode as optimized JPEG at quality 100 (visually lossless)
      - Always pick the smaller of the two results

    This ensures we never produce a file LARGER than a reasonable alternative.
    """
    original_size = len(image_bytes)

    # Detect original extension and mime type
    ext = (filename or '').rsplit('.', 1)[-1].lower()
    if ext in ('jpg', 'jpeg'):
        orig_mime = 'image/jpeg'
        orig_format = 'JPEG'
    elif ext == 'png':
        orig_mime = 'image/png'
        orig_format = 'PNG'
    elif ext == 'webp':
        orig_mime = 'image/webp'
        orig_format = 'WEBP'
    elif ext == 'gif':
        orig_mime = 'image/gif'
        orig_format = 'GIF'
    else:
        orig_mime = 'image/jpeg'
        orig_format = 'JPEG'

    # True original as base64
    original_b64 = f"data:{orig_mime};base64,{base64.b64encode(image_bytes).decode()}"

    # Open image preserving original mode
    image = Image.open(io.BytesIO(image_bytes))
    orig_mode = image.mode
    width, height = image.size

    # ── Strategy 1: Optimized PNG (truly lossless, supports all modes) ──
    png_buffer = io.BytesIO()
    # Preserve original mode if PNG-compatible; otherwise convert to RGB
    if orig_mode not in ('RGB', 'RGBA', 'L', 'P', '1', 'LA', 'I'):
        png_img = image.convert('RGB')
        png_mode = 'RGB'
    else:
        png_img = image
        png_mode = orig_mode

    png_img.save(png_buffer, format='PNG', optimize=True, compress_level=9)
    png_data = png_buffer.getvalue()
    png_size = len(png_data)

    # ── Strategy 2: Optimized JPEG quality 100 (visually lossless for photos) ──
    # JPEG at q=100 is "visually lossless" — human eye can't distinguish from original
    # We convert to RGB for JPEG (no alpha support)
    jpeg_buffer = io.BytesIO()
    jpeg_img = image.convert('RGB') if orig_mode != 'RGB' else image
    jpeg_img.save(jpeg_buffer, format='JPEG', quality=100, optimize=True)
    jpeg_data = jpeg_buffer.getvalue()
    jpeg_size = len(jpeg_data)

    # ── Pick the winner: whichever is smaller ────────────────────────────
    if png_size <= jpeg_size:
        compressed_data = png_data
        compressed_size = png_size
        output_mime = 'image/png'
        output_format = 'PNG'
        algorithm = 'PNG Optimize (Lossless)'
    else:
        compressed_data = jpeg_data
        compressed_size = jpeg_size
        output_mime = 'image/jpeg'
        output_format = 'JPEG'
        algorithm = 'JPEG Quality 100 (Visually Lossless)'

    # If BOTH are larger than original, fall back to returning the original
    # (no point in "compressing" to something bigger)
    if compressed_size >= original_size:
        compressed_data = image_bytes
        compressed_size = original_size
        output_mime = orig_mime
        output_format = orig_format
        algorithm = 'Original (Already Optimized)'

    compressed_b64 = f"data:{output_mime};base64,{base64.b64encode(compressed_data).decode()}"

    return {
        'original_b64': original_b64,
        'compressed_b64': compressed_b64,
        'width': width,
        'height': height,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'algorithm': algorithm,
        'output_format': output_format,
    }