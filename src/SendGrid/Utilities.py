import logging
from models import ConfigData, ndb

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
