import logging
from models import ConfigData, ndb, ServiceEndPointData


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
