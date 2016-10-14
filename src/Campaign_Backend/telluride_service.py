import logging
import httplib
from google.appengine.api import memcache
import json
from getOfferXml import get_xml
# import xml.etree.ElementTree as ET


class CreateOffer:
    def __init__(self):
        pass

    @classmethod
    def create_offer(cls, offer, member_entity):
        response_dict = dict()
        post_data = get_xml(offer).rstrip('\n')
        logging.info("post_data: %s", post_data)

        result = CreateOffer.make_telluride_request(post_data)
        # Below code is updating member offer object part
        # doc = ET.fromstring(result)
        # status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
        # if int(status_code) == 0:
        #     # Assuming one-to-one mapping with Member and Offer entities
        #     member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_entity.key,
        #                                              MemberOfferData.offer == offer.key).get()
        #     if member_offer_obj is not None:
        #         member_offer_obj.status = True
        #         member_offer_obj.put()
        #     else:
        #         logging.error("Member Offer Object not found for offer key :: %s and member key:: %s",
        #                       offer.key, member_entity.key)
        #
        #     logging.info("Activated offer %s for member %s", str(offer.key), str(member_entity.key))
        #     response_dict['data'] = str(result)
        #     response_dict['message'] = "Offer has been activated successfully"
        # else:
        #     logging.error("Telluride call returned with error for offer . Status:: %s, Status Text:: %s",
        #                   status_code, doc.find('.//{http://rewards.sears.com/schemas/}StatusText').text)
        #     response_dict['data'] = str(result)
        #     response_dict['message'] = "Offer activation has failed!!!"

        return response_dict

    @classmethod
    def make_telluride_request(cls, data):
        logging.info('**** data: %s', data)
        url = 'esbqa-1080.searshc.com'

        # Fetch access token from memcache
        access_token = memcache.get(key="ACCESS_TOKEN")
        if access_token is None:
            logging.info('Got None access_token from memcache. Generating new token')
            # Generating new Access Token
            generated_access_token = CreateOffer.generate_access_token()
            # Writing to memcache
            memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
            access_token = generated_access_token

        logging.info('Existing access_token from memcache: %s', access_token)
        logging.info('****url: %s', url)

        webservice = httplib.HTTPS(url)
        webservice.putrequest("POST", "/rest/tellurideAS/Offer")
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
            generated_access_token = CreateOffer.generate_access_token()
            # Deleting exisitng access token and Writing new token to memcache
            memcache.delete(key="ACCESS_TOKEN")
            logging.info('Deleted exisiting memcache ACCESS_TOKEN value')
            memcache.add(key="ACCESS_TOKEN", value=generated_access_token, time=0)
            logging.info('Written new ACCESS_TOKEN value to memcache')

            # retry with new access token
            webservice2 = httplib.HTTPS(url)
            webservice2.putrequest("POST", "/rest/tellurideAS/Offer")
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

    @classmethod
    def generate_access_token(cls):
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
