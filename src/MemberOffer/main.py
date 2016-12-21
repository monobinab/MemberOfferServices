import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
from models import CampaignData, MemberData, MemberOfferData, ndb, StoreData
from datastore import CampaignDataService, MemberOfferDataService, OfferDataService
from googleapiclient.errors import HttpError
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
        member_list = query.fetch()
        result = list()

        for member in member_list:
            logging.info("Member :: %s", member.member_id)
            logging.info("Member key :: %s", member.key)
            each_dict = dict()
            each_dict['member_details'] = member.to_dict()
            each_dict['offer_details'] = dict()

            query = MemberOfferData.query(MemberOfferData.member == member.key)

            created_at_query = query.order(-MemberOfferData.created_at)
            latest_offer_created = created_at_query.fetch(1)
            if not latest_offer_created:
                each_dict['offer_details']['latest_offer_created'] = list()
                logging.info("No offer data associated with this member.")
            else:
                logging.info("latest offer created :: %s", latest_offer_created)
                each_dict['offer_details']['latest_offer_created'] = latest_offer_created[0].to_dict()
                logging.info("Added latest offer created information for the member.")

            updated_at_query = query.order(-MemberOfferData.updated_at)
            latest_offer_updated = updated_at_query.fetch(1)
            if not latest_offer_updated:
                each_dict['offer_details']['latest_offer_updated'] = list()
                logging.info("No offer data associated with this member.")
            else:
                logging.info("latest offer updated :: %s", latest_offer_updated)
                each_dict['offer_details']['latest_offer_updated'] = latest_offer_updated[0].to_dict()
                logging.info("Added latest offer updated information for the member.")

            result.append(each_dict)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(result)


class MemberDetailsHandler(webapp2.RequestHandler):
    def get(self):
        # TODO : handle multiple members. Use a list of members
        member_id = self.request.get('member_id')
        member = MemberData.get_by_id(member_id)
        logging.info("Member object :: %s", member)
        self.response.write(list(member.to_dict()))

        # Member.IsMember()(deprioritized)
        # Member.IsIssued()
        # Member.IsEmailOptedIn()
        # Member.HasOfferFromModel()
        # Member.HasTransactionInBUPast3Days(BU_Name)(deprioritized)
        # Member.HasCurrentTransactionInBU(BU_Name)(deprioritized)
        # Offer.IsExpired()
        # Offer.Activated()
        # Offer.IsExpiringIn3Days()


class ActivateOfferHandler(webapp2.RequestHandler):
    def get(self):
        response_dict = dict()
        try:
            offer_id = self.request.get('offer_id')
            logging.info("Request offer_id: " + offer_id)
            if offer_id is None:
                response_html = """<html><head><title>Sears Offer Activation</title></head><body><h3>
                                Please provide offer_id and member_id with the request</h3></body></html>"""
                self.response.write(response_html)
                return

            member_id = self.request.get('member_id')
            logging.info("Request member_id: " + member_id)

            if member_id is None:
                response_html = """<html><head><title>Sears Offer Activation</title></head><body><h3>
                                Please provide offer_id and member_id with the request</h3></body></html>"""
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
                    relative_url = str("registerMember?offer_id=" + offer_id + "&&member_id=" + member_id)
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


class SendOfferToMemberHandler:
    # TODO: Make response consitent with other api's as well
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        member_id = self.request.get('member_id')
        offer_value = self.request.get('offer_value')
        campaign_name = self.request.get('campaign_name')
        channel = "EMAIL"

        if member_id is None or offer_value is None or campaign_name is None:
            response_html = """<html><head><title>Batch Job Execution</title></head><body><h3> Please provide
                            member_id, offer_value and campaign_name with the request</h3></body></html>"""

            self.response.write(response_html)

        else:
            response = self.process_data(member_id, offer_value, campaign_name, channel)
            self.response.write(json.dumps(response))

    def process_data(self, member_id, offer_value, campaign_name, channel):
        response_dict = dict()
        campaign_key = ndb.Key('CampaignData', campaign_name)
        logging.info("fetched campaign_key for: %s", campaign_name)
        campaign = campaign_key.get()

        if campaign is None:
            logging.info("campaign is None")
            response_dict['message'] = "Error: Campaign not found"
            return response_dict
        else:
            logging.info("campaign is not None")
            try:
                success_msg = "Offer email sent successfully"
                response_dict['message'] = ""
                logging.info('campaign_name: %s , member_id: %s, offer_value: %s', campaign_name, member_id, offer_value)

                offer_name = "{}_{}".format(str(campaign.name), str(offer_value))

                offer_key = ndb.Key('OfferData', offer_name)
                logging.info("fetched offer_key")
                offer_entry = offer_key.get()

                if offer_entry is None:
                    logging.info("Offer is None")
                    response_dict['message'] = "Error: Offer not found"
                    return response_dict
                else:
                    logging.info('Offer is not None. Sending email for Offer: %s', offer_name)
                    offer = OfferDataService.create_offer_obj(campaign, offer_value)

                    # HACK: Need to remove later. Only for testing purpose. <>
                    member_id = '7081327663412819'

                    member_key = ndb.Key('MemberData', member_id)
                    logging.info("Fetched member_key for member: %s", member_id)

                    member = member_key.get()
                    if member is None:
                        logging.info("member is None")
                        response_dict['message'] = "Member ID " + member_id + " not found in datastore"
                        return response_dict
                    else:
                        campaign_entity = offer.campaign.get()

                        # send_mail(member_entity=member, offer_entity=offer,
                        #           campaign_entity=campaign_entity)

                        host = "email-service-" + os.environ.get('NAMESPACE') + "-dot-syw-offers.appspot.com/"
                        relative_url = str("offerDetails?offer=" + offer_value + "&&member=" + member_id + "&&campaign=" + campaign_name)
                        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                        logging.info("email service call result :: %s", result)

                        member_offer_data_key = MemberOfferDataService.create(offer, member, channel)

                        logging.info('member_offer_key:: %s', member_offer_data_key)
                        logging.info('Offer %s email has been sent to:: %s', offer.OfferNumber, member.email)
                        response_dict['message'] = success_msg

            except HttpError as err:
                print('Error: {}'.format(err.content))
                logging.error('Error: {}'.format(err.content))
                response_dict['message'] = "HttpError exception: " + err.content
                raise err

        logging.info('response_dict[message]: %s', response_dict['message'])
        return response_dict


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/members', GetAllMembersHandler),
    ('/getMember', MemberDetailsHandler),
    ('/activateOffer', ActivateOfferHandler),
    ('/sendOffer', SendOfferToMemberHandler),
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
