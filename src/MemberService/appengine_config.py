import os


def namespace_manager_default_namespace_for_request():
    return os.environ.get('NAMESPACE')
