import boto3
import json

client = boto3.client('cloudformation')

stack_name = 'FeatureToggles-7e4f9743-e9c7-4f19-b99e-f868085fbe1a'
response = client.describe_stack_resource(
    StackName=stack_name,
    LogicalResourceId='LoadFeatureToggles'
)

load_function = response['StackResourceDetail']['PhysicalResourceId']

response = client.describe_stack_resource(
    StackName=stack_name,
    LogicalResourceId='UpdateFeatureToggles'
)

update_function = response['StackResourceDetail']['PhysicalResourceId']
