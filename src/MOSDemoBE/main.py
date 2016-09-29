import webapp2
import sys
import httplib
import logging
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import datetime
import json
import time
from time import gmtime, strftime
from datetime import datetime

DEFAULT_CAMPAIGN_NAME = 'default_campaign'

def campaign_key(campaign_name=DEFAULT_CAMPAIGN_NAME):
	return ndb.Key('Campaign_Data', campaign_name)

class Campaign_Data(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    #owner = ndb.StringProperty(indexed=False)
    money = ndb.IntegerProperty(indexed=False)
    category = ndb.StringProperty(indexed=True)
    conversion_ratio = ndb.IntegerProperty(indexed=False)
    period = ndb.StringProperty(indexed=False)
    offer_type = ndb.StringProperty(indexed=True)
    max_per_member_issuance_frequency = ndb.StringProperty(indexed=False)
    max_value = ndb.IntegerProperty(indexed=False)
    min_value = ndb.IntegerProperty(indexed=False)
    valid_till = ndb.StringProperty(indexed=False)
    created_at = ndb.DateTimeProperty(indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now_add=True)
	
    @classmethod
    def get_all_campaigns(cls):
        return cls.query().fetch(10, offset=0)



class Save(webapp2.RequestHandler):
    def get(self):
        offerdata = self.request.get('offer_data')
        logging.info('****offerdata: %s', offerdata)
        jsondata = json.loads(offerdata)
        campaign_dict = jsondata['campaign_details']
        campaign_name = campaign_dict['name']
        is_entity = ndb.Key('Campaign_Data', campaign_name).get()
        logging.info('is_entity: %s',is_entity)
        logging.info('type is_entity: %s',type (is_entity))

        #Check for create new entity or update an existing entity
        if is_entity is None:
            savecampaign(jsondata,datetime.now())
        else:
            savecampaign(jsondata,is_entity.created_at)


class GetAll(webapp2.RequestHandler):
	def get(self):
		campaign_name = self.request.get('campaign_name', DEFAULT_CAMPAIGN_NAME)
		query = Campaign_Data.query()
		entity_list = query.fetch(10)
		#logging.info(entity_list)
		#logging.info(query)
		result = list()
		logging.info('len of the list: %s',len(entity_list))
		for each in entity_list:
			key = ndb.Key('Campaign_Data', each.name)
			each_entity = key.get()
			campaign_dict = dict()
			offer_dict = dict()

			campaign_dict['name'] = each_entity.name 
			campaign_dict['money'] = each_entity.money
			campaign_dict['category'] = each_entity.category 
			campaign_dict['conversion_ratio'] = each_entity.conversion_ratio
			campaign_dict['period'] = each_entity.period

			offer_dict['offer_type'] = each_entity.offer_type
			offer_dict['min_value'] = each_entity.min_value
			offer_dict['max_value'] = each_entity.max_value
			offer_dict['valid_till'] = each_entity.valid_till
			offer_dict['member_issuance'] = each_entity.max_per_member_issuance_frequency
			each_dict= dict()
			each_dict['campaign_details'] = campaign_dict
			each_dict['offer_details'] = offer_dict
			result.append(each_dict)
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps({'data':result}))
			
def savecampaign(jsondata,createdtime):
    #{"offer_details":{"offer_type":"Liquidly Injection","min_value":"1","max_value":"2","valid_till":"2016-09-22","member_issuance":"2 per week"},
    #"campaign_details":{"name":"effwff","money":"500","category":"Approval","conversion_ratio":"5","period":"1 Weeks"}}
    campaign_dict = jsondata['campaign_details']
    offer_dict = jsondata['offer_details']

    campaign_name = campaign_dict['name']
    campaign_money = int(campaign_dict['money'])
    campaign_category = campaign_dict['category']
    campaign_convratio = int(campaign_dict['conversion_ratio'])
    campaign_period = campaign_dict['period']

    offer_type = offer_dict['offer_type']
    offer_minval = int(offer_dict['min_value'])
    offer_maxval = int(offer_dict['max_value'])
    offer_validtill = offer_dict['valid_till']
    offer_mbrissuance = offer_dict['member_issuance']

    campaign = Campaign_Data(name = campaign_name,money = campaign_money,category = campaign_category,
    conversion_ratio = campaign_convratio,period = campaign_period,
    offer_type = offer_type,max_per_member_issuance_frequency = offer_mbrissuance,
    max_value = offer_maxval,min_value = offer_minval,
    valid_till = offer_validtill,created_at = createdtime
    )

    campaign.key = ndb.Key('Campaign_Data', campaign_name)
    campaign_key = campaign.put()
    logging.info('campaign_key:: %s', campaign_key)

# [START app]
app = webapp2.WSGIApplication([
    ('/savecampaign', Save),
	('/getAllCampaign', GetAll)], debug=True)
# [END app]

def main():
    app.run()

if __name__=='__main__':
    main()
