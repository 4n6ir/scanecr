#!/usr/bin/env python3
import os

import aws_cdk as cdk

from scanecr.scanecr_stack import ScanecrStack

app = cdk.App()

ScanecrStack(
    app, 'ScanecrStackUSE1',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

ScanecrStack(
    app, 'ScanecrStackUSE2',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-2'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

ScanecrStack(
    app, 'ScanecrStackUSW2',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-west-2'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','ALL')
cdk.Tags.of(app).add('GitHub','https://github.com/4n6ir/scanecr.git')

app.synth()
