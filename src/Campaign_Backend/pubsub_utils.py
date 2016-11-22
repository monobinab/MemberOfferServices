import os
import threading
import logging
import base64
import json

from google.appengine.api import app_identity
from google.appengine.api import memcache
from google.appengine.api import modules
import Utilities
import sys
import time

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials


client_store = threading.local()

def is_devserver():
    """Check if the app is running on devserver or not."""
    return os.getenv('SERVER_SOFTWARE', '').startswith('Dev')


def get_client():
    """Creates Pub/Sub client and returns it."""
    if not hasattr(client_store, 'client'):
        client_store.client = get_client_from_credentials(
            GoogleCredentials.get_application_default())
    return client_store.client


def get_client_from_credentials(credentials):
    """Creates Pub/Sub client from a given credentials and returns it."""
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('pubsub', 'v1', credentials=credentials)

def get_full_topic_name():
    return 'projects/{}/topics/{}'.format(
        get_project_id(), get_app_topic_name())

def post_pubsub(message):
    """Publishes the message via the Pub/Sub API."""
    logging.info('Going to get client')
    config_dict = Utilities.get_pubsub_configuration()

    client = get_client()
    logging.info('Got client')
    logging.info('message:: %s', message)
    retry_count = 5

    if message:
        topic_name = config_dict['SERVICE_TOPIC'].encode("utf-8")
        logging.info('topic_name:: %s', topic_name)

        body = {
            'messages': [{
                'data': base64.b64encode(message.encode('utf-8'))
            }]
        }

        count = 0
        while (True):
            if count < retry_count:
                response = client.projects().topics().publish(
                    topic=topic_name, body=body).execute()

                logging.info('response:: %s', response)
                message_id =  response['messageIds']

                if message_id:
                    logging.info('Execution complete. Message_id:: %s', message_id)
                    return 200
                else:
                    logging.info('PubSub execution failed. No Message_id returned. Retrying')
                    count = count + 1

    return 500
