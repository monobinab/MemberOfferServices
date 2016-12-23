import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
from models import ndb, OfferData, CampaignData
from telluride_service import TellurideService
from google.appengine.api import namespace_manager


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
        self.response.write("telluride-backend-service")


class SaveCampaignHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            logging.info("Namespace:: %s", namespace_manager.get_namespace())
            campaign_id = self.request.get('campaign_id')
            logging.info("Campaign ID:: " + campaign_id)
            campaign = CampaignData.get_by_id(id=campaign_id, use_datastore=True, use_memcache=False, use_cache=False)
            logging.info("Campaign Key:: %s", campaign.key)
            logging.info("Campaign Fetched:: %s", campaign)
            offer_list = OfferData.query(OfferData.campaign == campaign.key).fetch()
            logging.info("Number of Offers fetched from datastore :: %d", len(offer_list))
            result_list = list()
            for offer in offer_list:
                result = TellurideService.create_offer(offer=offer)
                result['offer_id'] = offer.OfferNumber
                result_list.append(result)
            self.response.write(json.dumps({'data': result_list}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write(json.dumps({'data': "Request has timed out. Please try again."}))
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write(json.dumps({'data': "Internal Server Error"}))


class CreateOfferHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            offer_id = self.request.get('offer_id')
            logging.info("Offer ID:: " + offer_id)
            offer = OfferData.get_by_id(id=offer_id)
            result = TellurideService.create_offer(offer=offer)
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write(json.dumps({'data': "Request has timed out. Please try again."}))
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write(json.dumps({'data': "Internal Server Error"}))


class ActivateOfferHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            logging.info("Namespace:: %s", namespace_manager.get_namespace())
            offer_id = self.request.get('offer_id')
            member_id = self.request.get('member_id')
            logging.info(offer_id + " -------- " + member_id)
            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)
            offer = offer_key.get(use_datastore=True, use_memcache=False, use_cache=False)
            member = member_key.get(use_datastore=True, use_memcache=False, use_cache=False)
            result = TellurideService.register_member(offer, member)
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write("Request has timed out. Please try again.")
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write("Internal Server Error")


class BalanceHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            result = TellurideService.get_balance()
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write(json.dumps({'data': "Request has timed out. Please try again."}))
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write(json.dumps({'data': "Internal Server Error"}))


class RedeemOfferHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            result = TellurideService.redeem_offer()
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write(json.dumps({'data': "Request has timed out. Please try again."}))
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write(json.dumps({'data': "Internal Server Error"}))


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/createCampaign', SaveCampaignHandler),
    ('/registerMember', ActivateOfferHandler),
    ('/getBalance', BalanceHandler),
    ('/redeemOffer', RedeemOfferHandler),
    ('/createOffer', CreateOfferHandler)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()