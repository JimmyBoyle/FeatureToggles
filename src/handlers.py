"""Lambda function entrypoint handlers."""

import logging
import os
import config
import core
import schema

# set log level based on lambda config
logging.basicConfig(level=config.LOG_LEVEL)

LOGGER = logging.getLogger(__name__)

def runs_on_aws_lambda():
    """
        Returns True if this function is executed on AWS Lambda service.
    """
    return 'AWS_SAM_LOCAL' not in os.environ and 'LAMBDA_TASK_ROOT' in os.environ


# Patch all supported libraries for X-Ray - More info: https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-patching.html
if runs_on_aws_lambda():    
    #from aws_xray_sdk.core import patch_all
    #patch_all()
    continue

def load_feature_toggles(request, context):
    """Load feature toggles.

    Load all feature toggle values from the database.
    """

    LOGGER.info('Load feature toggles request')
    feature_toggles = core.load()
    response = {'feature_toggles': feature_toggles}
    LOGGER.debug('Load feature toggles response: %s', response)
    return response


def update_feature_toggles(request, context):
    """Update feature toggles.

    Update feature toggle values according to the request.
    """

    LOGGER.info('Update feature toggles request=%s', request)
    schema.validate_update_feature_toggles_request(request)

    # TODO: metrics for operator_id

    core.update(request['updates'])
