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


DEFAULT_CAMPAIGN_NAME = 'default_campaign'
ACCESS_TOKEN = '038f658bb152e08ce0f2148fffac2a75244178608ac9c273a10c1950b230fd47'


def get_campaign_key(campaign_name=DEFAULT_CAMPAIGN_NAME):
    return ndb.Key('CampaignData', campaign_name)


class IndexPageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("CAMPAIGN-BACKEND-SERVICE")


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
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        # Check for create new entity or update an existing entity
        if is_entity is None:
            save_campaign(json_data, datetime.now())
        else:
            save_campaign(json_data, is_entity.created_at)
        # self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        # self.response.write({'message': 'Campaign created successfullly!!!'})


class GetAllCampaignsHandler(webapp2.RequestHandler):
    def get(self):
        query = CampaignData.query()
        entity_list = query.fetch(100)
        # logging.info(entity_list)
        # logging.info(query)
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

    offer_type = offer_dict['offer_type']
    offer_min_val = int(offer_dict['min_value'])
    offer_max_val = int(offer_dict['max_value'])
    offer_valid_till = offer_dict['valid_till']
    offer_mbr_issuance = offer_dict['member_issuance']

    campaign = CampaignData(name=campaign_name, money=campaign_money, category=campaign_category,
                            conversion_ratio=campaign_convratio, period=campaign_period,
                            offer_type=offer_type, max_per_member_issuance_frequency=offer_mbr_issuance, max_value=offer_max_val,
                            min_value=offer_min_val, valid_till=offer_valid_till)

    campaign.key = get_campaign_key(campaign_name)
    campaign_key = campaign.put()
    logging.info('campaign_key:: %s', campaign_key)

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)
    end_date = end_date.strftime("%Y-%m-%d")
    offer = OfferData(surprise_points=10, threshold=10, OfferNumber=campaign_name+"_OFFER",
                      OfferPointsDollarName="test 101", OfferDescription="test 101",
                      OfferType="Xtreme Redeem", OfferSubType="Items", OfferStartDate=start_date,
                      OfferStartTime="00:00:00", OfferEndDate=end_date, OfferEndTime="23:59:00",
                      OfferBUProgram_BUProgram_BUProgramName="BU - Apparel",
                      OfferBUProgram_BUProgram_BUProgramCost=0.00, ReceiptDescription="TELL-16289",
                      OfferCategory="Stackable", OfferAttributes_OfferAttribute_Name="MULTI_TRAN_IND",
                      OfferAttributes_OfferAttribute_Values_Value="N", Rules_Rule_Entity="Location",
                      Rules_Conditions_Condition_Name="STORE_LOCATION",
                      Rules_Conditions_Condition_Operator="EQUALS",
                      Rules_Conditions_Condition_Values_Value="OrderLocation",
                      RuleActions_ActionID="ACTION-1", Actions_ActionID="ACTION-1",
                      Actions_ActionName="EARN",
                      Actions_ActionProperty_PropertyType="Tier",
                      Actions_ActionProperty_Property_Name="MIN",
                      Actions_ActionProperty_Property_Values_Value="1",
                      created_at=created_time)
    offer.key = ndb.Key('OfferData', campaign_name+"_OFFER")
    offer.campaign = campaign.key
    offer_key = offer.put()

    sendEmail.offer_email(campaign_name)

    # for member in MemberData.query().fetch():
    #     member_offer_data = MemberOfferData(offer=offer.key, member=member.key)
    #     member_offer_data.key = ndb.key('MemberOfferData')
    #     member_offer_data.status = "PENDING"
    #     member_offer_data.put()

    logging.info('offer_key:: %s', offer_key)


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
        member_id = self.request.get('member_id')
        offer = ndb.Key('OfferData', offer_id).get()
        member = ndb.Key('MemberData', member_id).get()
        # self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        response_dict = dict()
        if offer is not None:
            post_data = get_xml(offer).rstrip('\n')
            logging.info(post_data)

            result = ActivateOfferHandler.create_offer(post_data)

            doc = ET.fromstring(result)
            status_code = doc.find('.//{http://rewards.sears.com/schemas/}Status').text
            if int(status_code) == 0:
                # Assuming one-to-one mapping with Member and Offer entities
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member.key,
                                                         MemberOfferData.offer == offer.key).get()
                member_offer_obj.status = True
                member_offer_obj.put()

                logging.info("Activated offer " + offer.key.id() + " for member " + member.email)
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer has been activated successfully"
            else:
                response_dict['data'] = str(result)
                response_dict['message'] = "Offer activation has failed!!!"
        else:
            response_dict['message'] = "Sorry could not fetch offer details."
        response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                        + response_dict['message'] + "</h3></body></html>"
        self.response.write(response_html)

    @classmethod
    def create_offer(cls, data):
        logging.info('**** data: %s', data)
        url = 'esbqa-1080.searshc.com'
        access_token = ACCESS_TOKEN
        # headers = {'client_id': 'OFFER_REC_SYS_QA', 'access_token': access_token,
        # 'content-type': 'application/xml'}

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

        return result


class EmailOfferMembersHandler(webapp2.RequestHandler):
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
