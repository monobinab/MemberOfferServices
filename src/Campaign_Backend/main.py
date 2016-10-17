from datetime import datetime, timedelta
import json
import logging
from datetime import datetime
import webapp2
from models import CampaignData, OfferData, MemberData, MemberOfferData, ndb
from getOfferXml import get_xml
import httplib
import sendEmail
import xml.etree.ElementTree as ET
from google.appengine.api import memcache
from google.appengine.api import app_identity
from google.appengine.api import modules


DEFAULT_CAMPAIGN_NAME = 'default_campaign'


def get_campaign_key(campaign_name=DEFAULT_CAMPAIGN_NAME):
    return ndb.Key('CampaignData', campaign_name)


class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        self.response.write('An error occurred.')
        logging.exception(self, exception, debug)

        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)


class IndexPageHandler(webapp2.RequestHandler):
    def get(self):
        version_name = modules.get_current_version_name()
        app_name = app_identity.get_application_id()
        # server_url = app_identity.get_default_version_hostname()
        # self.response.write("Service running on:: " + server_url)
        self.response.write("Service running on:: " + version_name + "-dot-"+app_name)


class SaveCampaignHandler(webapp2.RequestHandler):
    def get(self):
        offer_data = self.request.get('offer_data')
        logging.info('****offerdata: %s', offer_data)
        json_data = json.loads(offer_data)
        campaign_dict = json_data['campaign_details']
        campaign_name = campaign_dict['name']
        is_entity = ndb.Key('CampaignData', campaign_name).get()
        logging.info('is_entity: %s', is_entity)
        logging.info('type is_entity: %s', type(is_entity))
        # Check for create new entity or update an existing entity
        if is_entity is None:
            save_campaign(json_data, datetime.now())
        else:
            save_campaign(json_data, is_entity.created_at)
        self.response.headers['Access-Control-Allow-Origin'] = '*'


class GetAllCampaignsHandler(webapp2.RequestHandler):
    def get(self):
        query = CampaignData.query()
        entity_list = query.fetch(100)
        result = list()
        logging.info('len of the list: %s', len(entity_list))
        for each in entity_list:
            key = ndb.Key('CampaignData', each.name)
            each_entity = key.get()
            campaign_dict = dict()
            offer_dict = dict()
            campaign_dict['campaign_id'] = each_entity.key.id()
            campaign_dict['name'] = each_entity.name
            campaign_dict['money'] = each_entity.money
            campaign_dict['category'] = each_entity.category
            campaign_dict['conversion_ratio'] = each_entity.conversion_ratio
            campaign_dict['period'] = each_entity.period
            campaign_dict['start_date'] = str(each_entity.start_date)
            campaign_dict['created_at'] = str(each_entity.created_at)

            offer_dict['offer_id'] = each_entity.key.id()
            offer_dict['offer_type'] = each_entity.offer_type
            offer_dict['min_value'] = each_entity.min_value
            offer_dict['max_value'] = each_entity.max_value
            offer_dict['valid_till'] = each_entity.valid_till
            offer_dict['member_issuance'] = each_entity.max_per_member_issuance_frequency
            each_dict = dict()
            each_dict['campaign_details'] = campaign_dict
            each_dict['offer_details'] = offer_dict
            result.append(each_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))


def save_campaign(json_data, created_time):
    campaign_dict = json_data['campaign_details']
    offer_dict = json_data['offer_details']

    campaign_name = campaign_dict['name']
    campaign_money = int(campaign_dict['money'])
    campaign_category = campaign_dict['category']
    campaign_convratio = int(campaign_dict['conversion_ratio'])
    campaign_period = campaign_dict['period']
    start_date = campaign_dict['start_date']

    offer_type = offer_dict['offer_type']
    offer_min_val = int(offer_dict['min_value'])
    offer_max_val = int(offer_dict['max_value'])
    offer_valid_till = offer_dict['valid_till']
    offer_mbr_issuance = offer_dict['member_issuance']

    campaign = CampaignData(name=campaign_name, money=campaign_money, category=campaign_category,
                            conversion_ratio=campaign_convratio, period=campaign_period,
                            offer_type=offer_type, max_per_member_issuance_frequency=offer_mbr_issuance, max_value=offer_max_val,
                            min_value=offer_min_val, valid_till=offer_valid_till, start_date=start_date)

    campaign.key = get_campaign_key(campaign_name)
    campaign_key = campaign.put()
    logging.info('campaign_key:: %s', campaign_key)

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)
    end_date = end_date.strftime("%Y-%m-%d")
    offer_name = campaign_name+"_OFR"
    offer = OfferData(surprise_points=10, threshold=10, OfferNumber=offer_name,
                      OfferPointsDollarName=offer_name, OfferDescription=offer_name,
                      OfferType="Xtreme Redeem", OfferSubType="Item", OfferStartDate=start_date,
                      OfferStartTime="00:00:00", OfferEndDate=end_date, OfferEndTime="23:59:00",
                      OfferBUProgram_BUProgram_BUProgramName="BU - Apparel",
                      OfferBUProgram_BUProgram_BUProgramCost=0.00, ReceiptDescription="TELL-16289",
                      OfferCategory="Stackable", OfferAttributes_OfferAttribute_Name="MULTI_TRAN_IND",
                      OfferAttributes_OfferAttribute_Values_Value="N", Rules_Rule_Entity="Product",
                      Rules_Conditions_Condition_Name="PRODUCT_LEVEL",
                      Rules_Conditions_Condition_Operator="IN",
                      Rules_Conditions_Condition_Values_Value="SEARSLEGACY~801~608~14~1~1~1~93059",
                      RuleActions_ActionID="ACTION-1", Actions_ActionID="ACTION-1",
                      Actions_ActionName="XR",
                      Actions_ActionProperty_PropertyType="Tier",
                      Actions_ActionProperty_Property_Name="MIN",
                      Actions_ActionProperty_Property_Values_Value="0.01",
                      created_at=created_time)
    offer.key = ndb.Key('OfferData', offer_name)
    offer.campaign = campaign.key
    offer_key = offer.put()

    sendEmail.offer_email(campaign_name)
    logging.info('offer created with key:: %s', offer_key)


class GetAllMembersHandler(webapp2.RequestHandler):
    def get(self):
        query = MemberData.query()
        member_list = query.fetch(10)
        result = []
        for member in member_list:
            result.append(member.to_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))


class ActivateOfferHandler(webapp2.RequestHandler):
    def get(self):
        offer_id = self.request.get('offer_id')
        logging.info("Request offer_id: " + offer_id)
        if offer_id is None or not offer_id:
            response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                             + "Please provide offer_id and member_id with the request</h3></body></html>"
            self.response.write(response_html)
            return

        member_id = self.request.get('member_id')
        logging.info("Request member_id: " + member_id)

        if member_id is None or not member_id:
            response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                             + "Please provide offer_id and member_id with the request</h3></body></html>"
            self.response.write(response_html)
            return

        offer_key = ndb.Key('OfferData', offer_id)
        member_key = ndb.Key('MemberData', member_id)
        # self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        logging.info("fetched offer_key and member key ")
        response_dict = dict()
        offer = offer_key.get()
        if offer is not None:
            logging.info("offer is not None")
            post_data = get_xml(offer).rstrip('\n')
            logging.info("post_data: %s", post_data)

            result = ActivateOfferHandler.create_offer(post_data)

            doc = ET.fromstring(result)
            status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
            if int(status_code) == 0:
                # Assuming one-to-one mapping with Member and Offer entities
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_key,
                                                         MemberOfferData.offer == offer_key).get()
                if member_offer_obj is not None:
                    member_offer_obj.status = True
                    member_offer_obj.put()
                else:
                    logging.error("Member Offer Object not found for offer key :: %s and member key:: %s",
                                  offer_key, member_key)

                logging.info("Activated offer %s for member %s", str(offer_key), str(member_key))
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer has been activated successfully"
            else:
                logging.error("Telluride call returned with error. Status:: %s, Status Text:: %s",
                              status_code, doc.find('.//{http://rewards.sears.com/schemas/}StatusText').text)
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer activation has failed!!!"
        else:
            logging.error("could not fetch offer details for key:: %s", offer_key)
            response_dict['message'] = "Sorry could not fetch offer details."
        response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                        + response_dict['message'] + "</h3></body></html>"
        self.response.write(response_html)

    @classmethod
    def create_offer(cls, data):
        logging.info('**** data: %s', data)
        url = 'esbqa-1080.searshc.com'

        # Fetch access token from memcache
        access_token = memcache.get(key="ACCESS_TOKEN")
        if access_token is None:
            logging.info('Got None access_token from memcache. Generating new token')
            # Generating new Access Token
            generated_access_token = ActivateOfferHandler.generateAccessToken()
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
            generated_access_token = ActivateOfferHandler.generateAccessToken()
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
    def generateAccessToken(cls):
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


class EmailOfferMembersHandler(BaseHandler):
    def get(self):
        campaign_id = self.request.get('campaign_id')

        obj = sendEmail.offer_email(campaign_id)
        self.response.out.write(json.dumps(obj))


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/saveCampaign', SaveCampaignHandler),
    ('/campaigns', GetAllCampaignsHandler),
    ('/members', GetAllMembersHandler),
    ('/activateOffer', ActivateOfferHandler),
    ('/emailMembers', EmailOfferMembersHandler)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()
