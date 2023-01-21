import cdk_nag

from aws_cdk import (
    Aspects,
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

        Aspects.of(self).add(
            cdk_nag.AwsSolutionsChecks(
                log_ignores = True,
                verbose = True
            )
        )

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self, suppressions = [
                {'id': 'AwsSolutions-IAM4','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-IAM5','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-L1','reason': 'GitHub Issue'}
            ]
        )

        account = Stack.of(self).account
        region = Stack.of(self).region

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:3'
        )

### ERROR ###

        error = _lambda.Function.from_function_arn(
            self, 'error',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-error'
        )

        timeout = _lambda.Function.from_function_arn(
            self, 'timeout',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-timeout'
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
                    'securityhub:BatchImportFindings'
                ],
                resources = [
                    'arn:aws:securityhub:'+region+':'+account+':product/'+account+'/default'
                ]
            )
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

        assesstimesub = _logs.SubscriptionFilter(
            self, 'assesstimesub',
            log_group = assesslogs,
            destination = _destinations.LambdaDestination(timeout),
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

        assessevent.add_target(
            _targets.LambdaFunction(
                assess
            )
        )

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

        configuretimesub = _logs.SubscriptionFilter(
            self, 'configuretimesub',
            log_group = configurelogs,
            destination = _destinations.LambdaDestination(timeout),
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
            function_name = 'report',
            handler = 'report.handler',
            code = _lambda.Code.from_asset('report'),
            architecture = _lambda.Architecture.ARM_64,
            runtime = _lambda.Runtime.PYTHON_3_9,
            timeout = Duration.seconds(900),
            environment = dict(
                ACCOUNT = account,
                REGION = region
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

        reportevent.add_target(
            _targets.LambdaFunction(
                report
            )
        )
