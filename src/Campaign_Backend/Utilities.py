from models import ndb
import logging
import json
import base64


# Function to read sendgrid configurations
def get_sendgrid_configuration():
    data_map = dict()
    data_key = ndb.Key('ConfigData', 'SendGridConfig')
    data_entity = data_key.get()
    data_map['SENDGRID_API_KEY'] = data_entity.SENDGRID_API_KEY
    data_map['SENDGRID_SENDER'] = data_entity.SENDGRID_SENDER
    data_map['TEMPLATE_ID'] = data_entity.TEMPLATE_ID

    return data_map


# Function to read url configurations
def get_url_configuration():
    data_map = dict()
    data_key = ndb.Key('ConfigData', 'URLConfig')
    data_entity = data_key.get()
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

    campaign_data = {}
    campaign_data['message'] = {}
    campaign_data['message']["token"] = config_dict['PUBLISH_TOKEN']
    campaign_data['message']["campaign_name"] = campaign_dict['name']
    campaign_data['message']["campaign_budget"] = campaign_dict['money']
    campaign_data['message']["campaign_category"] = campaign_dict['category']
    campaign_data['message']["campaign_convratio"] = campaign_dict['conversion_ratio']
    campaign_data['message']["campaign_period"] = campaign_dict['period']
    campaign_data['message']["start_date"] = campaign_dict['start_date']
    campaign_data['message']["offer_type"] = offer_dict['offer_type']
    campaign_data['message']["offer_min_val"] = offer_dict['min_value']
    campaign_data['message']["offer_max_val"] = offer_dict['max_value']
    campaign_data['message']["offer_mbr_issuance"] = offer_dict['member_issuance']

    campaign_json_data = json.dumps(campaign_data)

    return campaign_json_data
