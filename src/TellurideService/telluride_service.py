import logging
import httplib
from google.appengine.api import memcache
import json
from getXml import get_create_offer_xml, get_update_offer_xml, get_register_offer_xml, \
    get_redeem_offer_xml, get_balance_xml, get_change_offer_dates_xml
import xml.etree.ElementTree as ET
from utilities import get_url_configuration

ERROR_NS = 'http://rewards.sears.com/schemas/offer/'
STATUS_NS = 'http://rewards.sears.com/schemas/'


class TellurideService:
    def __init__(self):
        pass

    @classmethod
    def create_offer(cls, offer):
        response_dict = dict()
        logging.info("Offer:: %s", offer)
        post_data = get_create_offer_xml(offer).rstrip('\n')
        # logging.info("post_data: %s", post_data)
        config_data = get_url_configuration()
        logging.info("Config Data:: %s" % config_data)

        result = TellurideService.make_request(url=config_data['CREATE_OFFER_URL'],
                                               put_request=config_data['CREATE_OFFER_REQUEST'],
                                               request_type="POST", data=post_data, config_data=config_data,
                                               is_token_required=True)
        doc = ET.fromstring(result)
        status_code = int(doc.find('.//{'+STATUS_NS+'}Status').text)
        logging.info("Status code:: %s", status_code)
        if status_code == 0:
            update_offer_xml = get_update_offer_xml(offer_entity=offer, offer_status='ACTIVATED').rstrip('\n')
            update_offer_result = TellurideService.make_request(url=config_data['ACTIVATE_OFFER_URL'],
                                                                put_request=config_data['ACTIVATE_OFFER_REQUEST'],
                                                                request_type="POST", data=update_offer_xml,
                                                                config_data=config_data, is_token_required=True)
            if update_offer_result is not None:
                doc = ET.fromstring(update_offer_result)
                status_code = int(doc.find('.//{'+STATUS_NS+'}Status').text)
                if status_code == 0:
                    logging.info("Activated offer")
                    response_dict['message'] = "Offer has been created and activated successfully"
                    response_dict['status_code'] = status_code

            else:
                response_dict['message'] = "Offer has been created successfully, but could not activate."
                response_dict['error_message'] = doc.find('.//{' + ERROR_NS + '}ErrorText').text
                response_dict['status_code'] = status_code
        else:
            error_code = doc.find('.//{'+ERROR_NS+'}ErrorCode').text
            error_text = doc.find('.//{'+ERROR_NS+'}ErrorText').text
            logging.info("Error code:: %s", error_code)
            logging.info("Error text:: %s", error_text)

            if error_code is not None:
                # error_text = doc.find('.//{http://rewards.sears.com/schemas/}ErrorText').text
                if not error_text == "Offer update only allowed in DRAFT status":
                    logging.error("Create offer failed:: Telluride call returned with error."
                                  " Status:: %s, Status Text:: %s and Error Text:: %s", status_code,
                                  doc.find('.//{'+STATUS_NS+'}StatusText').text, error_text)
                    response_dict['message'] = "Offer activation has failed!!!"

                else:
                    response_dict['message'] = "Offer could not be created."
                    response_dict['status_code'] = status_code
                    response_dict['error_message'] = error_text
            else:
                response_dict['message'] = "Offer has been created successfully, but could not activate."
                response_dict['status_code'] = status_code

        # response_dict['data'] = str(result)
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
        logging.info("Result:: %s", result)
        doc = ET.fromstring(result)
        status_code = int(doc.find('.//{http://www.epsilon.com/webservices/}Status').text)
        response_dict = dict()
        if status_code == 0:
            response_dict['message'] = "Member has been registered to the offer successfully."
            response_dict['status_code'] = status_code
        else:
            response_dict['message'] = "Member registration to the offer has failed."
            response_dict['error_message'] = doc.find('.//{http://www.epsilon.com/webservices/}StatusText').text
            response_dict['status_code'] = status_code
        return response_dict

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
    def update_kpos_offer(cls, offer, member, start_date, end_date):
        """
        :param offer: offer object
        :param member: member object
        :param start_date: new start date
        :param end_date: new end date
        1. Change offer status to DRAFT
        2. Update offer start and end dates and send telluride request.
        3. Change offer status to ACTIVATED
        :return:
        """
        config_data = get_url_configuration()

        response_dict = TellurideService.change_offer_status(offer, 'DRAFT')
        logging.info("Offer status changed to DRAFT. Response dict :: %s", response_dict)

        change_offer_dates_xml = get_change_offer_dates_xml(offer=offer,
                                                            start_date=start_date,
                                                            end_date=end_date).rstrip('\n')

        change_offer_dates_result = TellurideService.make_request(url=config_data['CREATE_OFFER_URL'],
                                                                  put_request=config_data['CREATE_OFFER_REQUEST'],
                                                                  request_type="POST",
                                                                  data=change_offer_dates_xml,
                                                                  config_data=config_data,
                                                                  is_token_required=True)
        doc = ET.fromstring(change_offer_dates_result)
        status_code = int(doc.find('.//{' + STATUS_NS + '}Status').text)
        logging.info("Status code:: %s", status_code)

        if status_code == 0:
            response_dict = TellurideService.change_offer_status(offer, 'ACTIVATED')
            logging.info("Offer status changed to ACTIVATED. Response dict :: %s", response_dict)
        else:
            error_code = doc.find('.//{' + ERROR_NS + '}ErrorCode').text
            error_text = doc.find('.//{' + ERROR_NS + '}ErrorText').text
            logging.info("Error code:: %s", error_code)
            logging.info("Error text:: %s", error_text)

        return change_offer_dates_result

    @classmethod
    def change_offer_status(cls, offer, offer_status):
        response_dict = dict()
        config_data = get_url_configuration()
        update_offer_xml = get_update_offer_xml(offer_entity=offer,
                                                offer_status=offer_status).rstrip('\n')

        update_offer_result = TellurideService.make_request(url=config_data['ACTIVATE_OFFER_URL'],
                                                            put_request=config_data['ACTIVATE_OFFER_REQUEST'],
                                                            request_type="POST",
                                                            data=update_offer_xml,
                                                            config_data=config_data,
                                                            is_token_required=True)
        doc = ET.fromstring(update_offer_result)
        status_code = int(doc.find('.//{' + STATUS_NS + '}Status').text)

        if update_offer_result is not None:
            if status_code == 0:
                logging.info("Activated offer")
                response_dict['message'] = str("Offer status has been changed successfully to %s", offer_status)
                response_dict['status_code'] = status_code
            else:
                response_dict['message'] = "Offer could not activate."
                response_dict['error_message'] = doc.find('.//{' + ERROR_NS + '}ErrorText').text
                response_dict['status_code'] = status_code
        else:
            error_code = doc.find('.//{'+ERROR_NS+'}ErrorCode').text
            error_text = doc.find('.//{'+ERROR_NS+'}ErrorText').text
            logging.info("Error code:: %s", error_code)
            logging.info("Error text:: %s", error_text)

            if error_code is not None:
                # error_text = doc.find('.//{http://rewards.sears.com/schemas/}ErrorText').text
                if not error_text == "Offer update only allowed in DRAFT status":
                    logging.error("Create offer failed:: Telluride call returned with error."
                                  " Status:: %s, Status Text:: %s and Error Text:: %s", status_code,
                                  doc.find('.//{'+STATUS_NS+'}StatusText').text, error_text)
                    response_dict['message'] = "Offer activation has failed!!!"

                else:
                    response_dict['message'] = "Offer could not be created."
                    response_dict['status_code'] = status_code
                    response_dict['error_message'] = error_text
            else:
                response_dict['message'] = "Offer has been created successfully, but could not activate."
                response_dict['status_code'] = status_code
        return response_dict

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
        logging.info("URL:: %s", url+put_request)
        webservice.timeout = 30
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
