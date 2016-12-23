import logging
from models import ndb
import json
from models import ConfigData
from google.appengine.api import urlfetch
from google.appengine.api import app_identity
import jinja2
import os

# Function to read sendgrid configurations
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

    campaign_data = dict()
    campaign_data['message'] = dict()
    campaign_data['message']["token"] = config_dict['PUBLISH_TOKEN']

    campaign_data['message']["campaign_name"] = campaign_dict['name']
    campaign_data['message']["campaign_budget"] = campaign_dict['money']
    campaign_data['message']["campaign_category"] = campaign_dict['category']
    campaign_data['message']["campaign_convratio"] = campaign_dict['conversion_ratio']
    campaign_data['message']["campaign_period"] = campaign_dict['period']
    campaign_data['message']["start_date"] = campaign_dict['start_date']
    campaign_data['message']["store_location"] = campaign_dict['store_location']
    campaign_data['message']["format_level"] = campaign_dict['format_level']

    campaign_data['message']["offer_type"] = offer_dict['offer_type']
    campaign_data['message']["offer_min_val"] = offer_dict['min_value']
    campaign_data['message']["offer_max_val"] = offer_dict['max_value']
    campaign_data['message']["offer_mbr_issuance"] = offer_dict['member_issuance']

    campaign_json_data = json.dumps(campaign_data)
    return campaign_json_data


def make_request(host, relative_url, request_type, payload):
    logging.info("URL:: " + host + relative_url)
    logging.info("Request Method:: " + request_type)
    logging.info("Payload:: " + payload)
    try:
        app_id = app_identity.get_application_id()
        urlfetch.set_default_fetch_deadline(60)
        logging.info("App id:: %s", app_id)
        result = urlfetch.fetch("https://"+host + relative_url, headers={"X-Appengine-Inbound-Appid": app_id})
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