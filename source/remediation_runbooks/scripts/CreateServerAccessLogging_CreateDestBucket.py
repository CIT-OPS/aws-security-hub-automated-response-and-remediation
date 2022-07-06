import logging
import boto3
from botocore.exceptions import ClientError

def create_bucket(s3, bucket_name, region):
  """Create an S3 bucket in a specified region

  If a region is not specified, the bucket is created in the S3 default
  region (us-east-1).

  :param bucket_name: Bucket to create
  :param region: String region to create bucket in, e.g., 'us-west-2'
  :return: True if bucket created, else False
  """

  # Create bucket
  try:
    if region != 'us-east-1':
        bucket = s3.create_bucket(
          Bucket=bucket_name,
          ACL='private',
          CreateBucketConfiguration={ 
            'LocationConstraint': region
          },
          ObjectLockEnabledForBucket=False,
          ObjectOwnership='BucketOwnerEnforced'
        ) 
        logging.info(bucket)
    else:
        bucket = s3.create_bucket(
          Bucket=bucket_name,
          ACL='private',
          ObjectLockEnabledForBucket=False,
          ObjectOwnership='BucketOwnerEnforced'
        ) 
        logging.info(bucket)
    
    s3_client = boto3.client("s3")
    response = s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
            ]
        },
    )   
    response = s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'Status': 'Enabled'
        },
    )
    
  except ClientError as e:
    logging.error(e)
    return False
  return True


def lambda_handler(event, context):
  s3 = boto3.resource("s3")
  iam = boto3.resource('iam')
  resourceId = event["Resource"]['Id']
  region = event["Resource"]["Region"]
  bucketArray = resourceId.split(":")
  AwsAccountId = event['Finding']['AwsAccountId']
  bucket = 'cnxc-s3-server-access-logging-' + AwsAccountId + '-' + region
  

  # Create Bucket
  if create_bucket(s3, bucket, region):
    return bucket
  else:
    return 'failed'