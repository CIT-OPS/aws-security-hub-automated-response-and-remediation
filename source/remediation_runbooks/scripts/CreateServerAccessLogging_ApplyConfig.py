import logging
import copy
import json
import time
from pprint import pprint
import botocore
import boto3

def enableAccessLogging(s3, bucketName, storageBucket, targetPrefix):
  return s3.put_bucket_logging(
      Bucket=bucketName,
      BucketLoggingStatus={
          'LoggingEnabled': {
              'TargetBucket': storageBucket,
              'TargetPrefix': targetPrefix
          }
      }
  )

def lambda_handler(event, context):
  s3 = boto3.resource('s3')
  s3_client = boto3.client('s3')

  resourceId = event['Resource']['Id']
  region = event['Resource']['Region']
  bucketArray = resourceId.split(':')
  fixmeBucket = bucketArray[-1]
  AwsAccountId = event['Finding']['AwsAccountId']
  destBucket = 'cnxc-s3-server-access-logging-' + AwsAccountId + '-' + region
  targetPrefix = fixmeBucket+'/'
  
  if fixmeBucket == destBucket:
      return {
        'output':
          {
            'message': 'This bucket is exempt from logging as it would create a circular log effect',
            'resourceBucketName': fixmeBucket,
            'LoggingBucketName': destBucket,
            'LoggingPrefix': targetPrefix,
            'status': 'SUPPRESSED'
          }
      }

  result = enableAccessLogging(s3_client, fixmeBucket, destBucket, targetPrefix)
  
  return {
    'output':
      {
        'message': 'Server Access Logging Successfully Set.',
        'resourceBucketName': fixmeBucket,
        'LoggingBucketName': destBucket,
        'LoggingPrefix': targetPrefix,
        'status': 'RESOLVED'
      }
  }