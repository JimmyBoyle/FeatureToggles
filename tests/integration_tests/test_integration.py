import boto3
import json
import lambda_functions
import sys

lambda_client = boto3.client('lambda')


def test_basic_load():
    updates = {
        "operator_id": "tester",
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
        'feature_toggles': {
            'feature1': {
                'dimension1': True,
                'dimension2': False
            },
            'feature2': {
                'dimension3': True
            }
        }
    }
    _update_toggles(updates)
    assert _load_toggles() == expected
    _clear_toggles(expected)

def test_clear_one():
    before = {
        "operator_id": "tester",
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
    _update_toggles(before)
    updates = {
        "operator_id": "tester",
        "updates": [
            {
                "action": "CLEAR",
                "toggle_name": "feature1",
                "dimension": "dimension1"
            }
        ]
    }

    expected = {
        'feature_toggles': {
            'feature1': {
                'dimension2': False
            },
            'feature2': {
                'dimension3': True
            }
        }
    }
    _update_toggles(updates)
    assert _load_toggles() == expected
    _clear_toggles(expected)

def test_clear_all():
    before = {
        "operator_id": "tester",
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
    _update_toggles(before)
    updates = {
        "operator_id": "tester",
        "updates": [
            {
                "action": "CLEAR_ALL",
                "toggle_name": "feature1"
            }
        ]
    }

    expected = {
        'feature_toggles': {
            'feature2': {
                'dimension3': True
            }
        }
    }
    _update_toggles(updates)
    assert _load_toggles() == expected
    _clear_toggles(expected)
    
def test_bad_action():
    updates = {
        "operator_id": "tester",
        "updates": [
            {
                "action": "SETS",
                "toggle_name": "feature1",
                "dimension": "dimension1",
                "value": True
            }
        ]
    }

    result = _update_toggles(updates)
    assert 'errorMessage' in result
    assert 'ValidationError' == result['errorType']

def test_missing_dimension():
    updates = {
        "operator_id": "tester",
        "updates":  [
            {
                'action': 'SET',
                'toggle_name': 't1',
                'value': True,
            }
        ]
    }
    
    result = _update_toggles(updates)
    assert 'errorMessage' in result
    assert 'ValidationError' == result['errorType'] 

def test_missing_action():
    updates = {
        "operator_id": "tester",
        "updates":  [
            {
                'toggle_name': 't1',
                'value': True,
            }
        ]
    }
    
    result = _update_toggles(updates)
    assert 'errorMessage' in result
    assert 'ValidationError' == result['errorType'] 

def _load_toggles():
    res = lambda_client.invoke(
        FunctionName=lambda_functions.load_function,
        InvocationType='RequestResponse'
    )
    return json.loads(res['Payload'].read().decode("utf-8"))


def _update_toggles(updates):
    print(lambda_functions.update_function)
    res = lambda_client.invoke(
        FunctionName=lambda_functions.update_function,
        InvocationType='RequestResponse',
        Payload=json.dumps(updates)
    )
    return json.loads(res['Payload'].read().decode("utf-8"))


def _clear_toggles(current_toggles):
    updates = {
        "operator_id": "tester",
        "updates": []
    }
    for toggle_name in current_toggles['feature_toggles']:
        updates['updates'].append(
            {
                "action": "CLEAR_ALL",
                "toggle_name": toggle_name
            }
        )

    _update_toggles(updates)
    assert _load_toggles() == {'feature_toggles': {}}
