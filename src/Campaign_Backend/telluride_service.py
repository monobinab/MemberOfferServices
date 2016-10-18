import logging
import httplib
from google.appengine.api import memcache
import json
from getXml import get_create_offer_xml, get_update_offer_xml, get_register_offer_xml
import xml.etree.ElementTree as ET

CLIENT_ID = "OFFER_REC_SYS_QA"
CREATE_OFFER_URL = "esbqa-1080.searshc.com"
CREATE_OFFER_REQUEST = "/rest/tellurideAS/Offer"

ACTIVATE_OFFER_URL = 'trtstel2app01.vm.itg.corp.us.shldcorp.com'
ACTIVATE_OFFER_REQUEST = "/tellurideAS/Offer"
ACTIVATE_OFFER_PORT = 8580

REGISTER_OFFER_URL = 'trtstel2app01.vm.itg.corp.us.shldcorp.com'
REGISTER_OFFER_REQUEST = "/tellurideAS/Bank"


class TellurideService:
    def __init__(self):
        pass

    @classmethod
    def create_offer(cls, offer, member_entity):
        response_dict = dict()
        post_data = get_create_offer_xml(offer).rstrip('\n')
        logging.info("post_data: %s", post_data)

        result = TellurideService.make_request(url=CREATE_OFFER_URL, port=None, put_request=CREATE_OFFER_REQUEST,
                                               request_type="POST", data=post_data)
        doc = ET.fromstring(result)
        status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
        if int(status_code) == 0:
            update_offer_xml = get_update_offer_xml(offer_entity=offer).rstrip('\n')
            update_offer_result = TellurideService.make_request(url=ACTIVATE_OFFER_URL, port=ACTIVATE_OFFER_PORT,
                                                                put_request=ACTIVATE_OFFER_REQUEST,
                                                                request_type="POST", data=update_offer_xml)
            doc = ET.fromstring(update_offer_result)
            status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
            if int(status_code) == 0:
                logging.info("Activated offer")
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer has been created and activated successfully"
            else:
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer has been created successfully, but could not activate."
        else:
            logging.error("Create offer failed:: Telluride call returned with error."
                          " Status:: %s, Status Text:: %s", status_code,
                          doc.find('.//{http://rewards.sears.com/schemas/}StatusText').text)
            response_dict['data'] = str(result)
            response_dict['message'] = "Offer activation has failed!!!"

        return response_dict

    @classmethod
    def register_member(cls, offer, member_entity):
        post_data = get_register_offer_xml(offer, member_entity).rstrip('\n')
        logging.info("post_data: %s", post_data)

        result = TellurideService.make_request(url=REGISTER_OFFER_URL, port=ACTIVATE_OFFER_PORT, put_request=REGISTER_OFFER_REQUEST,
                                               request_type="POST", data=post_data)
        doc = ET.fromstring(result)
        status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
        return status_code

    @classmethod
    def make_request(cls, url, port, put_request, request_type, data):
        logging.info('**** data: %s', data)

        if port is not None:
            webservice = httplib.HTTP(url, port=port)
            logging.info('****url: %s', url)

            webservice.putrequest(request_type, put_request)
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
        else:
            # Fetch access token from memcache
            access_token = memcache.get(key="ACCESS_TOKEN")
            if access_token is None:
                logging.info('Got None access_token from memcache. Generating new token')
                # Generating new Access Token
                generated_access_token = GenerateAccessToken.generate()
                # Writing to memcache
                memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
                access_token = generated_access_token

            logging.info('Existing access_token from memcache: %s', access_token)
            logging.info('****url: %s', url)

            webservice = httplib.HTTPS(url)
            webservice.putrequest(request_type, put_request)
            webservice.putheader("client_id", "OFFER_REC_SYS_QA")
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

            if status_code == 500:
                logging.info('Request failed with status_code = 500')
                logging.info('Generating new Access Token and retrying')
                # Generating new Access Token
                generated_access_token = GenerateAccessToken.generate()
                # Deleting exisitng access token and Writing new token to memcache
                memcache.delete(key="ACCESS_TOKEN")
                logging.info('Deleted exisiting memcache ACCESS_TOKEN value')
                memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
                logging.info('Written new ACCESS_TOKEN value to memcache')

                # retry with new access token

                webservice2 = httplib.HTTPS(url)
                webservice2.putrequest(request_type, put_request)
                webservice2.putheader("client_id", "OFFER_REC_SYS_QA")
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
    def generate(cls):
        access_token_url = 'syw-offers-accesstoken-qa-dot-syw-offers.appspot.com'
        webservice = httplib.HTTPS(access_token_url)
        webservice.putrequest("GET", "/generateAccessToken")
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
