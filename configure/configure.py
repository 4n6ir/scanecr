import boto3
import json

def handler(event, context):

    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()

    for region in regions['Regions']:
        try:
            ecr = boto3.client('ecr', region_name = region['RegionName'])
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
            print('ENABLED: '+region['RegionName'])
        except:
            print('ERROR: '+region['RegionName'])
            pass

    return {
        'statusCode': 200,
        'body': json.dumps('Configure ECR Repositories')
    }