import boto3
from botocore.exceptions import ClientError

credentials = [
    {
        "name": "Set 1 (deduplication-main)",
        "key": "***REMOVED***",
        "secret": "***REMOVED***",
        "region": "us-east-1",
        "bucket": "deduplication-main"
    },
    {
        "name": "Set 2 (bhanumainproject01)",
        "key": "***REMOVED***",
        "secret": "***REMOVED***",
        "region": "us-east-1",
        "bucket": "bhanumainproject01"
    }
]

for cred in credentials:
    print(f"\nTesting {cred['name']}...")
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=cred['key'],
            aws_secret_access_key=cred['secret'],
            region_name=cred['region']
        )
        s3.list_buckets()
        print(f"  [OK] Valid credentials for {cred['name']}")
        
        try:
            s3.head_bucket(Bucket=cred['bucket'])
            print(f"  [OK] Bucket access successful for {cred['bucket']}")
        except ClientError as e:
            print(f"  [X] Bucket access failed: {e}")
            
    except ClientError as e:
        print(f"  [X] Credentials invalid: {e}")
    except Exception as e:
        print(f"  [X] Error: {e}")
