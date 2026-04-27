from config import Config
print(f"USE_S3: {Config.USE_S3}")
print(f"AWS_ACCESS_KEY: '{Config.AWS_ACCESS_KEY}'")
print(f"AWS_SECRET_KEY: '{Config.AWS_SECRET_KEY[:4]}...{Config.AWS_SECRET_KEY[-4:]}'" if Config.AWS_SECRET_KEY else "AWS_SECRET_KEY: None")
print(f"S3_BUCKET_NAME: '{Config.S3_BUCKET_NAME}'")
print(f"AWS_REGION: '{Config.AWS_REGION}'")
