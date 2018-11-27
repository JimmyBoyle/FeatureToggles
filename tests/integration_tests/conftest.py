import boto3
import json
import pytest
import sys

def pytest_addoption(parser):
    parser.addoption('--stack-name', action='store', dest='stringvalue')

#stack_name = ''

client = boto3.client('cloudformation')

@pytest.fixture()
def load_function(request):
    response = client.describe_stack_resource(
        StackName=request.config.getoption('stringvalue'),
        LogicalResourceId='LoadFeatureToggles'
    )

    load_function = response['StackResourceDetail']['PhysicalResourceId']
    return load_function

@pytest.fixture
def update_function(request):
    response = client.describe_stack_resource(
        StackName=request.config.getoption('stringvalue'),
        LogicalResourceId='UpdateFeatureToggles'
    )

    update_function = response['StackResourceDetail']['PhysicalResourceId']
    return update_function

'''
stack_name = 'FeatureToggles-2ebc91d6-05a3-432f-9c6d-3663236d7a47'
#print stack_name
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
'''