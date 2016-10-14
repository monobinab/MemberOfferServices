from models import ndb


# Function to read configurations
def get_configuration():
    data_map = dict()
    data_key = ndb.Key('SendgridData', '1')
    data_entity = data_key.get()
    data_map['SENDGRID_API_KEY'] = data_entity.SENDGRID_API_KEY
    data_map['SENDGRID_SENDER'] = data_entity.SENDGRID_SENDER
    data_map['TEMPLATE_ID'] = data_entity.TEMPLATE_ID
    return data_map
