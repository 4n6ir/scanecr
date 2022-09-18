import boto3
import sys

from aws_cdk import (
    CustomResource,
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_logs_destinations as _destinations,
    aws_sns as _sns,
    aws_sns_subscriptions as _subs,
    custom_resources as _custom
)

from constructs import Construct

class ScanecrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        region = Stack.of(self).region

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:1'
        )

        try:
            client = boto3.client('account')
            operations = client.get_alternate_contact(
                AlternateContactType='OPERATIONS'
            )
            security = client.get_alternate_contact(
                AlternateContactType='SECURITY'
            )
        except:
            print('Missing IAM Permission --> account:GetAlternateContact')
            sys.exit(1)
            pass

        operationstopic = _sns.Topic(
            self, 'operationstopic'
        )

        operationstopic.add_subscription(
            _subs.EmailSubscription(operations['AlternateContact']['EmailAddress'])
        )

        securitytopic = _sns.Topic(
            self, 'securitytopic'
        )

        securitytopic.add_subscription(
            _subs.EmailSubscription(security['AlternateContact']['EmailAddress'])
        )

### IAM ###

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'ec2:DescribeRegions',
                    'ecr:DescribeImageScanFindings',
                    'ecr:DescribeRepositories',
                    'ecr:ListImages',
                    'ecr:PutRegistryScanningConfiguration',
                    'ecr:StartImageScan'
                ],
                resources = ['*']
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'sns:Publish'
                ],
                resources = [
                    operationstopic.topic_arn,
                    securitytopic.topic_arn
                ]
            )
        )

### ERROR ###

        error = _lambda.Function(
            self, 'error',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('error'),
            handler = 'error.handler',
            role = role,
            environment = dict(
                SNS_TOPIC = operationstopic.topic_arn
            ),
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(7),
            memory_size = 128
        )

        errormonitor = _logs.LogGroup(
            self, 'errormonitor',
            log_group_name = '/aws/lambda/'+error.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

### ASSESS ###

        assess = _lambda.Function(
            self, 'assess',
            handler = 'assess.handler',
            code = _lambda.Code.from_asset('assess'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(900),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )
       
        assesslogs = _logs.LogGroup(
            self, 'assesslogs',
            log_group_name = '/aws/lambda/'+assess.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        assesssub = _logs.SubscriptionFilter(
            self, 'assesssub',
            log_group = assesslogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        assesstime= _logs.SubscriptionFilter(
            self, 'assesstime',
            log_group = assesslogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )

        assessevent = _events.Rule(
            self, 'assessevent',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '9',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        assessevent.add_target(_targets.LambdaFunction(assess))

### CONFIGURE ###

        configure = _lambda.Function(
            self, 'configure',
            handler = 'configure.handler',
            code = _lambda.Code.from_asset('configure'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(900),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )
       
        configurelogs = _logs.LogGroup(
            self, 'configurelogs',
            log_group_name = '/aws/lambda/'+configure.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        configuresub = _logs.SubscriptionFilter(
            self, 'configuresub',
            log_group = configurelogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        configuretime= _logs.SubscriptionFilter(
            self, 'configuretime',
            log_group = configurelogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )

        provider = _custom.Provider(
            self, 'provider',
            on_event_handler = configure
        )

        resource = CustomResource(
            self, 'resource',
            service_token = provider.service_token
        )

### REPORT ###

        report = _lambda.Function(
            self, 'report',
            handler = 'report.handler',
            code = _lambda.Code.from_asset('report'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(900),
            environment = dict(
                SNS_TOPIC = securitytopic.topic_arn
            ),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )

        reportlogs = _logs.LogGroup(
            self, 'reportlogs',
            log_group_name = '/aws/lambda/'+report.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        reportsub = _logs.SubscriptionFilter(
            self, 'reportsub',
            log_group = reportlogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )

        reporttime= _logs.SubscriptionFilter(
            self, 'reporttime',
            log_group = reportlogs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )

        reportevent = _events.Rule(
            self, 'reportevent',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '11',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        reportevent.add_target(_targets.LambdaFunction(report))
