import boto3
import json

client = boto3.client('cloudformation')

stack_name = 'FeatureToggles-8f3ee30d-d462-4660-a219-452141ebbe30'
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


lambda_client = boto3.client('lambda')

updates = [
    {
        'action': 'SET',
        'toggle_name': 'existing',
        'dimension': 'd1',
        'value': False,
    }
]

response =lambda_client.invoke(
    FunctionName = update_function,
    InvocationType='RequestResponse',
    Payload=json.dumps(updates)
)

print response