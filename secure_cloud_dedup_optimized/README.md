# Secure Cloud Deduplication System - Optimized

A comprehensive secure cloud deduplication system with ML-assisted duplicate detection, convergent encryption, Proof of Ownership (PoW) verification, and cloud storage integration.

## Features

### Core Features
- **ML-Assisted Deduplication**: Machine learning-based duplicate prediction
- **Convergent Encryption**: Content-based encryption for secure deduplication
- **Optimized Parallel Encryption**: 2-3x faster encryption through multi-threading
- **Block-Level Deduplication**: Fixed and variable-size chunkingwhy
- **Proof of Ownership (PoW)**: Adaptive difficulty verification
- **Cloud Storage Integration**: AWS S3 support with local caching

### Advanced Features
- **Bloom Filters**: Fast duplicate detection with compressed storage
- **KEK Tree**: Hierarchical key management
- **Lazy Update Strategy**: Batched updates for performance
- **Performance Monitoring**: Real-time metrics and analytics dashboard
- **In-Memory Caching**: LRU cache for hash lookups
- **User Authentication**: Role-based access control

## Project Structure

```
secure_cloud_dedup_optimized/
├── backend/                    # Core backend modules
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── models.py              # Database models
│   ├── dedup_manager.py       # Deduplication engine
│   ├── pow_manager.py         # PoW verification
│   ├── encryption.py          # Traditional encryption
│   ├── optimized_encryption.py # Parallel encryption
│   ├── ownership_manager.py   # Ownership management
│   ├── block_level_dedup.py   # Block-level deduplication
│   ├── performance_monitor.py # Performance tracking
│   └── cloud_utils.py         # S3 integration
│
├── cloud_simulator/           # Cloud simulation components
│   ├── bloom_filter.py        # Basic Bloom filter
│   ├── optimized_bloom_filter.py # Compressed Bloom filter
│   ├── kek_tree.py            # KEK tree implementation
│   ├── lazy_update.py         # Lazy update strategy
│   ├── adaptive_pow.py        # Adaptive PoW
│   └── cloud_storage.py       # Cloud storage simulator
│
├── database/                  # Database layer
│   ├── schema.sql             # Database schema
│   ├── db_manager.py          # Database operations
│   └── cache_manager.py       # In-memory cache
│
├── templates/                 # HTML templates
├── static/                    # CSS, JS, images
├── storage/                   # File storage
├── scripts/                   # Utility scripts
└── logs/                      # Application logs
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- (Optional) AWS account for S3 integration

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd secure_cloud_dedup_optimized
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open browser: `http://127.0.0.1:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## Configuration

### Environment Variables (.env)

- `SECRET_KEY`: Flask secret key
- `USE_S3`: Enable AWS S3 integration (True/False)
- `AWS_ACCESS_KEY`: AWS access key
- `AWS_SECRET_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket name
- `POW_DIFFICULTY`: PoW difficulty level (2-6)
- `POW_ADAPTIVE`: Enable adaptive PoW (True/False)
- `PARALLEL_WORKERS`: Number of parallel encryption workers

### Advanced Configuration (config.yaml)

Edit `config.yaml` for advanced settings:
- Performance tuning
- Bloom filter parameters
- Cache settings
- Upload limits
- Cloud simulation parameters

## Usage

### Upload Files
1. Login to the system
2. Navigate to Upload page
3. Select file and choose encryption method
4. System automatically detects duplicates

### View Dashboard
- Real-time performance metrics
- Deduplication statistics
- Encryption performance comparison
- System overview

### Manage Files
- View all uploaded files
- Download files (automatic decryption)
- Share files with other users

## Performance Optimization

### Optimized vs Traditional Encryption
- **Traditional**: Single-threaded convergent encryption
- **Optimized**: Multi-threaded parallel chunked encryption
- **Speedup**: 2-3x faster for large files

### Bloom Filter Benefits
- Fast duplicate detection (O(k) time)
- Low memory footprint with compression
- < 1% false positive rate

### Caching
- LRU cache for hash lookups
- Configurable TTL and size
- Significant performance improvement for repeated operations

## Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# Deduplication tests
python scripts/test_dedup.py

# Performance benchmarks
python scripts/benchmark.py

# Stress tests
python scripts/stress_test.py
```

### Generate Test Data
```bash
python scripts/generate_test_data.py
```

## Security Features

- **Convergent Encryption**: Content-based encryption ensures identical files produce identical ciphertexts
- **Proof of Ownership**: Prevents unauthorized access to deduplicated files
- **User Authentication**: Secure login with password hashing
- **Audit Logging**: Complete audit trail of all actions
- **Access Control**: Role-based permissions (user/admin)

## Architecture

### Deduplication Flow
1. User uploads file
2. System calculates file hash
3. Bloom filter quick check for duplicates
4. Database verification
5. If duplicate: Reference existing file
6. If unique: Encrypt and store
7. Update Bloom filter and cache

### Key Management (KEK Tree)
- Hierarchical key structure
- Efficient key updates
- Lazy propagation for performance

## API Endpoints

- `GET /`: Homepage
- `POST /register`: User registration
- `POST /login`: User login
- `GET /logout`: User logout
- `POST /upload`: File upload
- `GET /files`: List user files
- `GET /download/<id>`: Download file
- `GET /dashboard`: Performance dashboard
- `GET /api/stats`: System statistics (JSON)
- `GET /api/metrics/realtime`: Real-time metrics (JSON)

## Troubleshooting

### Database Issues
```bash
# Reinitialize database
python scripts/setup.py
```

### S3 Connection Issues
- Verify AWS credentials in `.env`
- Check S3 bucket permissions
- Ensure bucket region matches configuration

### Performance Issues
- Adjust `PARALLEL_WORKERS` in `.env`
- Increase cache size in `config.yaml`
- Enable compression for better storage efficiency

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check documentation
- Review logs in `logs/` directory
- Examine performance metrics in dashboard

## Acknowledgments

Built with:
- Flask web framework
- SQLAlchemy ORM
- Cryptography library
- Boto3 (AWS SDK)
- Scikit-learn (ML)
