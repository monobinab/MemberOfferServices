import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
from models import CampaignData, MemberData, MemberOfferData, ndb, StoreData
from datastore import CampaignDataService, MemberOfferDataService, OfferDataService
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from utilities import create_pubsub_message, make_request
from datetime import datetime
import xml.etree.ElementTree as ET
import os


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
        self.response.write("member-offer-service")


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
        response_dict = dict()
        try:
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
            offer = offer_key.get()
            member = member_key.get()
            if offer is not None and member is not None:
                logging.info("offer is not None")
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_key,
                                                         MemberOfferData.offer == offer_key).get()
                if member_offer_obj is not None:

                    host = "telluride-service-" + os.environ.get('NAMESPACE') + "-dot-syw-offers.appspot.com/"
                    relative_url = str("registerMember?offer_id="+offer_id+"&&member_id="+member_id)
                    result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                    logging.info(json.loads(result))
                    result = json.loads(result).get('data')
                    logging.info(result)
                    doc = ET.fromstring(result)
                    if doc is not None:
                        status_code = int(doc.find('.//{http://www.epsilon.com/webservices/}Status').text)
                        logging.info("Status code:: %d" % status_code)
                        if status_code == 0:
                                member_offer_obj.status = True
                                member_offer_obj.activated_at = datetime.now()
                                member_offer_obj.put()
                                response_dict['message'] = "Offer has been activated successfully"
                        elif status_code == 1 or status_code == 99:
                            member_offer_obj.status = True
                            member_offer_obj.put()
                            response_dict['message'] = "Member already registered for this offer"
                        else:
                            logging.error("Telluride call failed.")
                            response_dict['message'] = "Sorry, Offer could not be activated"
                    else:
                        logging.error("Telluride call failed.")
                        response_dict['message'] = "Sorry, Offer could not be activated"
                else:
                    logging.error("Member Offer Object not found for offer key :: %s and member key:: %s",
                                  offer_key, member_key)

                    logging.info("Activated offer %s for member %s", str(offer_key), str(member_key))
                    response_dict['message'] = "Sorry, Offer could not be activated. Member Offer Object not found."
            else:
                logging.error("could not fetch offer or member details for key:: %s", offer_key)
                response_dict['message'] = "Sorry could not fetch member offer details."
        except httplib.HTTPException as exc:
            logging.error(exc)
            response_dict['message'] = "Sorry could not fetch offer details because of the request time out."
        response_html = "<html><head><title>Sears Offer Activation</title></head><body><h3> " \
                        + response_dict['message'] + "</h3></body></html>"
        self.response.write(response_html)



# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/members', GetAllMembersHandler),
    ('/activateOffer', ActivateOfferHandler),
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
