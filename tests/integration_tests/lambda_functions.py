import boto3
import json
import pytest
import sys
import test_constants

client = boto3.client('cloudformation')

stack_name = 'FeatureToggles-2ebc91d6-05a3-432f-9c6d-3663236d7a47'
print (stack_name)
response = client.describe_stack_resource(
    StackName=test_constants.STACK_NAME,
    LogicalResourceId='LoadFeatureToggles'
)

load_function = response['StackResourceDetail']['PhysicalResourceId']

response = client.describe_stack_resource(
    StackName=test_constants.STACK_NAME,
    LogicalResourceId='UpdateFeatureToggles'
)

update_function = response['StackResourceDetail']['PhysicalResourceId']
