import logging
from models import ConfigData, ndb, ServiceEndPointData
from google.appengine.api import urlfetch
from google.appengine.api import app_identity

def get_sendgrid_configuration():
    data_map = dict()
    try:
        data_entity = ConfigData.get_by_id('SendGridConfig')
        data_map['SENDGRID_API_KEY'] = data_entity.SENDGRID_API_KEY
        data_map['SENDGRID_SENDER'] = data_entity.SENDGRID_SENDER
        data_map['TEMPLATE_ID'] = data_entity.TEMPLATE_ID
    except Exception as e:
        logging.error(e)
    finally:
        return data_map

def make_request(host, relative_url, request_type, payload):
    logging.info("URL:: " + host + relative_url)
    logging.info("Request Method:: " + request_type)
    logging.info("Payload:: " + payload)
    try:
        app_id = app_identity.get_application_id()
        urlfetch.set_default_fetch_deadline(60)
        logging.info("App id:: %s", app_id)
        result = urlfetch.fetch(host + relative_url, headers={"X-Appengine-Inbound-Appid": app_id})
        if result.status_code == 200:
            logging.info('Response status_code: %s', result.status_code)
            logging.info('Response result: %s', str(result))
            logging.info('Response result content: %s', str(result.content))

        else:
            status_code = result.status_code
            logging.info('Response status_code: %s', status_code)
        return result.content
    except urlfetch.Error:
        logging.exception('Caught exception fetching url')
    except Exception as e:
        logging.error(e)

def get_telluride_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get()
    return data_entity.telluride


def get_email_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get()
    return data_entity.email


def get_backend_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get()
    return data_entity.backend

def get_member_offer_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get()
    return data_entity.member

def get_emailconfig_data():
    data_key = ndb.Key('ConfigData', 'EmailChannelConfig')
    data_entity = data_key.get()
    return data_entity    
