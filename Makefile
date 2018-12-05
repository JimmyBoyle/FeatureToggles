SHELL := /bin/sh
PY_VERSION := 3.6

export PYTHONUNBUFFERED := 1

BUILD_DIR := dist
TEMPLATE_DIR := sam

# Required environment variables (user must override)

# S3 bucket used for packaging SAM templates
PACKAGE_BUCKET ?= cfn-temps
PACKAGE_PREFIX ?= FeatureToggles

# user can optionally override the following by setting environment variables with the same names before running make


# Stack name used when deploying the app for manual testing
APP_STACK_NAME ?= jimbo-toggles-1
# Default AWS CLI region
AWS_DEFAULT_REGION ?= us-west-2

PYTHON := $(shell /usr/bin/which python$(PY_VERSION))

.DEFAULT_GOAL := build

clean:
	rm -rf dist

init:
	pip install pipenv
	pipenv install --dev

compile-app:
	mkdir -p $(BUILD_DIR)
	pipenv run cfn-lint $(TEMPLATE_DIR)/template.yml

test-unit:
	pipenv run python -m pytest -s tests/unit_tests/test_unit.py

test-integration:
	pipenv run python -m pytest -s tests/integration_tests/test_integration.py --stack-name $(APP_STACK_NAME)

build: package 

package: compile-app
	cp -r $(TEMPLATE_DIR)/template.yml src $(BUILD_DIR)

	# package dependencies in lib dir
	pipenv lock --requirements > $(BUILD_DIR)/requirements.txt
	pipenv run pip install -t $(BUILD_DIR)/src/ -r $(BUILD_DIR)/requirements.txt	

deploy: package
	pipenv run sam package --template-file $(BUILD_DIR)/template.yml --s3-bucket $(PACKAGE_BUCKET) --s3-prefix $(PACKAGE_PREFIX) --output-template-file $(BUILD_DIR)/packaged-template.yml
	pipenv run sam deploy --template-file $(BUILD_DIR)/packaged-template.yml --stack-name $(APP_STACK_NAME) --capabilities CAPABILITY_IAM

teardown:
	aws cloudformation delete-stack --stack-name $(APP_STACK_NAME)