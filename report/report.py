import boto3
import json
import os

def handler(event, context):

    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()

    ### Region Loop ###

    for region in regions['Regions']:

        ecr = boto3.client('ecr', region_name = region['RegionName'])
        paginator = ecr.get_paginator('describe_repositories')
        response_iterator = paginator.paginate()

        ### Repository Loop ###

        for page in response_iterator:
            for repository in page['repositories']:

                paginator2 = ecr.get_paginator('list_images')
                response_iterator2 = paginator2.paginate(
                    repositoryName = repository['repositoryName'],
                )

                ### Image Loop ###

                for page2 in response_iterator2:
                    for imageid in page2['imageIds']:

                        findings = ecr.describe_image_scan_findings(
                            registryId = repository['registryId'],
                            repositoryName = repository['repositoryName'],
                            imageId = {
                                'imageDigest': imageid['imageDigest'],
                                'imageTag': imageid['imageTag']
                            }
                        )

                        if len(findings['imageScanFindings']['findingSeverityCounts']) > 0:
                            output = {}
                            output['registryId'] = findings['registryId']
                            output['repositoryName'] = findings['repositoryName']
                            output['imageDigest'] = findings['imageId']['imageDigest']
                            output['imageTag'] = findings['imageId']['imageTag']
                            output['imageScanStatus'] = findings['imageScanStatus']['status']
                            output['imageScanFindings'] = findings['imageScanFindings']['findingSeverityCounts']
                            
                            client = boto3.client('sns')
                            response = client.publish(
                                TopicArn = os.environ['SNS_TOPIC'],
                                Subject = 'ECR Vulnerabilities',
                                Message = str(output)
                            )

    return {
        'statusCode': 200,
        'body': json.dumps('Report ECR Repositories')
    }