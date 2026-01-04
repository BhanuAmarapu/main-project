# CloudDedup Pro: ML-Assisted Secure Hybrid Cloud Deduplication

CloudDedup Pro is a high-performance, secure cloud storage system that combines **Machine Learning (ML)** prediction with **Convergent Narrowing Storage (CNS)** to maximize storage efficiency and data security.

## 🚀 Key Features

-   **Secure Authentication**: Full login and registration system with **RBAC (Role-Based Access Control)**.
-   **Direct S3 Access**: Privileged users (admins) can view and stream files directly from the cloud.
-   **Duplicate Alerts**: Real-time user notification if a duplicate file is detected during upload.
-   **ML-Assisted Prediction**: Uses a Decision Tree model to predict duplicate likelihood before hashing, reducing computational overhead for unique files.
-   **CNS Secure Deduplication**: Implements convergent encryption (AES-256) where keys are derived from data content, ensuring only unique ciphertexts are stored.
-   **Hybrid Cloud Storage**: Seamlessly switches between local storage and **AWS S3** for enterprise-grade scalability.
-   **Integrity Auditing**: Third-Party Auditor (TPA) simulation with block-based hash-chain verification ensuring data remains uncorrupted.
-   **Premium Dashboard**: Real-time insights into deduplication rates, storage savings, and audit logs.

## 🛠️ Technology Stack

-   **Backend**: Python Flask
-   **Machine Learning**: Scikit-Learn (Decision Tree)
-   **Encryption**: AES-256 (Cryptography lib)
-   **Cloud**: AWS S3 (Boto3)
-   **Database**: SQLite
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
-   `auditing.py`: Integrity verification module.
-   `utils.py`: Helper functions for S3, hashing, and logs.
-   `templates/`: UI components and pages.
-   `db/`: SQLite database and schema.

## 🛡️ Security Note
This project uses AES-256 encryption. Ensure your `SECRET_KEY` in `config.py` is kept secure in production environments.
