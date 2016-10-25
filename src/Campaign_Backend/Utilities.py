from models import ndb


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