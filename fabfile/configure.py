#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from getpass import getpass
from fabric.tasks import Task
from fabric.colors import green
from fabric.api import task, env, local
from boto3 import Session


def require_input(prompt, hide=False):
    """
    Demand input from the user.
    """
    i = None
    while not i:
        if hide:
            i = getpass(prompt.strip()+' ')
        else:
            i = raw_input(prompt.strip()+' ')

        if not i:
            print '  I need this, please.'
    return i


def get_current_config():
    """
    Return a dict of the vars currently in the config_file
    """
    config = {}

    if os.path.isfile(env.config_file):
        with open(env.config_file) as f:
            for line in f:
                if 'export' in line:
                    line = line.replace('export', '').strip().split('=')
                    config[line[0]] = line[1]

    return config


def add_aws_config(setting, value):
    """
    Add an aws configuration (setting name and value) to the config file.
    """
    config = get_current_config()

    with open(env.config_file, 'w') as f:
        f.write('#!/bin/bash\n\n')
        config[setting.upper()] = value
        for k, v in config.iteritems():
            f.write('export {0}={1}\n'.format(k, v))


@task
def configure():
    """
    Initialize AWS configuration, which are stored in the config_file.
    """
    config = {}

    print('')
    print('AWS configuration')
    print('=================')
    print('')

    # Request data from the user
    config['AWS_ACCESS_KEY_ID'] = require_input(
        'Your AWS access key [Required]:',
        hide=True,
    )
    config['AWS_SECRET_ACCESS_KEY'] = require_input(
        'Your AWS secret key [Required]:',
        hide=True,
    )
    config['KEY_NAME'] = raw_input(
        'Your AWS key name [Default: my-key-pair]:'
    ) or 'my-key-pair'
    config['DB_PASSWORD'] = require_input(
        'Database user password [Required]:',
        hide=True,
    )
    config['RDS_HOST'] = raw_input('RDS Host [press ENTER to skip]:')
    config['EC2_HOST'] = raw_input('EC2 Host [press ENTER to skip]:')

    with open(env.config_file, 'w') as f:
        f.write('#!/bin/bash\n\n')

        for k, v in config.iteritems():
            f.write('export {0}={1}\n'.format(k, v))

    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in {0}'.format(env.config_file))
    print('')


def loadconfig():
    """
    Load aws configs into fab env
    """
    if not os.path.isfile(env.config_file):
        configure()

    config = get_current_config()

    for k, v in config.iteritems():
        env[k] = v
    
    try:
        env.hosts = [env.EC2_HOST, ]
        env.host = env.EC2_HOST
        env.host_string = env.EC2_HOST
    except AttributeError:
        pass

    try:
        env.key_filename = (
            os.path.join(env.key_file_dir, "%s.pem" % env.KEY_NAME),
        )
    except AttributeError:
        pass

    try:
        env.hosts = [env.EC2_HOST, ]
        env.host = env.EC2_HOST
        env.host_string = env.EC2_HOST
    except AttributeError:
        pass

    try:
        env.key_filename = (
            os.path.join(env.key_file_dir, "%s.pem" % env.key_name),
        )
    except AttributeError:
        pass


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
