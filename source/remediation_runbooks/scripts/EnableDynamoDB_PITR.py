#!/usr/bin/python
###############################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.    #
#                                                                             #
#  Licensed under the Apache License Version 2.0 (the "License"). You may not #
#  use this file except in compliance with the License. A copy of the License #
#  is located at                                                              #
#                                                                             #
#      http://www.apache.org/licenses/LICENSE-2.0/                                        #
#                                                                             #
#  or in the "license" file accompanying this file. This file is distributed  #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express #
#  or implied. See the License for the specific language governing permis-    #
#  sions and limitations under the License.                                   #
###############################################################################

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

def connect_to_dynamodb(region, boto_config):
    return boto3.client('dynamodb', region_name=region, config=boto_config)

def lambda_handler(event, context):
    """
    remediates DynamoDB.2 by enabling Point In Time Recovery
    On success returns a string map
    On failure returns NoneType
    """
    boto_config = Config(
        retries ={
          'mode': 'standard'
        }
    )
    
    splitEnv = event['tableArn'].split(":")
    splitTable = splitEnv[5].split("/")
    
    if (splitTable[0] != 'table' and splitTable[0] != 'global-table') or splitEnv[0] != 'arn' or splitEnv[1] != 'aws' or splitEnv[2] != 'dynamodb':
        print("Invalid DynamoDB arn of ",event['tableArn'])
        return {
            "response": {
                "message": f'Invalid DynamoDB arn {event["tableArn"]}',
                "status": "Failed"
            }
        }
        
    tablename = splitTable[1]
    region = splitEnv[3]
    account = splitEnv[4]
    #print(account,region,tablename)

    ddb_client = connect_to_dynamodb(region, boto_config)
    
    try:
        ddb_client.update_continuous_backups(
            TableName=tablename,
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            }
        )
        return {
            "response": {
                "message": f'Enabled PITR on {tablename}',
                "status": "Success"
            }
        }
    except Exception as e:
        exit(f'Error setting PITR: {str(e)}')
