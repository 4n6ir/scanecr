import boto3
import json

def handler(event, context):

    ecr = boto3.client('ecr')
    
    ecr.put_registry_scanning_configuration(
        scanType = 'BASIC',
        rules = [
            {
                'scanFrequency': 'SCAN_ON_PUSH',
                'repositoryFilters': [
                    {
                        'filter': '*',
                        'filterType': 'WILDCARD'
                    }
                ]
            }
        ]
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Configure ECR Repositories')
    }