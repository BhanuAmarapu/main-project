from config import Config
import os
print(f"USE_S3 type: {type(Config.USE_S3)}, value: {Config.USE_S3}")
print(f"AWS_ACCESS_KEY length: {len(Config.AWS_ACCESS_KEY)}")
print(f"AWS_ACCESS_KEY value: [{Config.AWS_ACCESS_KEY}]")
print(f"S3_BUCKET_NAME value: [{Config.S3_BUCKET_NAME}]")
