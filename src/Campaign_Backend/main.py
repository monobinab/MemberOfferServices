import json
import logging
from datetime import datetime
import webapp2
from models import CampaignData, MemberData, MemberOfferData, FrontEndData, ndb
from datastore import CampaignDataService
from telluride_service import TellurideService


class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        self.response.write('An error occurred.')
        logging.exception(self, exception, debug)

        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)


class IndexPageHandler(BaseHandler):
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
        # Check for create new entity or update an existing entity
        if is_entity is None:
            CampaignDataService.save_campaign(json_data, datetime.now())
        else:
            CampaignDataService.save_campaign(json_data, is_entity.created_at)

        self.response.headers['Access-Control-Allow-Origin'] = '*'


class GetAllCampaignsHandler(webapp2.RequestHandler):
    def get(self):
        query = CampaignData.query().order(-CampaignData.created_at)
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
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        logging.info("fetched offer_key and member key ")
        response_dict = dict()
        offer = offer_key.get()
        member = member_key.get()
        if offer is not None and member is not None:
            logging.info("offer is not None")

            status_code = TellurideService.register_member(offer, member)
            logging.info("Status code:: %d" % status_code)
            if status_code == 0:
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_key,
                                                         MemberOfferData.offer == offer_key).get()
                if member_offer_obj is not None:
                    member_offer_obj.status = True
                    member_offer_obj.put()
                    response_dict['message'] = "Offer has been activated successfully"
                else:
                    logging.error("Telluride call failed.")
                    response_dict['message'] = "Sorry, Offer could not be activated"
            elif status_code == 1 or status_code == 99:
                response_dict['message'] = "Member already registered for this offer"
            else:
                logging.error("Member Offer Object not found for offer key :: %s and member key:: %s",
                              offer_key, member_key)

                logging.info("Activated offer %s for member %s", str(offer_key), str(member_key))
                # response_dict['data'] = str(result)
                response_dict['message'] = "Sorry, Offer could not be activated."
        else:
            logging.error("could not fetch offer or member details for key:: %s", offer_key)
            response_dict['message'] = "Sorry could not fetch offer details."
        response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                        + response_dict['message'] + "</h3></body></html>"
        self.response.write(response_html)


class EmailOfferMembersHandler(BaseHandler):
    def get(self):
        # campaign_id = self.request.get('campaign_id')
        # obj = sendEmail.offer_email(campaign_id)
        # self.response.out.write(json.dumps(obj))
        pass


class UIListItemsHandler(webapp2.RequestHandler):
    def get(self):
        key = ndb.Key('FrontEndData', '1')
        result = key.get()
        result_dict = dict()
        result_dict['categories'] = list(result.Categories)
        result_dict['offer_type'] = list(result.Offer_Type)
        result_dict['conversion_ratio'] = list(result.Conversion_Ratio)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result_dict}))


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/saveCampaign', SaveCampaignHandler),
    ('/campaigns', GetAllCampaignsHandler),
    ('/members', GetAllMembersHandler),
    ('/activateOffer', ActivateOfferHandler),
    ('/emailMembers', EmailOfferMembersHandler),
    ('/getListItems', UIListItemsHandler)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()
