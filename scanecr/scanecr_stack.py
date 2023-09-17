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
            cdk_nag.AwsSolutionsChecks()
        )

        Aspects.of(self).add(
            cdk_nag.HIPAASecurityChecks()    
        )

        Aspects.of(self).add(
            cdk_nag.NIST80053R5Checks()
        )

        Aspects.of(self).add(
            cdk_nag.PCIDSS321Checks()
        )

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self, suppressions = [
                {"id":"AwsSolutions-IAM4","reason":"The IAM user, role, or group uses AWS managed policies."},
                {"id":"AwsSolutions-IAM5","reason":"The IAM entity contains wildcard permissions and does not have a cdk-nag rule suppression with evidence for those permission."},
                {"id":"AwsSolutions-L1","reason":"The non-container Lambda function is not configured to use the latest runtime version."},
                {"id":"HIPAA.Security-IAMNoInlinePolicy","reason":"The IAM Group, User, or Role contains an inline policy - (Control IDs: 164.308(a)(3)(i), 164.308(a)(3)(ii)(A), 164.308(a)(3)(ii)(B), 164.308(a)(4)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(B), 164.308(a)(4)(ii)(C), 164.312(a)(1))."},
                {"id":"HIPAA.Security-IAMPolicyNoStatementsWithAdminAccess","reason":"The IAM policy grants admin access, meaning the policy allows a principal to perform all actions on all resources - (Control IDs: 164.308(a)(3)(i), 164.308(a)(3)(ii)(A), 164.308(a)(3)(ii)(B), 164.308(a)(4)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(B), 164.308(a)(4)(ii)(C), 164.312(a)(1))."},
                {"id":"HIPAA.Security-IAMPolicyNoStatementsWithFullAccess","reason":"The IAM policy grants full access, meaning the policy allows a principal to perform all actions on individual resources - (Control IDs: 164.308(a)(3)(i), 164.308(a)(3)(ii)(A), 164.308(a)(3)(ii)(B), 164.308(a)(4)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(B), 164.308(a)(4)(ii)(C), 164.312(a)(1))."},
                {"id":"HIPAA.Security-IAMUserNoPolicies","reason":"The IAM policy is attached at the user level - (Control IDs: 164.308(a)(3)(i), 164.308(a)(3)(ii)(A), 164.308(a)(3)(ii)(B), 164.308(a)(4)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(B), 164.308(a)(4)(ii)(C), 164.312(a)(1))."},
                {"id":"HIPAA.Security-LambdaConcurrency","reason":"The Lambda function is not configured with function-level concurrent execution limits - (Control ID: 164.312(b))."},
                {"id":"HIPAA.Security-LambdaDLQ","reason":"The Lambda function is not configured with a dead-letter configuration - (Control ID: 164.312(b))."},
                {"id":"HIPAA.Security-LambdaInsideVPC","reason":"The Lambda function is not VPC enabled - (Control IDs: 164.308(a)(3)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(C), 164.312(a)(1), 164.312(e)(1))."},
                {"id":"HIPAA.Security-CloudWatchLogGroupEncrypted","reason":"The CloudWatch Log Group is not encrypted with an AWS KMS key - (Control IDs: 164.312(a)(2)(iv), 164.312(e)(2)(ii))."},
                {"id":"HIPAA.Security-CloudWatchLogGroupRetentionPeriod","reason":"The CloudWatch Log Group does not have an explicit retention period configured - (Control ID: 164.312(b))."},
                {"id":"HIPAA.Security-LambdaFunctionPublicAccessProhibited","reason":"The Lambda function permission grants public access - (Control IDs: 164.308(a)(3)(i), 164.308(a)(4)(ii)(A), 164.308(a)(4)(ii)(C), 164.312(a)(1), 164.312(e)(1))."},
                {"id":"NIST.800.53.R5-IAMNoInlinePolicy","reason":"The IAM Group, User, or Role contains an inline policy - (Control IDs: AC-2i.2, AC-2(1), AC-2(6), AC-3, AC-3(3)(a), AC-3(3)(b)(1), AC-3(3)(b)(2), AC-3(3)(b)(3), AC-3(3)(b)(4), AC-3(3)(b)(5), AC-3(3)(c), AC-3(3), AC-3(4)(a), AC-3(4)(b), AC-3(4)(c), AC-3(4)(d), AC-3(4)(e), AC-3(4), AC-3(7), AC-3(8), AC-3(12)(a), AC-3(13), AC-3(15)(a), AC-3(15)(b), AC-4(28), AC-6, AC-6(3), AC-24, CM-5(1)(a), CM-6a, CM-9b, MP-2, SC-23(3))."},
                {"id":"NIST.800.53.R5-IAMPolicyNoStatementsWithAdminAccess","reason":"The IAM policy grants admin access, meaning the policy allows a principal to perform all actions on all resources - (Control IDs: AC-2i.2, AC-2(1), AC-2(6), AC-3, AC-3(3)(a), AC-3(3)(b)(1), AC-3(3)(b)(2), AC-3(3)(b)(3), AC-3(3)(b)(4), AC-3(3)(b)(5), AC-3(3)(c), AC-3(3), AC-3(4)(a), AC-3(4)(b), AC-3(4)(c), AC-3(4)(d), AC-3(4)(e), AC-3(4), AC-3(7), AC-3(8), AC-3(12)(a), AC-3(13), AC-3(15)(a), AC-3(15)(b), AC-4(28), AC-5b, AC-6, AC-6(2), AC-6(3), AC-6(10), AC-24, CM-5(1)(a), CM-6a, CM-9b, MP-2, SC-23(3), SC-25)."},
                {"id":"NIST.800.53.R5-IAMPolicyNoStatementsWithFullAccess","reason":"The IAM policy grants full access, meaning the policy allows a principal to perform all actions on individual resources - (Control IDs: AC-3, AC-5b, AC-6(2), AC-6(10), CM-5(1)(a))."},
                {"id":"NIST.800.53.R5-IAMUserNoPolicies","reason":"The IAM policy is attached at the user level - (Control IDs: AC-2i.2, AC-2(1), AC-2(6), AC-3, AC-3(3)(a), AC-3(3)(b)(1), AC-3(3)(b)(2), AC-3(3)(b)(3), AC-3(3)(b)(4), AC-3(3)(b)(5), AC-3(3)(c), AC-3(3), AC-3(4)(a), AC-3(4)(b), AC-3(4)(c), AC-3(4)(d), AC-3(4)(e), AC-3(4), AC-3(7), AC-3(8), AC-3(12)(a), AC-3(13), AC-3(15)(a), AC-3(15)(b), AC-4(28), AC-6, AC-6(3), AC-24, CM-5(1)(a), CM-6a, CM-9b, MP-2, SC-23(3), SC-25)."},
                {"id":"NIST.800.53.R5-LambdaConcurrency","reason":"The Lambda function is not configured with function-level concurrent execution limits - (Control IDs: AU-12(3), AU-14a, AU-14b, CA-7, CA-7b, PM-14a.1, PM-14b, PM-31, SC-6)."},
                {"id":"NIST.800.53.R5-LambdaDLQ","reason":"The Lambda function is not configured with a dead-letter configuration - (Control IDs: AU-12(3), AU-14a, AU-14b, CA-2(2), CA-7, CA-7b, PM-14a.1, PM-14b, PM-31, SC-36(1)(a), SI-2a)."},
                {"id":"NIST.800.53.R5-LambdaInsideVPC","reason":"The Lambda function is not VPC enabled - (Control IDs: AC-2(6), AC-3, AC-3(7), AC-4(21), AC-6, AC-17b, AC-17(1), AC-17(1), AC-17(4)(a), AC-17(9), AC-17(10), MP-2, SC-7a, SC-7b, SC-7c, SC-7(2), SC-7(3), SC-7(9)(a), SC-7(11), SC-7(12), SC-7(16), SC-7(20), SC-7(21), SC-7(24)(b), SC-25)."},
                {"id":"NIST.800.53.R5-CloudWatchLogGroupEncrypted","reason":"The CloudWatch Log Group is not encrypted with an AWS KMS key - (Control IDs: AU-9(3), CP-9d, SC-8(3), SC-8(4), SC-13a, SC-28(1), SI-19(4))."},
                {"id":"NIST.800.53.R5-CloudWatchLogGroupRetentionPeriod","reason":"The CloudWatch Log Group does not have an explicit retention period configured - (Control IDs: AC-16b, AT-4b, AU-6(3), AU-6(4), AU-6(6), AU-6(9), AU-10, AU-11(1), AU-11, AU-12(1), AU-12(2), AU-12(3), AU-14a, AU-14b, CA-7b, PM-14a.1, PM-14b, PM-21b, PM-31, SC-28(2), SI-4(17), SI-12)."},
                {"id":"NIST.800.53.R5-LambdaFunctionPublicAccessProhibited","reason":"The Lambda function permission grants public access - (Control IDs: AC-2(6), AC-3, AC-3(7), AC-4(21), AC-6, AC-17b, AC-17(1), AC-17(1), AC-17(4)(a), AC-17(9), AC-17(10), MP-2, SC-7a, SC-7b, SC-7c, SC-7(2), SC-7(3), SC-7(7), SC-7(9)(a), SC-7(11), SC-7(12), SC-7(16), SC-7(20), SC-7(21), SC-7(24)(b), SC-7(25), SC-7(26), SC-7(27), SC-7(28), SC-25)."},
                {"id":"PCI.DSS.321-IAMNoInlinePolicy","reason":"The IAM Group, User, or Role contains an inline policy - (Control IDs: 2.2, 7.1.2, 7.1.3, 7.2.1, 7.2.2)."},
                {"id":"PCI.DSS.321-IAMPolicyNoStatementsWithAdminAccess","reason":"The IAM policy grants admin access, meaning the policy allows a principal to perform all actions on all resources - (Control IDs: 2.2, 7.1.2, 7.1.3, 7.2.1, 7.2.2)."},
                {"id":"PCI.DSS.321-IAMPolicyNoStatementsWithFullAccess","reason":"The IAM policy grants full access, meaning the policy allows a principal to perform all actions on individual resources - (Control IDs: 7.1.2, 7.1.3, 7.2.1, 7.2.2)."},
                {"id":"PCI.DSS.321-IAMUserNoPolicies","reason":"The IAM policy is attached at the user level - (Control IDs: 2.2, 7.1.2, 7.1.3, 7.2.1, 7.2.2)."},
                {"id":"PCI.DSS.321-LambdaInsideVPC","reason":"The Lambda function is not VPC enabled - (Control IDs: 1.2, 1.2.1, 1.3, 1.3.1, 1.3.2, 1.3.4, 2.2.2)."},
                {"id":"PCI.DSS.321-CloudWatchLogGroupEncrypted","reason":"The CloudWatch Log Group is not encrypted with an AWS KMS key - (Control ID: 3.4)."},
                {"id":"PCI.DSS.321-CloudWatchLogGroupRetentionPeriod","reason":"The CloudWatch Log Group does not have an explicit retention period configured - (Control IDs: 3.1, 10.7)."},
                {"id":"PCI.DSS.321-LambdaFunctionPublicAccessProhibited","reason":"The Lambda function permission grants public access - (Control IDs: 1.2, 1.2.1, 1.3, 1.3.1, 1.3.2, 1.3.4, 2.2.2)."},
            ]
        )

        account = Stack.of(self).account
        region = Stack.of(self).region

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:9'
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
            runtime = _lambda.Runtime.PYTHON_3_11,
            timeout = Duration.seconds(900),
            environment = dict(
                AWS_ACCOUNT = account
            ),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )
       
        assesslogs = _logs.LogGroup(
            self, 'assesslogs',
            log_group_name = '/aws/lambda/'+assess.function_name,
            retention = _logs.RetentionDays.ONE_MONTH,
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
            runtime = _lambda.Runtime.PYTHON_3_11,
            timeout = Duration.seconds(900),
            environment = dict(
                AWS_ACCOUNT = account
            ),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )
       
        configurelogs = _logs.LogGroup(
            self, 'configurelogs',
            log_group_name = '/aws/lambda/'+configure.function_name,
            retention = _logs.RetentionDays.ONE_MONTH,
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
            runtime = _lambda.Runtime.PYTHON_3_11,
            timeout = Duration.seconds(900),
            environment = dict(
                AWS_ACCOUNT = account,
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
            retention = _logs.RetentionDays.ONE_MONTH,
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
