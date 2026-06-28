# IMAGEIQ – AI-Powered Image Compression System Using MiniBatch K-Means Clustering

## 🎥 Watch Live Demo

Before exploring the project, watch the complete live demonstration to see how IMAGEIQ compresses images using Unsupervised Machine Learning and how different K-values influence image quality and compression performance.

**Live Demo:**
https://www.linkedin.com/posts/dikachi-baron-a4a380356_imageiq-machinelearning-artificialintelligence-ugcPost-7476978533035143168-14QM/

---

# Overview

IMAGEIQ is an AI-powered image compression system built with **Unsupervised Machine Learning**, leveraging **MiniBatch K-Means Clustering** to intelligently reduce image complexity while preserving visual quality.

Unlike traditional compression techniques that primarily focus on resizing dimensions or reducing file quality, IMAGEIQ learns the dominant color patterns within an image and reconstructs the image using a smaller, representative color palette.

A single digital image may contain millions—or even billions—of possible color combinations. IMAGEIQ transforms these massive color spaces into **K dominant color clusters**, where K is selected by the user, providing full control over the balance between image quality and compression efficiency.

The system is deployed through a lightweight Flask web application, enabling users to upload images, select compression levels, visualize before-and-after results, and download optimized outputs instantly.

---

# Project Objectives

IMAGEIQ was designed to solve several practical challenges:

* Reduce image storage requirements.
* Lower bandwidth consumption.
* Accelerate image delivery on websites and applications.
* Preserve visual quality during compression.
* Provide adjustable compression levels through K-values.
* Demonstrate real-world applications of Unsupervised Machine Learning.

---

# Technologies Used

* Python
* Flask
* NumPy
* Pillow (PIL)
* Scikit-Learn
* MiniBatch K-Means Clustering
* HTML/CSS
* Base64 Encoding

---

# Machine Learning Pipeline

```text
Image Upload
      ↓
Input Validation
      ↓
Image Loading (Pillow)
      ↓
RGB Conversion
      ↓
NumPy Pixel Extraction
      ↓
Pixel Sampling (Max: 8,000 Pixels)
      ↓
MiniBatch K-Means Training
      ↓
Dominant Color Discovery
      ↓
Pixel-to-Centroid Assignment
      ↓
Image Reconstruction
      ↓
JPEG Optimization
      ↓
Base64 Encoding
      ↓
Flask Rendering
      ↓
Downloadable Compressed Output
```

---

# System Workflow

## 1. Image Upload

Users upload images through the Flask web interface.

Supported formats include:

* PNG
* JPG
* JPEG
* WEBP
* GIF

The system validates every uploaded file before processing.

---

## 2. Input Validation

The application performs multiple validation checks:

### File Validation

* Image existence check
* File extension verification
* Supported format validation

### K-Value Validation

Users select a K-value between:

```text
1 ≤ K ≤ 50
```

The K-value represents the number of dominant colors preserved in the compressed image.

Higher K-values preserve more details.

Lower K-values achieve stronger compression.

---

# Image Processing Pipeline

## Image Loading

The uploaded image is loaded using Pillow:

```python
image = Image.open(image_file)
```

All images are converted into RGB format to ensure compatibility:

```python
image = image.convert("RGB")
```

This allows the system to process:

* Transparent PNGs
* GIF files
* Indexed color images
* RGBA images

---

## Image-to-Pixel Transformation

The image is converted into a NumPy array:

```python
image_array = np.array(image)
```

Each pixel becomes:

```text
(R, G, B)
```

The image shape is transformed into:

```text
Height × Width × 3
```

This numerical representation allows machine learning algorithms to analyze color patterns.

---

# Fast Pixel Sampling

Processing millions of pixels directly can be computationally expensive.

To improve performance, IMAGEIQ introduces pixel sampling:

```python
MAX_SAMPLE_PIXELS = 8000
```

If an image contains more than 8,000 pixels:

* Random sampling is performed.
* Only the sampled pixels are used for centroid discovery.
* The full-resolution image is reconstructed afterward.

Benefits include:

* Faster processing
* Reduced memory consumption
* Better scalability
* Improved responsiveness

---

# MiniBatch K-Means Clustering

IMAGEIQ uses:

```python
MiniBatchKMeans(
    n_clusters=k,
    random_state=42,
    n_init=3,
    max_iter=100
)
```

Instead of processing all pixels simultaneously, MiniBatch K-Means operates on smaller batches, providing substantial performance improvements compared to traditional K-Means.

Advantages include:

* Faster convergence
* Lower memory requirements
* Better scalability
* Efficient processing for high-resolution images

---

# Color Clustering

The model discovers:

```text
K Dominant Colors
```

Each cluster center represents one major color within the image.

For example:

```text
K = 30
```

means:

```text
30 Representative Colors
```

The algorithm learns these dominant colors automatically without labels, making it a true Unsupervised Learning application.

---

# Image Reconstruction

Once the dominant colors are identified:

Every pixel is assigned to its nearest color centroid.

The system then reconstructs the image using these representative colors.

The final image:

* Preserves original dimensions.
* Maintains visual similarity.
* Uses significantly fewer unique colors.
* Achieves smaller file sizes.

---

# JPEG Optimization

Both original and compressed images are converted to optimized JPEG outputs:

```python
quality = 85
```

Benefits include:

* Smaller payload sizes
* Faster browser rendering
* Lower storage requirements
* Improved network performance

---

# Flask Web Application

The user interacts with IMAGEIQ through a Flask-powered interface.

Application Flow:

```text
User
 ↓
Upload Image
 ↓
Select K Value
 ↓
Process Image
 ↓
MiniBatch K-Means Compression
 ↓
Display Results
 ↓
Download Compressed Image
```

---

# Results Page

The results interface provides:

### Original Image

The full-resolution uploaded image.

### Compressed Image

The reconstructed image using K dominant colors.

### Download Functionality

Users can immediately download optimized outputs.

### Visual Comparison

Side-by-side comparison enables users to evaluate:

* Quality retention
* Compression effectiveness
* K-value influence

---

# System Optimizations

IMAGEIQ implements several performance enhancements:

✅ MiniBatch K-Means

✅ Random Pixel Sampling

✅ Reduced n_init (3)

✅ Maximum Iterations (100)

✅ Dynamic Batch Processing

✅ JPEG Optimization

✅ Memory-Efficient Processing

✅ High-Resolution Image Support

---

# Business Value

IMAGEIQ provides practical benefits across multiple industries.

## Reduced Storage Costs

Compressed images occupy significantly less disk space.

---

## Lower Bandwidth Usage

Smaller files require fewer network resources.

---

## Faster Web Applications

Optimized images improve:

* Website loading speed
* Mobile responsiveness
* User experience

---

## Scalable Deployment

The system is suitable for:

* E-commerce platforms
* Content management systems
* Cloud storage services
* Mobile applications
* Image hosting platforms

---

## User-Controlled Compression

Users determine the balance between:

```text
Image Quality
vs
Compression Efficiency
```

through adjustable K-values.

---

# Educational Value

IMAGEIQ demonstrates practical applications of:

* Unsupervised Learning
* MiniBatch K-Means Clustering
* Computer Vision
* Color Quantization
* Image Processing
* Web Deployment with Flask

It serves as a real-world example of how machine learning can solve everyday engineering problems.

---

# Future Improvements

Potential enhancements include:

* Batch Image Compression
* Drag-and-Drop Upload Support
* Cloud Deployment
* REST API Integration
* GPU Acceleration
* Additional Compression Algorithms
* Compression Statistics Dashboard
* Real-Time Processing Analytics

---

# Author

## Dikachi Baron

AI Engineer | Machine Learning Engineer | Data Scientist

Building intelligent systems that transform complex data into practical and scalable solutions.

---

⭐ If you found this project useful, consider giving the repository a star and sharing your feedback.
