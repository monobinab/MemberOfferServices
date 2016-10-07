import yaml
import os
import sys


# Function to read configurations
def get_configuration():
    dataMap = {}
    try:
        with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as stream:
            try:
                dataMap = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print 'YAML error'
    except IOError:
        print 'IO error'

    return dataMap