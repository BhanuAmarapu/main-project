# CloudDedup Pro: ML-Assisted Secure Hybrid Cloud Deduplication

CloudDedup Pro is a high-performance, secure cloud storage system that combines **Machine Learning (ML)** prediction with **Convergent Narrowing Storage (CNS)** to maximize storage efficiency and data security.

## 🚀 Key Features

-   **Secure Authentication**: Full login and registration system with **RBAC (Role-Based Access Control)**.
-   **AI Content Moderation**: Real-time TF-IDF-based analysis automatically rejects inappropriate uploads (explicit content, profanity, violence) before storage.
-   **Direct S3 Access**: Privileged users (admins) can view and stream files directly from the cloud.
-   **Enhanced Duplicate Detection**: 
    -   **Identical File Detection** (🔴): Detects exact duplicates via hash matching with red alerts and "EXACT MATCH" badges
    -   **Content Similarity Detection** (⚠️): Uses TF-IDF algorithm to detect near-duplicate files (60%+ content match) even with different names/sizes
    -   **Similar File Detection** (⚠️): Identifies files with similar metadata (name/size) but different content
    -   **S3 Location Display**: Shows storage location (S3 bucket or local) with cloud icons
    -   **User Choice**: "Store Anyway" or "Don't Store" options for all match types
-   **ML-Assisted Prediction**: Uses a Decision Tree model to predict duplicate likelihood before hashing, reducing computational overhead for unique files.
-   **CNS Secure Deduplication**: Implements convergent encryption (AES-256) where keys are derived from data content, ensuring only unique ciphertexts are stored.
-   **Hybrid Cloud Storage**: Seamlessly switches between local storage and **AWS S3** for enterprise-grade scalability.
-   **Integrity Auditing**: Third-Party Auditor (TPA) simulation with block-based hash-chain verification ensuring data remains uncorrupted.
-   **Premium Dashboard**: Real-time insights into deduplication rates, storage savings, and audit logs.

## 🛠️ Technology Stack

-   **Backend**: Python Flask
-   **Machine Learning**: Scikit-Learn (Decision Tree, TF-IDF Vectorizer)
-   **Encryption**: AES-256 (Cryptography lib)
-   **Cloud**: AWS S3 (Boto3)
-   **Database**: SQLite
-   **PDF Processing**: PyPDF2
-   **Frontend**: Bootstrap 5 + Bootstrap Icons

## 📋 Prerequisites

-   Python 3.8+
-   AWS Account (for S3 storage)
-   Windows/Linux/MacOS

## ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    cd "Hybrid ML-CNS Dedupliation System"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Setup Script** (Recommended):
    ```bash
    python scripts/setup.py
    ```
    This will create directories, initialize the database, and create a default admin user.

    **OR** manually initialize the database:
    ```bash
    python init_db.py
    ```

## ☁️ Configuring AWS S3

To use real cloud storage, update `config.py` or `.env`:

1.  Set `USE_S3 = True`.
2.  Provide your AWS credentials:
    ```python
    AWS_ACCESS_KEY = 'YOUR_ACCESS_KEY'
    AWS_SECRET_KEY = 'YOUR_SECRET_KEY'
    S3_BUCKET_NAME = 'YOUR_BUCKET_NAME'
    AWS_REGION = 'YOUR_REGION'
    ```

## 🏃 Running the Application

Start the Flask development server:
```bash
python run.py
```

**OR** run directly:
```bash
python app.py
```

Access the application at: `http://127.0.0.1:5000`

**Default Login**: 
- Username: `admin`
- Password: `admin123`

## 📂 Project Structure

-   `app.py`: Main Flask application and routing.
-   `ml_model.py`: ML prediction logic and training.
-   `dedup.py`: Deduplication and encryption engine.
-   `content_similarity.py`: TF-IDF content similarity detection.
-   `content_moderator.py`: AI content moderation with TF-IDF analysis.
-   `auditing.py`: Integrity verification module.
-   `utils.py`: Helper functions for S3, hashing, and logs.
-   `templates/`: UI components and pages.
-   `db/`: SQLite database and schema.

## 🔍 Duplicate Detection Feature

### How It Works

When you upload a file, the system performs intelligent duplicate detection:

1. **Hash Computation**: File hash (SHA-256) is computed immediately
2. **Exact Match Check**: System searches for identical files with the same hash
3. **Content Similarity Analysis**: TF-IDF algorithm analyzes file content to detect near-duplicates (60%+ match)
4. **Metadata Analysis**: ML model analyzes file size, name, and frequency
5. **Visual Alerts**: Color-coded alerts show match type with similarity percentages

### Match Types

#### 🔴 Identical Files (Exact Match)
- **Detection**: Files with identical hash (100% match)
- **Visual**: Red alert with "Identical File Found!" message
- **Display**: Table showing existing files with "EXACT MATCH" badges
- **Storage Info**: Shows S3 bucket location or local storage path
- **Action**: Choose "Store Anyway" (creates reference) or "Don't Store" (cancel)

#### ⚠️ Similar Files (Metadata Match)
- **Detection**: Files with similar name/size but different content
- **Visual**: Orange alert with "Potential Duplicate Detected"
- **Display**: Table showing similar files for comparison
- **Storage Info**: Shows where each similar file is stored
- **Action**: Review and decide whether to proceed with upload

#### 📊 Content Similarity Detection (TF-IDF)
- **Detection**: Uses TF-IDF (Term Frequency-Inverse Document Frequency) to detect near-duplicate files with 60%+ content similarity
- **Algorithm**: Computes cosine similarity between document vectors
- **Supported Files**: 
  - Text files: `.txt`, `.md`, `.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`, `.html`, `.css`, `.json`, `.xml`, `.csv`, `.log`, `.sql`
  - PDF files: Extracts text using PyPDF2
- **Visual**: Yellow alert with "Near-Duplicate Files Found" and similarity percentage
- **Display**: Table showing similar files with exact similarity scores (e.g., "85.3% Similar")
- **Features**:
  - Works even when files have different names or sizes
  - Detects renamed files, slightly modified versions, or paraphrased content
  - Shows download button for existing similar files
  - Displays top 5 most similar files
- **Action**: Choose "Store Anyway" or "Don't Store" after reviewing similar files

### User Workflow Example

```
1. User uploads "report.pdf" (5MB)
2. System detects identical file already exists in S3
3. Red alert appears with:
   - File details (name, size, hash)
   - Existing file location: "☁️ S3 Bucket: s3://my-bucket/abc123_report.pdf"
   - Download button to access existing file
4. User chooses:
   - "Store Anyway" → Creates ownership reference (saves storage)
   - "Don't Store" → Cancels upload
```

### Benefits

- **Storage Savings**: Avoid uploading duplicate files to S3
- **Cost Reduction**: Minimize cloud storage costs
- **Quick Access**: Download existing files instead of re-uploading
- **Transparency**: See exactly where files are stored (S3 or local)

## 🛡️ AI Content Moderation

### Overview

The system includes real-time AI content moderation that automatically scans uploaded files for inappropriate content **before** storage. Using TF-IDF machine learning algorithm, it intelligently detects and rejects:

- **EXPLICIT** content (adult, sexual, pornographic material)
- **PROFANITY** (curse words, vulgar language)
- **VIOLENCE** (violent content, weapons, hate speech)

### How It Works

1. **Upload Initiated**: User selects file to upload
2. **Pre-Storage Scan**: File is analyzed using TF-IDF algorithm
3. **Similarity Analysis**: Content is compared against known bad content patterns
4. **Decision**: 
   - If similarity ≥ 35% → ❌ **REJECTED** (file deleted, user notified, admin alerted)
   - If similarity < 35% → ✅ **ALLOWED** (continues to deduplication)

### TF-IDF Algorithm

The moderation system uses **Term Frequency-Inverse Document Frequency (TF-IDF)** for intelligent content analysis:

```
Training Data → TF-IDF Vectorization → Cosine Similarity → Rejection Decision
```

**Benefits over keyword matching**:
- ✅ Context-aware analysis
- ✅ Fewer false positives
- ✅ Confidence scoring
- ✅ Auto-categorization

### Supported File Types

**Text Files** (Full Content Analysis):
- `.txt`, `.md`, `.log`, `.csv`, `.json`, `.xml`
- `.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`, `.html`, `.css`, `.sql`
- `.pdf` (text extraction via PyPDF2)

**Image Files** (Filename Analysis):
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- Checks filenames for suspicious keywords (e.g., "gun.jpg", "nude.png")

### What Happens on Rejection

1. 🚫 **Upload Rejected**: User sees "Upload rejected due to inappropriate content"
2. 📝 **Logged**: Rejection saved to `moderation_logs` table with details
3. 🚨 **Admin Alert**: Automatic alert created in `suspicious_activities` table
4. 🗑️ **File Deleted**: Temp file immediately removed from server
5. 📊 **Trackable**: Admins can review all rejections at `/admin/moderation`

### Admin Moderation Panel

Admins can access `/admin/moderation` to:
- View all rejected uploads
- See user details, violation type, and flagged keywords
- Filter by reviewed/unreviewed status
- Add reviewer notes
- Track moderation statistics

### Configuration

Adjust moderation threshold in `content_moderator.py`:
```python
moderator = ContentModerator(threshold=0.35)  # 35% similarity
```

**Threshold Recommendations**:
- `0.30` (30%) - Strict mode
- `0.35` (35%) - **Default** (balanced)
- `0.40` (40%) - Lenient mode

## 🛡️ Security Note
This project uses AES-256 encryption. Ensure your `SECRET_KEY` in `config.py` is kept secure in production environments.

