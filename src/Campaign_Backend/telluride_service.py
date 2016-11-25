import logging
import httplib
from google.appengine.api import memcache
import json
from getXml import get_create_offer_xml, get_update_offer_xml, get_register_offer_xml, get_redeem_offer_xml, get_balance_xml
import xml.etree.ElementTree as ET
from Utilities import get_url_configuration


class TellurideService:
    def __init__(self):
        pass

    @classmethod
    def create_offer(cls, offer):
        response_dict = dict()
        post_data = get_create_offer_xml(offer).rstrip('\n')
        # logging.info("post_data: %s", post_data)
        config_data = get_url_configuration()
        logging.info("Config Data:: %s" % config_data)

        result = TellurideService.make_request(url=config_data['CREATE_OFFER_URL'],
                                               put_request=config_data['CREATE_OFFER_REQUEST'],
                                               request_type="POST", data=post_data, config_data=config_data,
                                               is_token_required=True)
        doc = ET.fromstring(result)
        status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
        if int(status_code) == 0:
            update_offer_xml = get_update_offer_xml(offer_entity=offer).rstrip('\n')
            update_offer_result = TellurideService.make_request(url=config_data['ACTIVATE_OFFER_URL'],
                                                                put_request=config_data['ACTIVATE_OFFER_REQUEST'],
                                                                request_type="POST", data=update_offer_xml,
                                                                config_data=config_data, is_token_required=True)
            if update_offer_result is not None:
                doc = ET.fromstring(update_offer_result)
                status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
                if int(status_code) == 0:
                    logging.info("Activated offer")
                    response_dict['message'] = "Offer has been created and activated successfully"
            else:
                response_dict['message'] = "Offer has been created successfully, but could not activate."
        else:
            error_text = doc.find('.//{http://rewards.sears.com/schemas/}ErrorText').text
            if not error_text == "Offer update only allowed in DRAFT status":
                logging.error("Create offer failed:: Telluride call returned with error."
                              " Status:: %s, Status Text:: %s and Error Text:: %s", status_code,
                              doc.find('.//{http://rewards.sears.com/schemas/}StatusText').text, error_text)
                response_dict['message'] = "Offer activation has failed!!!"
            else:
                response_dict['message'] = "Offer has been created successfully, but could not activate."
        response_dict['data'] = str(result)
        return response_dict

    @classmethod
    def register_member(cls, offer, member_entity):
        post_data = get_register_offer_xml(offer, member_entity).rstrip('\n')
        logging.info("post_data: %s", post_data)
        config_data = get_url_configuration()
        logging.info("Config Data:: %s" % config_data)
        result = TellurideService.make_request(url=config_data['REGISTER_OFFER_URL'],
                                               put_request=config_data['REGISTER_OFFER_REQUEST'],
                                               request_type="POST", data=post_data, config_data=config_data,
                                               is_token_required=False)
        doc = ET.fromstring(result)
        status_code = doc.find('.//{http://www.epsilon.com/webservices/}Status').text
        return int(status_code)

    @classmethod
    def get_balance(cls):
        post_data = get_balance_xml().rstrip('\n')
        logging.info("post_data: %s", post_data)
        config_data = get_url_configuration()
        logging.info("Config Data:: %s" % config_data)
        result = TellurideService.make_request(url=config_data['REGISTER_OFFER_URL'],
                                               put_request=config_data['REDEEM_OFFER_REQUEST'],
                                               request_type="POST", data=post_data, config_data=config_data,
                                               is_token_required=False)
        # doc = ET.fromstring(result)
        # status_code = doc.find('.//{http://www.epsilon.com/webservices/}Status').text
        return result

    @classmethod
    def redeem_offer(cls):
        post_data = get_redeem_offer_xml().rstrip('\n')
        logging.info("post_data: %s", post_data)
        config_data = get_url_configuration()
        logging.info("Config Data:: %s" % config_data)
        result = TellurideService.make_request(url=config_data['REGISTER_OFFER_URL'],
                                               put_request=config_data['REDEEM_OFFER_REQUEST'],
                                               request_type="POST", data=post_data, config_data=config_data,
                                               is_token_required=False)
        # doc = ET.fromstring(result)
        # status_code = doc.find('.//{http://www.epsilon.com/webservices/}Status').text
        return result

    @classmethod
    def make_request(cls, url, put_request, request_type, data, config_data, is_token_required):
        if is_token_required:
            # Fetch access token from memcache
            access_token = memcache.get(key="ACCESS_TOKEN")
            if access_token is None:
                logging.info('Got None access_token from memcache. Generating new token')
                # Generating new Access Token
                generated_access_token = GenerateAccessToken.generate(config_data=config_data)
                # Writing to memcache
                memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
                access_token = generated_access_token

            logging.info('Existing access_token from memcache: %s', access_token)
            logging.info('****url: %s', url+"/"+put_request)

        webservice = httplib.HTTPS(url)
        webservice.timeout = 15
        webservice.putrequest(request_type, put_request)
        webservice.putheader("client_id", config_data['TELLURIDE_CLIENT_ID'])
        if is_token_required:
            webservice.putheader("access_token", access_token)
        webservice.putheader("Content-type", "application/xml")
        webservice.endheaders()
        webservice.send(data)

        # get the response
        status_code, status_message, header = webservice.getreply()
        result = webservice.getfile().read()
        logging.info('Response status_code: %s', status_code)
        logging.info('Response status_message: %s', status_message)
        logging.info('Response header: %s', header)
        logging.info('Response result: %s', result)

        if is_token_required and status_code == 500:
            logging.info('Request failed with status_code = 500')
            logging.info('Generating new Access Token and retrying')
            # Generating new Access Token
            generated_access_token = GenerateAccessToken.generate(config_data=config_data)
            # Deleting exisitng access token and Writing new token to memcache
            memcache.delete(key="ACCESS_TOKEN")
            logging.info('Deleted existing memcache ACCESS_TOKEN value')
            memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
            logging.info('Written new ACCESS_TOKEN value to memcache')

            # retry with new access token

            webservice2 = httplib.HTTPS(url)
            webservice2.timeout = 15
            webservice2.putrequest(request_type, put_request)
            webservice2.putheader("client_id", config_data['TELLURIDE_CLIENT_ID'])
            webservice2.putheader("access_token", generated_access_token)
            webservice2.putheader("Content-type", "application/xml")
            webservice2.endheaders()
            webservice2.send(data)

            # get the response after retry
            status_code2, status_message2, header2 = webservice2.getreply()
            result2 = webservice2.getfile().read()
            logging.info('Response status_code: %s', status_code2)
            logging.info('Response status_message: %s', status_message2)
            logging.info('Response header: %s', header2)
            logging.info('Response result: %s', result2)

        return result


class GenerateAccessToken:
    def __init__(self):
        pass

    @classmethod
    def generate(cls, config_data):
        webservice = httplib.HTTPS(config_data['GENERATE_TOKEN_HOST'])
        webservice.putrequest("GET", config_data['GENERATE_TOKEN_URL'])
        status_code, status_message, header = webservice.getreply()
        access_token_result = webservice.getfile().read()

        logging.info('Response access_token_result: %s', access_token_result)

        try:
            json_response = json.loads(access_token_result)
        except ValueError:
            # decoding failed. Retrying.
            logging.info('Response decoding to JSON failed. Retrying to generate token.')
            status_code, status_message, header = webservice.getreply()
            access_token_result = webservice.getfile().read()
            logging.info('Response access_token_result from retry : %s', access_token_result)
            json_response = json.loads(access_token_result)

        new_generated_access_token = json_response['access_token']
        logging.info('New access_token: %s', new_generated_access_token)

        return new_generated_access_token
