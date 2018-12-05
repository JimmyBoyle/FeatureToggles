"""Core feature toggle app logic."""

import json
import logging
import ast

import boto3
import botocore
from jsonschema import ValidationError

import config

LOGGER = logging.getLogger(__name__)

client = boto3.client('ssm')
paginator = client.get_paginator('get_parameters_by_path')
#PREFIX = '/FeatureToggles'
PREFIX = '/' + config.PREFIX + '/'


def load():
    """Load feature toggles.

    Load all feature toggle values from SSM
    """

    response_iterator = paginator.paginate(
        Path=PREFIX,
        Recursive=True
    )
    response = {}

    for iters in response_iterator:
        for param in iters['Parameters']:
            toggle, dimension = param['Name'].split('/')[2:]
            if toggle not in response:
                response[toggle] = {}
            response[toggle][dimension] = ast.literal_eval(param['Value'])
    return response


def update(updates):
    """Update feature toggles.

    Apply the given updates to the stored feature toggles.
    """
    cur_params = load()

    params_to_clear = []
    params_to_update = []
    for update in updates:
        action = update['action']
        if action != 'CLEAR_ALL':
            if 'dimension' not in update:
                raise ValidationError('update must specify a "dimension" key')
        if action == 'SET':
            if 'value' not in update:
                raise ValidationError('SET update must specify a "value" key')
            params_to_update.append(update)
        elif action == 'CLEAR':
            if update['toggle_name'] in cur_params:
                if update['dimension'] in cur_params[update['toggle_name']]:
                    params_to_clear.append(
                        PREFIX + update['toggle_name'] + '/' + update['dimension'])
            else:
                raise ValidationError('{} toggle does not exist'.format(update['toggle_name']))
        elif action == 'CLEAR_ALL':
            if update['toggle_name'] in cur_params:
                for dimension in cur_params[update['toggle_name']]:
                    param_name = PREFIX + \
                        update['toggle_name'] + '/' + dimension
                    params_to_clear.append(param_name)
            else:
                raise ValidationError('{} toggle does not exist'.format(update['toggle_name']))
        else:
            raise Exception('Unsupported action: {}'.format(action))
    _update_params(params_to_update)
    _clear_params(params_to_clear)


def _update_params(params):
    for param in params:
        try:
            client.put_parameter(
                Name=PREFIX + param['toggle_name'] + '/' + param['dimension'],
                Value=str(param['value']),
                Type='String',
                Overwrite=True
            )
        except botocore.exceptions.ClientError as err:
            raise err
    return


def _clear_params(param_names):
    if len(param_names) == 0:
        return
    # max size of items to delete for ssm api call is 10 so we split into size 10 chunks
    n = 10
    for param_chunk in [param_names[i:i + n] for i in range(0, len(param_names), n)]:
        try:
            response = client.delete_parameters(
                Names=param_chunk
            )
        except botocore.exceptions.ClientError as err:
            raise err

    return
