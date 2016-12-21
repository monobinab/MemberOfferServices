import sys
sys.path.insert(0, 'lib')
import logging
import webapp2

import json
from models import CampaignData, MemberData, MemberOfferData, ndb, OfferData
from datastore import MemberOfferDataService, OfferDataService
from sendEmail import send_mail
from googleapiclient.errors import HttpError


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


# TODO : this is implemented in memberoffer microservice, all datastore operations should be removed from here
class ModelDataSendEmailHandler(webapp2.RequestHandler):
    def get(self):
        if self.request.get('member_id') is None or not self.request.get('member_id') or self.request.get('offer_value') is None or not self.request.get('offer_value') or self.request.get('campaign_name') is None or not self.request.get('campaign_name') :
            response_html = "<html><head><title>Batch Job Execution</title></head><body><h3> Please provide " \
                            "member_id, offer_value and campaign_name with the request</h3></body></html>"

            self.response.write(response_html)
            return

        member_id = self.request.get('member_id')
        offer_value = self.request.get('offer_value')
        campaign_name = self.request.get('campaign_name')
        channel = "EMAIL"

        response = self.process_data(member_id, offer_value, campaign_name, channel)

        self.response.write(response['message'])

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
                offer_name = "%s_%s" % (str(campaign.name), str(offer_value))

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
                        send_mail(member_entity=member, offer_entity=offer,
                                  campaign_entity=campaign_entity)

                        member_offer_data_key = MemberOfferDataService.create(offer, member, channel)

                        logging.info('member_offer_key:: %s', member_offer_data_key)
                        logging.info('Offer %s email has been sent to:: %s', offer.OfferNumber, member.email)
                        response_dict['message'] = "Success"

            except HttpError as err:
                print('Error: {}'.format(err.content))
                logging.error('Error: {}'.format(err.content))
                response_dict['message'] = "HttpError exception: " + err.content
                raise err

        logging.info('response_dict[message]: %s', response_dict['message'])
        return response_dict


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
        logging.info("OfferDetailsHandler camaign_entity :: %s", campaign_entity)

        send_mail(member_entity=member_entity, offer_entity=offer_entity, campaign_entity=campaign_entity)
        logging.info("Mail sent. ")

        result = {"data": "Mail sent successfully."}
        self.response.write(json.dumps(result))


app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/sendEmailJob', ModelDataSendEmailHandler),
    ('/emailMembers', EmailOfferMembersHandler),
    ('/offerDetails', OfferDetailsHandler)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()