import sys
sys.path.insert(0, 'lib')
import logging
import webapp2

import json
from models import ndb
from datastore import OfferDataService
from sendEmail import send_mail


class IndexPageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("sendgrid-email-service")


class EmailOfferMembersHandler(webapp2.RequestHandler):
    def get(self):
        try:
            logging.info("Member id:: %s", self.request.get('member_id'))
            logging.info("Offer id:: %s", self.request.get('offer_id'))
            member_entity = ndb.Key('MemberData', self.request.get('member_id')).get()
            offer_entity = ndb.Key('OfferData', self.request.get('offer_id')).get()
            logging.info("Member :: %s", member_entity)
            logging.info("Offer :: %s", offer_entity)
            if member_entity is None or offer_entity is None:
                response_dict = {'status': 'Failure', 'message': "Details not found for the request"}
            else:
                campaign_entity = offer_entity.campaign.get()
                send_mail(member_entity=member_entity, offer_entity=offer_entity, campaign_entity=campaign_entity)
                response_dict = {'status': 'Success', 'message': "Offer email has been sent successfully!!!"}

        except Exception as e:
            logging.error(e)
            response_dict = {'status': 'Failure', 'message': "Server error has encountered an error"}

        finally:
            logging.info(response_dict)
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.headers['Content-type'] = 'application/json'
            self.response.write(json.dumps(response_dict))


class OfferDetailsHandler(webapp2.RequestHandler):
    def get(self):
        offer_value = self.request.get('offer')
        member_id = self.request.get('member')
        campaign_name = self.request.get('campaign')
        logging.info("Request parameters - offer, member, campaign received.")

        campaign_key = ndb.Key('CampaignData', campaign_name)
        logging.info("fetched campaign_key for: %s", campaign_name)
        campaign = campaign_key.get()
        if campaign is None:
            logging.info("campaign is None")
        logging.info("OfferDetailsHandler campaign :: %s", campaign)

        offer_name = "{}_{}".format(str(campaign.name), str(offer_value))
        offer_key = ndb.Key('OfferData', offer_name)
        logging.info("fetched offer_key")
        offer_entry = offer_key.get()
        if offer_entry is None:
            logging.info("OfferDetailsHandler - Offer is None")
        logging.info("OfferDetailsHandler offer :: %s", offer_entry)
        offer_entity = OfferDataService.create_offer_obj(campaign, offer_value)

        # HACK: Need to remove later. Only for testing purpose. <>
        member_id = '7081327663412819'
        member_key = ndb.Key('MemberData', member_id)
        logging.info("Fetched member_key for member: %s", member_id)
        member_entity = member_key.get()
        if member_entity is None:
            logging.info("member is None")
        logging.info("OfferDetailsHandler member :: %s", member_entity)

        campaign_entity = offer_entity.campaign.get()
        logging.info("OfferDetailsHandler campaign_entity :: %s", campaign_entity)

        send_mail(member_entity=member_entity, offer_entity=offer_entity, campaign_entity=campaign_entity)
        logging.info("Mail sent. ")

        result = {"data": "Mail sent successfully."}
        self.response.write(json.dumps(result))


app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    # ('/sendEmailJob', ModelDataSendEmailHandler),
    ('/emailMembers', EmailOfferMembersHandler),
    ('/offerDetails', OfferDetailsHandler)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()