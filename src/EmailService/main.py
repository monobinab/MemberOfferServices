import sys
sys.path.insert(0, 'lib')
import logging
import webapp2
import json
from models import CampaignData, MemberData, MemberOfferData, ndb, OfferData
from datastore import MemberOfferDataService, OfferDataService
from sendEmail import send_mail
from googleapiclient.errors import HttpError
import os


class IndexPageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("email-service")


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
        response_offer = dict()
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
                    offer = OfferDataService.create_offer_obj(campaign, offer_value, "")

                    # HACK: Need to remove later. Only for testing purpose. <>
                    if os.environ['NAMESPACE'] in ['qa', 'dev']:
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

                        # send_mail(member_entity=member, offer_entity=offer)
                        member_offer_data_key = MemberOfferDataService.create(offer_entity=offer,
                                                                              member_entity=member,
                                                                              channel=channel.upper(),
                                                                              reg_start_date=offer.OfferStartDate,
                                                                              reg_end_date=offer.OfferEndDate,
                                                                              offer_id=campaign_name+"_"+offer_value,
                                                                              member_id=member_id)

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

app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/sendEmailJob', ModelDataSendEmailHandler)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
