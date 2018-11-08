import boto3
import json

client = boto3.client('cloudformation')

stack_name = 'FeatureToggles-b4c42e9d-1105-46e8-857d-79d92ff57d6b'
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

updates = {
    "operator_id": "janedeveloper",
    "updates": [
        {
            "action": "SET",
            "toggle_name": "feature1",
            "dimension": "dimension1",
            "value": True
        },
        {
            "action": "SET",
            "toggle_name": "feature1",
            "dimension": "dimension2",
            "value": False
        },
        {
            "action": "SET",
            "toggle_name": "feature2",
            "dimension": "dimension3",
            "value": True
        }
    ]
}

response =lambda_client.invoke(
    FunctionName = update_function,
    InvocationType='RequestResponse',
    Payload=json.dumps(updates)
)

print response