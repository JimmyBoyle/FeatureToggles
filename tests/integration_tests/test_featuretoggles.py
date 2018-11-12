import boto3
import json
import conftest

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

expected = {
    'feature_toggles':{
        'feature1':{
            'dimension1':'True',
            'dimension2':'False'
        },
        'feature2':{
            'dimension3':'True'
        }
    }
}

response =lambda_client.invoke(
    FunctionName = conftest.update_function,
    InvocationType='RequestResponse',
    Payload=json.dumps(updates)
)

print response

res =lambda_client.invoke(
    FunctionName = conftest.load_function,
    InvocationType='RequestResponse'
)
print res
res_json = json.loads(res['Payload'].read().decode("utf-8"))
print res_json == expected
for feature in res_json['feature_toggles']:
    for dim in res_json['feature_toggles'][feature]:
        print feature, dim, type(res_json['feature_toggles'][feature][dim])