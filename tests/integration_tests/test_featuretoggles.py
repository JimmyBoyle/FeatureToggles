import boto3
import json

client = boto3.client('cloudformation')

stack_name = 'FeatureToggles-d9486166-153b-4edd-86cc-3614e9d2a5d6'

response = client.describe_stack_resource(
    StackName = stack_name,
    LogicalResourceId = 'LoadFeatureToggles'
)

load_function = response['StackResourceDetail']['PhysicalResourceId']

response = client.describe_stack_resource(
    StackName = stack_name,
    LogicalResourceId = 'UpdateFeatureToggles'
)

update_function = response['StackResourceDetail']['PhysicalResourceId']


print load_function
print update_function

lambda_client = boto3.client('lambda')


response =lambda_client.invoke(
    FunctionName = load_function
)

print response