#!/usr/bin/env python3
import os

import aws_cdk as cdk

from scanecr.scanecr_stack import ScanecrStack

app = cdk.App()

ScanecrStack(
    app, 'ScanecrStack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = os.getenv('CDK_DEFAULT_REGION')
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','ALL')
cdk.Tags.of(app).add('GitHub','https://github.com/4n6ir/scanecr.git')

app.synth()
