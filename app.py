#!/usr/bin/env python3
import os

import aws_cdk as cdk

from remedy_scan_ecr_repositories.remedy_scan_ecr_repositories_stack import RemedyScanEcrRepositoriesStack

app = cdk.App()

RemedyScanEcrRepositoriesStack(
    app, 'RemedyScanEcrRepositoriesStack',
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('scan-ecr-repositories','scan-ecr-repositories')

app.synth()
