import boto3
import dateutil.tz
import json
import os
from datetime import datetime, timezone

def handler(event, context):

    ecr = boto3.client('ecr')
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

                    if findings['imageScanStatus']['status'] != 'FAILED':

                        if len(findings['imageScanFindings']['findingSeverityCounts']) > 0:

                            output = {}
                            output['registryId'] = findings['registryId']
                            output['repositoryName'] = findings['repositoryName']
                            output['imageDigest'] = findings['imageId']['imageDigest']
                            output['imageTag'] = findings['imageId']['imageTag']
                            output['imageScanStatus'] = findings['imageScanStatus']['status']
                            output['imageScanFindings'] = findings['imageScanFindings']['findingSeverityCounts']

                            right_now = datetime.now(dateutil.tz.tzlocal())
                            diff = right_now - findings['imageScanFindings']['vulnerabilitySourceUpdatedAt']

                            if diff.days < 2:

                                account = os.environ['ACCOUNT']
                                region = os.environ['REGION']

                                now = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

                                securityhub_client = boto3.client('securityhub')

                                securityhub_response = securityhub_client.batch_import_findings(
                                    Findings = [
                                        {
                                            "SchemaVersion": "2018-10-08",
                                            "Id": region+"/"+account+"/vuln",
                                            "ProductArn": "arn:aws:securityhub:"+region+":"+account+":product/"+account+"/default", 
                                            "GeneratorId": "ecr-vuln",
                                            "AwsAccountId": account,
                                            "CreatedAt": now,
                                            "UpdatedAt": now,
                                            "Title": "Vuln",
                                            "Description": str(output),
                                            "Resources": [
                                                {
                                                    "Type": "AwsLambda",
                                                    "Id": "arn:aws:lambda:"+region+":"+account+":function:report"
                                                }
                                            ],
                                            "FindingProviderFields": {
                                                "Confidence": 100,
                                                "Severity": {
                                                    "Label": "MEDIUM"
                                                },
                                                "Types": [
                                                    "security/ecr/vuln"
                                                ]
                                            }
                                        }
                                    ]
                                )

                                print(securityhub_response)

    return {
        'statusCode': 200,
        'body': json.dumps('Report ECR Repositories')
    }