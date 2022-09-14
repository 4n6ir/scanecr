import boto3
import json

def handler(event, context):

    repo_count = 0
    img_count = 0

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

                repo_count += 1
                paginator2 = ecr.get_paginator('list_images')
                response_iterator2 = paginator2.paginate(
                    repositoryName = repository['repositoryName'],
                )

                ### Image Loop ###
                
                for page2 in response_iterator2:
                    for imageid in page2['imageIds']:

                        img_count += 1
                        ecr.start_image_scan(
                            registryId = repository['registryId'],
                            repositoryName = repository['repositoryName'],
                            imageId = {
                                'imageDigest': imageid['imageDigest'],
                                'imageTag': imageid['imageTag']
                            }
                        )

    print('Total Repositories: '+str(repo_count))
    print('Total Images: '+str(img_count))

    return {
        'statusCode': 200,
        'body': json.dumps('Assess ECR Repositories')
    }
