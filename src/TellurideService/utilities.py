import logging
from models import ConfigData


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


