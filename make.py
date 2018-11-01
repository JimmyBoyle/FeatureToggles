import shutil
import os
import sys
import argparse
import subprocess
import distutils
from distutils import dir_util

BUILD_DIR = 'dist'
TEMPLATE_DIR = 'sam'
PACKAGE_BUCKET = 'lambda-code-toggles'
APP_STACK_NAME = 'jimbo-toggles-1'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', default='build', type=str,
                        help='Target for building up the project')
    target = parser.parse_args().target

    if target == 'clean':
        clean()
    if target == 'init':
        init()
    if target == 'compile-app':
        compile_app()
    if target == 'package':
        package()
    if target == 'test':
        test()


def clean():
    try:
        if os.path.exists(BUILD_DIR) and os.path.isdir(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
    except OSError as e:
        print e
    return


def init():
    commands = []
    commands.append('python -m pip install pipenv --user')
    commands.append('pipenv sync --dev')

    for command in commands:
        print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        for c in iter(lambda: process.stdout.read(1), ''):
            sys.stdout.write(c)
    return


def compile_app():
    if not os.path.exists(BUILD_DIR) and not os.path.isdir(BUILD_DIR):
        os.mkdir(BUILD_DIR)

    commands = []
    commands.append('pipenv run cfn-lint {}/template.yml'.format(TEMPLATE_DIR))

    for command in commands:
        print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        for c in iter(lambda: process.stdout.read(1), ''):
            continue
            # sys.stdout.write(c)
    return


def test():
    package()
    commands = []
    commands.append("pipenv run sam local invoke  --template {}/template.yml UpdateFeatureToggles --env-vars tests/env_var.json -e test/update_feature_toggles_happycase.json  --debug".format(BUILD_DIR))

    for command in commands:
        print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        for c in iter(lambda: process.stdout.read(1), ''):
            sys.stdout.write(c)
    return


def package():
    compile_app()
    distutils.dir_util.copy_tree('app', '{}/app'.format(BUILD_DIR))
    shutil.copy('{}/template.yml'.format(TEMPLATE_DIR), BUILD_DIR)

    req = subprocess.check_output('pipenv lock --requirements', shell=True)
    with open('{}/requirements.txt'.format(BUILD_DIR), 'w') as requirements:
        requirements.write(req)

    commands = []
    commands.append(
        'pipenv run pip install -t {}/app/ -r {}/requirements.txt'.format(BUILD_DIR, BUILD_DIR))

    for command in commands:
        print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        for c in iter(lambda: process.stdout.read(1), ''):
            continue
            # sys.stdout.write(c)
    return


def deploy():
    package()

    commands = []
    commands.append('pipenv run sam package --template-file {}}/template.yml --s3-bucket {} --output-template-file {}/packaged-template.yml'.format(
        BUILD_DIR, PACKAGE_BUCKET, BUILD_DIR))
    commands.append(
        'pipenv run sam deploy --template-file {}/packaged-template.yml --stack-name {} --capabilities CAPABILITY_IAM'.format(BUILD_DIR, APP_STACK_NAME))

    for command in commands:
        print command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        for c in iter(lambda: process.stdout.read(1), ''):
            sys.stdout.write(c)
    return


if __name__ == '__main__':
    main()
