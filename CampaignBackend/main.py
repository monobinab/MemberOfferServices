import datetime
import time
import json
import logging
from datetime import datetime
import webapp2
from models import CampaignData, OfferData, MemberData, MemberOfferData, ndb


DEFAULT_CAMPAIGN_NAME = 'default_campaign'


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
            offer = OfferData.query(OfferData.campaign==each_entity.key).get()
            campaign_dict['campaign_id'] = each_entity.key.id()
            campaign_dict['name'] = each_entity.name
            campaign_dict['money'] = each_entity.money
            campaign_dict['category'] = each_entity.category
            campaign_dict['conversion_ratio'] = each_entity.conversion_ratio
            campaign_dict['period'] = each_entity.period

            offer_dict['offer_id'] = offer.key.id()
            offer_dict['offer_type'] = offer.offer_type
            offer_dict['min_value'] = offer.min_value
            offer_dict['max_value'] = offer.max_value
            offer_dict['valid_till'] = offer.valid_till
            offer_dict['member_issuance'] = offer.max_per_member_issuance_frequency
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
                            conversion_ratio=campaign_convratio, period=campaign_period)

    campaign.key = get_campaign_key(campaign_name)
    campaign_key = campaign.put()
    logging.info('campaign_key:: %s', campaign_key)

    offer = OfferData(offer_number="10", offer_points="10", surprise_points=10, threshold=10,
                      offer_type=offer_type, max_per_member_issuance_frequency=offer_mbr_issuance,
                      max_value=offer_max_val, min_value=offer_min_val, valid_till=offer_valid_till,
                      created_at=created_time)
    offer.key = ndb.Key('OfferData', int(time.time()))
    offer.campaign = campaign.key
    offer_key = offer.put()
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


class EmailOfferMembersHandler(webapp2.RequestHandler):
    def post(self):
        pass


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/saveCampaign', SaveCampaignHandler),
    ('/campaigns', GetAllCampaignsHandler),
    ('/members', GetAllMembersHandler),
    ('/emailMembers', EmailOfferMembersHandler)], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()
