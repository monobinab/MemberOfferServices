import logging
from models import ndb, ServiceEndPointData
import json
from models import ConfigData
from google.appengine.api import urlfetch
from google.appengine.api import app_identity
import jinja2
import os


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


# Function to read url configurations
def get_url_configuration():
    data_map = dict()
    try:
        # namespace_manager.set_namespace(config_namespace)
        # logging.info("Namespace set::" + config_namespace)
        data_entity = ConfigData.get_by_id('URLConfig')
        data_map['GENERATE_TOKEN_HOST'] = data_entity.GENERATE_TOKEN_HOST
        data_map['GENERATE_TOKEN_URL'] = data_entity.GENERATE_TOKEN_URL
        data_map['TELLURIDE_CLIENT_ID'] = data_entity.TELLURIDE_CLIENT_ID

        data_map['CREATE_OFFER_URL'] = data_entity.CREATE_OFFER_URL
        data_map['CREATE_OFFER_REQUEST'] = data_entity.CREATE_OFFER_REQUEST

        data_map['ACTIVATE_OFFER_URL'] = data_entity.ACTIVATE_OFFER_URL
        data_map['ACTIVATE_OFFER_REQUEST'] = data_entity.ACTIVATE_OFFER_REQUEST
        data_map['ACTIVATE_OFFER_PORT'] = data_entity.ACTIVATE_OFFER_PORT

        data_map['REGISTER_OFFER_URL'] = data_entity.REGISTER_OFFER_URL
        data_map['REGISTER_OFFER_REQUEST'] = data_entity.REGISTER_OFFER_REQUEST

        data_map['REDEEM_OFFER_REQUEST'] = data_entity.REDEEM_OFFER_REQUEST

    except Exception as e:
        logging.error(e)
    finally:
        return data_map


# Function to read PubSub configurations
def get_pubsub_configuration():
    data_map = dict()
    data_key = ndb.Key('ConfigData', 'PubSubConfig')
    data_entity = data_key.get()
    data_map['SERVICE_TOPIC'] = data_entity.SERVICE_TOPIC
    data_map['PUBLISH_TOKEN'] = data_entity.PUBLISH_TOKEN
    return data_map


# Function to read PubSub configurations
def create_pubsub_message(json_data):
    campaign_dict = json_data['campaign_details']
    offer_dict = json_data['offer_details']
    config_dict = get_pubsub_configuration()

    category_type = ''
    category_string = ''
    if 'divisions' in campaign_dict:
        category_string = __get_property_value('divisions', campaign_dict)
        category_type = 'div'
    else:
        if 'category' in campaign_dict:
            category_string = __get_property_value('category', campaign_dict)
            category_type = 'soar'
        else:
            category_type = 'div'
            default_div_list = ndb.Key('ConfigData', 'GeneralConfig').get()
            if campaign_dict['format_level'] == 'Sears':
                category_string = ', '.join(default_div_list.SearsDefaultDiv)
            else:
                category_string = ', '.join(default_div_list.KmartDefaultDiv)

    store_string = ''
    if 'store_location' in campaign_dict:
        store_string = __get_property_value('store_location', campaign_dict)

    campaign_data = dict()
    campaign_data['message'] = dict()
    campaign_data['message']["token"] = config_dict['PUBLISH_TOKEN']
    campaign_data['message']["campaign_name"] = campaign_dict['name']
    campaign_data['message']["category_type"] = category_type
    campaign_data['message']["start_date"] = campaign_dict['start_date']
    campaign_data['message']["campaign_format"] = campaign_dict['format_level']
    campaign_data['message']["store_location"] = store_string
    campaign_data['message']["period"] = campaign_dict['period']
    campaign_data['message']["offer_max_val"] = str(offer_dict['max_value'])
    campaign_data['message']["categories"] = category_string

    campaign_json_data = json.dumps(campaign_data)
    return campaign_json_data



def make_request(host, relative_url, request_type, payload):
    logging.info("URL:: " + str(host) + str(relative_url))
    logging.info("Request Method:: " + request_type)
    logging.info("Payload:: " + payload)
    try:
        app_id = app_identity.get_application_id()
        urlfetch.set_default_fetch_deadline(60)
        logging.info("App id:: %s", app_id)
        result = urlfetch.fetch(host + relative_url, headers={"X-Appengine-Inbound-Appid": app_id})
        if result.status_code == 200:
            logging.info('Response status_code: %s', result.status_code)
            # logging.info('Response status_message: %s', status_message)
            # logging.info('Response header: %s', header)
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


def get_jinja_environment():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    logging.info("Templates directory :: %s", templates_dir)

    jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_dir)
    )
    return jinja_environment


def get_telluride_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get(use_datastore=True, use_cache=False, use_memcache=False)
    return data_entity.telluride


def get_email_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get(use_datastore=True, use_cache=False, use_memcache=False)
    return data_entity.email


def get_member_host():
    data_key = ndb.Key('ServiceEndPointData', 'endpoints')
    data_entity = data_key.get(use_datastore=True, use_cache=False, use_memcache=False)
    logging.info("Data entity:: %s", data_entity)
    return data_entity.member

def __get_property_value(property_name, campaign_dict):
    property_string = ''
    property_list = campaign_dict[property_name].split(',')
    for i, val in enumerate(property_list):
        prop = val.split('-')
        if prop:
            prop_id = prop[0].strip()
            if i == 0:
                property_string = prop_id
            else:
                property_string = property_string + ', ' + prop_id

    return property_string
