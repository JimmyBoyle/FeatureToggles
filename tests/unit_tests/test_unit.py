import core
import handlers
import pytest
import os
import botocore

from pytest_mock import mocker
from jsonschema import ValidationError


PREFIX = '/'+os.environ['PREFIX'] +  '/'


def test_handler_load_with_item(mocker):
    toggles_data = {
        't1': {
            'd1': True,
            'd2': False,
        },
        't2': {
            'd1': True,
        },
        't3': {
            'd1': False,
        },
    }
    _mock_toggles(mocker, toggles_data)
    expected = {'feature_toggles': toggles_data}
    assert handlers.load_feature_toggles(None,None) == expected

def test_load_no_item(mocker):
    mocker.patch.object(core.paginator, 'paginate')
    core.paginator.paginate.return_value = [{'Parameters': []}]
    assert core.load() == {}


def test_load_with_item(mocker):
    toggles_data = {
        't1': {
            'd1': True,
            'd2': False,
        },
        't2': {
            'd1': True,
        },
        't3': {
            'd1': False,
        },
    }
    _mock_toggles(mocker, toggles_data)
    assert core.load() == toggles_data


def test_update_invalid_action(mocker):
    mocker.patch.object(core.client, 'put_parameter')
    before_update = {}
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'NOPE',
            'toggle_name': 'existing',
            'dimension': 'd1',
            'value': False,
        }
    ]

    with pytest.raises(Exception):
        core.update(updates)
    core.client.put_parameter.assert_not_called()


def test_update_set_missing_dimension(mocker):
    mocker.patch.object(core.client, 'put_parameter')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 't1',
            'value': True,
        }
    ]
    with pytest.raises(ValidationError):
        core.update(updates)
    core.client.put_parameter.assert_not_called()


def test_update_set_missing_value(mocker):
    mocker.patch.object(core.client, 'put_parameter')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 't1',
            'dimension': 'd2',
        }
    ]
    with pytest.raises(ValidationError):
        core.update(updates)
    core.client.put_parameter.assert_not_called()


def test_update_set_happycase(mocker):
    mocker.patch.object(core, '_update_params')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 'existing',
            'dimension': 'd1',
            'value': False,
        }
    ]

    core.update(updates)
    core._update_params.assert_called_with(updates)


def test_update_set_new_toggle(mocker):
    mocker.patch.object(core, '_update_params')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 'new',
            'dimension': 'd1',
            'value': False,
        }
    ]

    core.update(updates)
    core._update_params.assert_called_with(updates)


def test_update_set_new_dimension(mocker):
    mocker.patch.object(core, '_update_params')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 'existing',
            'dimension': 'd2',
            'value': True,
        }
    ]

    core.update(updates)
    core._update_params.assert_called_with(updates)


def test_update_clear_happycase(mocker):
    mocker.patch.object(core, '_clear_params')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'CLEAR',
            'toggle_name': 'existing',
            'dimension': 'd1',
        }
    ]

    core.update(updates)
    core._clear_params.assert_called_with(
        _convert_clears(before_update, updates))


def test_update_clear_all_toggle_no_exist(mocker):
    mocker.patch.object(core, '_clear_params')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'CLEAR_ALL',
            'toggle_name': 'notthere',
        }
    ]
    with pytest.raises(ValidationError):
        core.update(updates)
    core._clear_params.assert_not_called()


def test_update_put_parameter_exception(mocker):
    mocker.patch.object(core.client, 'put_parameter')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)
    err_response = {
        'Error': {'Code': 'Client Error'}
    }
    _mock_put_parameter_error(err_response)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 'existing',
            'dimension': 'd1',
            'value': False,
        }
    ]
    with pytest.raises(botocore.exceptions.ClientError):
        core.update(updates)

def test_update_delete_parameters_exception(mocker):
    mocker.patch.object(core.client, 'delete_parameters')
    before_update = {
        'existing': {
            'd1': True,
        },
    }
    _mock_toggles(mocker, before_update)
    err_response = {
        'Error': {'Code': 'Client Error'}
    }
    _mock_delete_parameters_error(err_response)

    updates = [
        {
            'action': 'CLEAR',
            'toggle_name': 'existing',
            'dimension': 'd1'
        }
    ]
    with pytest.raises(botocore.exceptions.ClientError):
        core.update(updates)

def test_update_multiple_updates(mocker):
    mocker.patch.object(core, '_update_params')
    mocker.patch.object(core, '_clear_params')
    before_update = {
        't1': {
            'd1': True,
            'd2': False,
        },
        't2': {
            'd1': False,
        },
    }
    _mock_toggles(mocker, before_update)

    updates = [
        {
            'action': 'SET',
            'toggle_name': 't1',
            'dimension': 'd1',
            'value': False,
        },
        {
            'action': 'CLEAR',
            'toggle_name': 't1',
            'dimension': 'd2',
        },
        {
            'action': 'SET',
            'toggle_name': 't3',
            'dimension': 'd3',
            'value': True,
        },
        {
            'action': 'CLEAR_ALL',
            'toggle_name': 't2',
        },
    ]
    core.update(updates)

    clear_calls = [
        PREFIX + 't1/d2',
        PREFIX + 't2/d1' 
    ]
    set_calls = [
        {
            'action': 'SET',
            'toggle_name': 't1',
            'dimension': 'd1',
            'value': False,
        },
        {
            'action': 'SET',
            'toggle_name': 't3',
            'dimension': 'd3',
            'value': True,
        }
    ]

    core._clear_params.assert_called_with(clear_calls)

    core._update_params.assert_called_with(set_calls)



def _convert_clears(cur_params, updates):
    clears = []
    for update in updates:
        if update['action'] == 'CLEAR':
            if update['toggle_name'] in cur_params:
                if update['dimension'] in cur_params[update['toggle_name']]:
                    clears.append(
                        PREFIX + update['toggle_name'] + '/' + update['dimension'])
        elif action == 'CLEAR_ALL':
            if update['toggle_name'] in cur_params:
                for dimension in cur_params[update['toggle_name']]:
                    param_name = PREFIX + \
                        update['toggle_name'] + '/' + dimension
                    clears.append(param_name)

    return clears

def _mock_toggles(mocker, toggles):
    mocker.patch.object(core.paginator, 'paginate')
    keys = list(toggles.keys())
    pages = [keys[:1], keys[1:]]
    return_val = []
    for page in pages:
        val = {'Parameters': []}
        for toggle in page:
            for dimension in toggles[toggle]:
                val['Parameters'].append({
                    'Name': PREFIX + toggle + '/' + dimension,
                    'Value': str(toggles[toggle][dimension])
                })
        return_val.append(val)
    core.paginator.paginate.return_value = return_val
    return return_val


def _mock_put_parameter_error(err_response):
    error = botocore.exceptions.ClientError(err_response, 'PutParameter')
    core.client.put_parameter.side_effect = error

def _mock_delete_parameters_error(err_response):
    error = botocore.exceptions.ClientError(err_response, 'DeleteParameters')
    core.client.delete_parameters.side_effect = error
