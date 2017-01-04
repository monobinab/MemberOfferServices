import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
from models import CampaignData, MemberData, MemberOfferData, ndb, StoreData
from datastore import CampaignDataService, MemberOfferDataService, OfferDataService
from googleapiclient.errors import HttpError
from utilities import create_pubsub_message, make_request, get_telluride_host, get_email_host
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


class AllMemberOffers(webapp2.RequestHandler):
    def get(self):
        query = MemberData.query()
        member_list = query.fetch()
        result = list()

        for member in member_list:
            logging.info("Member :: %s", member.member_id)
            member_dict = dict()
            member_dict['member_details'] = member.to_dict()
            member_dict['offer_details'] = dict()

            query = MemberOfferData.query(MemberOfferData.member == member.key)

            issuance_date_query = query.order(-MemberOfferData.issuance_date)
            latest_offer_issued = issuance_date_query.fetch(1)
            if not latest_offer_issued:
                member_dict["offer_details"]["latest_offer_issued"] = list()
                logging.info("No offer data associated with this member.")
            else:
                logging.info("latest offer issued :: %s", latest_offer_issued)
                for item in latest_offer_issued:
                    issued_offer = dict()
                    issued_offer["member"] = item.member.id()
                    issued_offer["status"] = item.status if item.status is not None else 0
                    issued_offer["offer"] = item.offer.id()
                    issued_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                        item.issuance_date is not None else None

                    issued_offer["activation_date"] = item.activation_date.strftime('%Y-%m-%d %H:%m') if \
                        item.activation_date is not None else None

                    issued_offer["user_action_date"] = item.user_action_date.strftime('%Y-%m-%d %H:%m') if \
                        item.user_action_date is not None else None

                    issued_offer["validity_end_date"] = item.validity_end_date.strftime('%Y-%m-%d %H:%m') if \
                        item.validity_end_date is not None else None

                    issued_offer["redeemed_date"] = item.redeemed_date.strftime('%Y-%m-%d %H:%m') if \
                        item.redeemed_date is not None else None

                    issued_offer["redeemed"] = item.redeemed
                    issued_offer["validity_start_date"] = item.validity_start_date.strftime('%Y-%m-%d %H:%m') if \
                        item.validity_start_date is not None else None

                    issued_offer["activated_channel"] = item.activated_channel
                    issued_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                        item.issuance_date is not None else None
                    issued_offer["issuance_channel"] = str(item.issuance_channel)

                    offer = item.offer.get()
                    campaign = offer.campaign.get()
                    logging.info("Campaign :: %s ", campaign.to_dict())
                    issued_offer["offer_value"] = offer.surprise_points
                    issued_offer["category"] = campaign.category

                    logging.info("Added latest offer issued information for the member."
                                 "Offer details dict :: %s", issued_offer)
                    member_dict["offer_details"]["latest_offer_issued"] = issued_offer


            user_action_query = query.order(-MemberOfferData.user_action_date)
            latest_offer_updated = user_action_query.fetch(1)
            if not latest_offer_updated:
                member_dict["offer_details"]["latest_offer_updated"] = list()
                logging.info("No offer data associated with this member.")
            else:
                logging.info("latest offer updated :: %s", latest_offer_updated)
                for item in latest_offer_updated:
                    updated_offer = dict()
                    updated_offer["member"] = item.member.id()
                    updated_offer["status"] = item.status if item.status is not None else 0
                    updated_offer["offer"] = item.offer.id()
                    updated_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                        item.issuance_date is not None else None

                    updated_offer["activation_date"] = item.activation_date.strftime('%Y-%m-%d %H:%m') if \
                        item.activation_date is not None else None

                    updated_offer["user_action_date"] = item.user_action_date.strftime('%Y-%m-%d %H:%m') if \
                        item.user_action_date is not None else None

                    updated_offer["validity_end_date"] = item.validity_end_date.strftime('%Y-%m-%d %H:%m') if \
                        item.validity_end_date is not None else None

                    updated_offer["redeemed_date"] = item.redeemed_date.strftime('%Y-%m-%d %H:%m') if \
                        item.redeemed_date is not None else None

                    updated_offer["redeemed"] = item.redeemed
                    updated_offer["validity_start_date"] = item.validity_start_date.strftime('%Y-%m-%d %H:%m') if \
                        item.validity_start_date is not None else None

                    updated_offer["activated_channel"] = item.activated_channel
                    updated_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                        item.issuance_date is not None else None
                    updated_offer["issuance_channel"] = str(item.issuance_channel)

                    offer = item.offer.get()
                    campaign = offer.campaign.get()
                    logging.info("Campaign :: %s ", campaign.to_dict())
                    issued_offer["offer_value"] = offer.surprise_points
                    issued_offer["category"] = campaign.category

                    logging.info("Added latest offer issued information for the member."
                                 "Offer details dict :: %s", updated_offer)
                    member_dict["offer_details"]["latest_offer_updated"] = updated_offer

            result.append(member_dict)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({"data": result}))


class SingleMemberOffer(webapp2.RequestHandler):
    def get(self):
        member_id = self.request.get('member_id')
        member = MemberData.get_by_id(member_id)

        if member is None:
            result = {"data": "That member does not exist!"}
            self.response.write(json.dumps(result))
            return

        logging.info("Member object :: %s", member)
        result = list()
        member_dict = dict()

        member_dict["member_details"] = member.to_dict()
        member_dict["offer_details"] = dict()

        query = MemberOfferData.query(MemberOfferData.member == member.key)

        issuance_date_query = query.order(-MemberOfferData.issuance_date)
        latest_offer_issued = issuance_date_query.fetch(1)
        if not latest_offer_issued:
            member_dict["offer_details"]["latest_offer_issued"] = list()
            logging.info("No offer data associated with this member.")
        else:
            logging.info("latest offer issued :: %s", latest_offer_issued)
            for item in latest_offer_issued:
                issued_offer = dict()
                issued_offer["member"] = item.member.id()
                issued_offer["status"] = item.status if item.status is not None else 0
                issued_offer["offer"] = item.offer.id()
                issued_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                    item.issuance_date is not None else None

                issued_offer["activation_date"] = item.activation_date.strftime('%Y-%m-%d %H:%m') if \
                    item.activation_date is not None else None

                issued_offer["user_action_date"] = item.user_action_date.strftime('%Y-%m-%d %H:%m') if \
                    item.user_action_date is not None else None

                issued_offer["validity_end_date"] = item.validity_end_date.strftime('%Y-%m-%d %H:%m') if \
                    item.validity_end_date is not None else None

                issued_offer["redeemed_date"] = item.redeemed_date.strftime('%Y-%m-%d %H:%m') if \
                    item.redeemed_date is not None else None

                issued_offer["redeemed"] = item.redeemed
                issued_offer["validity_start_date"] = item.validity_start_date.strftime('%Y-%m-%d %H:%m') if \
                    item.validity_start_date is not None else None

                issued_offer["activated_channel"] = item.activated_channel
                issued_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                    item.issuance_date is not None else None
                issued_offer["issuance_channel"] = str(item.issuance_channel)

                offer = item.offer.get()
                campaign = offer.campaign.get()
                logging.info("Campaign :: %s ", campaign.to_dict())
                issued_offer["offer_value"] = offer.surprise_points
                issued_offer["category"] = campaign.category

                logging.info("Added latest offer issued information for the member."
                             "Offer details dict :: %s", issued_offer)
                member_dict["offer_details"]["latest_offer_issued"] = issued_offer

        user_action_query = query.order(-MemberOfferData.user_action_date)
        latest_offer_updated = user_action_query.fetch(1)
        if not latest_offer_updated:
            member_dict["offer_details"]["latest_offer_updated"] = list()
            logging.info("No offer data associated with this member.")
        else:
            logging.info("latest offer updated :: %s", latest_offer_updated)
            for item in latest_offer_updated:
                updated_offer = dict()
                updated_offer["member"] = item.member.id()
                updated_offer["status"] = item.status if item.status is not None else 0
                updated_offer["offer"] = item.offer.id()
                updated_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                    item.issuance_date is not None else None

                updated_offer["activation_date"] = item.activation_date.strftime('%Y-%m-%d %H:%m') if \
                    item.activation_date is not None else None

                updated_offer["user_action_date"] = item.user_action_date.strftime('%Y-%m-%d %H:%m') if \
                    item.user_action_date is not None else None

                updated_offer["validity_end_date"] = item.validity_end_date.strftime('%Y-%m-%d %H:%m') if \
                    item.validity_end_date is not None else None

                updated_offer["redeemed_date"] = item.redeemed_date.strftime('%Y-%m-%d %H:%m') if \
                    item.redeemed_date is not None else None

                updated_offer["redeemed"] = item.redeemed
                updated_offer["validity_start_date"] = item.validity_start_date.strftime('%Y-%m-%d %H:%m') if \
                    item.validity_start_date is not None else None

                updated_offer["activated_channel"] = item.activated_channel
                updated_offer["issuance_date"] = item.issuance_date.strftime('%Y-%m-%d %H:%m') if \
                    item.issuance_date is not None else None
                updated_offer["issuance_channel"] = str(item.issuance_channel)

                offer = item.offer.get()
                campaign = offer.campaign.get()
                logging.info("Campaign :: %s ", campaign.to_dict())
                updated_offer["offer_value"] = offer.surprise_points
                updated_offer["category"] = campaign.category

                logging.info("Added latest offer issued information for the member."
                             "Offer details dict :: %s", updated_offer)
                member_dict["offer_details"]["latest_offer_updated"] = updated_offer

        result.append(member_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({"data": result}))


class ActivateEmailOffer(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        response_dict = dict()
        try:
            offer_id = self.request.get('offer_id')
            logging.info("Request offer_id: " + offer_id)
            member_id = self.request.get('member_id')
            logging.info("Request member_id: " + member_id)

            if not offer_id or not member_id:
                response_dict['message'] = "Please provide offer_id and member_id with the request"
                self.response.write(json.dumps(response_dict))
                return

            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)
            if offer_key is None:
                result = {"data": "Invalid offer!"}
                self.response.write(json.dumps(result))
                return
            if member_key is None:
                result = {"data": "That member does not exist!"}
                self.response.write(json.dumps(result))
                return

            logging.info("fetched offer_key and member key ")

            offer = offer_key.get()
            member = member_key.get()
            if offer is not None and member is not None:
                logging.info("offer is not None")
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_key,
                                                         MemberOfferData.offer == offer_key).get()

                if member_offer_obj is not None:
                    host = get_telluride_host()
                    relative_url = str("registerMember?offer_id=" + offer_id + "&&member_id=" + member_id)
                    logging.info("Telluride URL :: %s, %s", host, relative_url)
                    result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                    logging.info(json.loads(result))
                    result = json.loads(result).get('data')
                    logging.info(result)
                    doc = ET.fromstring(result)
                    if doc is not None:
                        status_code = int(doc.find('.//{http://www.epsilon.com/webservices/}Status').text)
                        logging.info("Status code:: %d" % status_code)
                        if status_code == 0:
                            member_offer_obj.status = 1
                            member_offer_obj.activation_date = datetime.now()
                            member_offer_obj.put()
                            response_dict['message'] = "Offer has been activated successfully"
                        elif status_code == 1 or status_code == 99:
                            # TODO : check response from telluride when user is trying to activate an expired offer.
                            member_offer_obj.status = 0  # TODO: 1 or 0?
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
                    response_dict['message'] = "Sorry, Offer could not be activated. Member Offer Object not found."
            else:
                logging.error("could not fetch offer or member details for key:: %s", offer_key)
                response_dict['message'] = "Sorry could not fetch member offer details."
        except httplib.HTTPException as exc:
            logging.error(exc)
            response_dict['message'] = "Sorry could not fetch offer details because of the request time out."

        self.response.write(json.dumps(response_dict))


class SendOfferToMember(webapp2.RequestHandler):
    # TODO: Make response consistent with other APIs as well
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        member_id = self.request.get('member_id')
        offer_value = self.request.get('offer_value')
        campaign_name = self.request.get('campaign_name')
        issuance_channel = "EMAIL"

        if not member_id or not offer_value or not campaign_name:
            response_dict = {"message": "Please provide member_id, offer_value and campaign_name with the request"}
            self.response.write(json.dumps(response_dict))
        else:
            response = self.process_data(member_id, offer_value, campaign_name, issuance_channel)
            self.response.write(json.dumps(response))

    def process_data(self, member_id, offer_value, campaign_name, issuance_channel):
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

                    member = member_key.get(use_datastore=True, use_memcache=False, use_cache=False)
                    if member is None:
                        logging.info("member is None")
                        response_dict['message'] = "Member ID " + member_id + " not found in database."
                        return response_dict
                    else:
                        host = get_email_host()
                        relative_url = str("offerDetails?offer=" + offer_value +
                                           "&&member=" + member_id +
                                           "&&campaign=" + campaign_name)

                        # send_mail(member_entity=member, offer_entity=offer,
                        #           campaign_entity=campaign_entity)

                        logging.info("Email URL :: %s %s", host, relative_url)
                        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                        logging.info("email service call result :: %s", result)

                        member_offer_data_key = MemberOfferDataService.create(offer, member, issuance_channel)

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


class IssueActivateKPOSOffer(webapp2.RequestHandler):
    def get(self):
        """
        Register a member to an offer on KPOS side.
        Get offer_id, member_id, start and end date from query parameters. If any missing,
        respond with an error message.
        Verify that the offer and member have valid entries in OfferData and MemberData respectively.
        IF offer_end_date and end_date in the request URL are different, 3 telluride calls will have to
        be made. 1. Bring offer to DRAFT state, 2. update start and end date for the offer, 3. change offer
        state to ACTIVATED. Register the member to the offer at Telluride. The MemberOfferData kind is then
        updated with details of this member-offer mapping.
        """
        self.response.headers['Content-Type'] = 'application.json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        response_dict = dict()
        try:
            offer_id = self.request.get('offer_id')
            logging.info("Request offer_id: " + offer_id)
            member_id = self.request.get('member_id')
            logging.info("Request member_id: " + member_id)
            start_date = self.request.get('start_date')
            logging.info("Request start_date: " + start_date)
            end_date = self.request.get('end_date')
            logging.info("Request end_date: " + end_date)
            issuance_channel = self.request.get("channel")
            logging.info("Request channel :: %s", issuance_channel)

            if not offer_id or not member_id or not start_date or not end_date or not issuance_channel:
                response_dict['message'] = """Please provide offer_id, member_id,
                                           start date and end date with the request"""
                self.response.write(json.dumps(response_dict))
                return

            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)

            if offer_key is None:
                result = {"data": "Invalid offer!"}
                self.response.write(json.dumps(result))
                return

            if member_key is None:
                result = {"data": "That member does not exist!"}
                self.response.write(json.dumps(result))
                return

            logging.info("fetched offer_key and member key ")

            offer = offer_key.get()
            member = member_key.get()

            offer_end_date = offer.OfferEndDate
            offer_start_date = offer.OfferStartDate

            logging.info("The offer's current start and end date are :: %s, %s", offer_start_date, offer_end_date)

            if offer is not None and member is not None:
                logging.info("Valid offer and member. ")

                if offer_end_date == end_date and offer_start_date == start_date:
                    logging.info("Start and end date is the same as campaign dates.")
                    message = self.register_offer(offer_id, member_id, start_date, end_date, issuance_channel)
                    response_dict['message'] = message
                else:
                    logging.info("Start and end dates to be updated.")
                    message = self.update_offer(offer_id, member_id, start_date, end_date, issuance_channel)
                    response_dict['message'] = message

                    register_message = self.register_offer(offer_id, member_id, start_date, end_date, issuance_channel)
                    logging.info("Register member to offer message :: %s", register_message)

                    offer.OfferEndDate = end_date
                    offer.OfferStartDate = start_date
                    offer.put()
                    logging.info("Updated offer entity with new dates.")
            else:
                logging.error("could not fetch offer or member details for key:: %s", offer_key)
                response_dict['message'] = "Sorry could not fetch member offer details."
        except httplib.HTTPException as exc:
            logging.error(exc)
            response_dict['message'] = "Sorry could not fetch offer details because of the request time out."

        self.response.write(json.dumps({'data':response_dict}))

    def register_offer(self, offer_id, member_id, start_date, end_date, issuance_channel):
        host = get_telluride_host()
        relative_url = str("registerMember?offer_id=" + offer_id +
                           "&&member_id=" + member_id)
        logging.info("Telluride URL :: %s, %s", host, relative_url)
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

        logging.info(json.loads(result))
        result = json.loads(result).get('data')
        logging.info(result)

        status_code = int(result.get('status_code'))

        offer_key = ndb.Key('OfferData', offer_id)
        member_key = ndb.Key('MemberData', member_id)

        member_offer_data = MemberOfferData(offer=offer_key,
                                            member=member_key,
                                            offer_id=offer_id,
                                            member_id=member_id,
                                            status=0,
                                            issuance_date=datetime.now(),
                                            validity_start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                                            validity_end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                                            issuance_channel=issuance_channel)


        if status_code == 0:
            member_offer_data.status = 1
            member_offer_data.activation_date = datetime.now()
            member_offer_data.put()
        elif status_code == 1 or status_code == 99:
            # TODO : check response from telluride when user is trying to activate an expired offer.
            member_offer_data.status = 0  # TODO: 1 or 0?
            member_offer_data.put()
        else:
            logging.error("Telluride call failed. %s", result.get('error_message'))


        return result.get('message')

    def update_offer(self, offer_id, member_id, start_date, end_date, issuance_channel):
        host = get_telluride_host()
        relative_url = str("updateKposOffer?offer_id=" + offer_id +
                           "&&member_id=" + member_id +
                           "&&start_date=" + start_date +
                           "&&end_date=" + end_date +
                           "&&channel=" + issuance_channel)
        logging.info("Telluride URL :: %s, %s", host, relative_url)
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
        logging.info("RESULT ::%s", result)

        logging.info(json.loads(result))
        result = json.loads(result).get('data')
        logging.info(result)

        offer_key = ndb.Key('OfferData', offer_id)
        member_key = ndb.Key('MemberData', member_id)

        member_offer_data = MemberOfferData(offer=offer_key,
                                            member=member_key,
                                            offer_id=offer_id,
                                            member_id=member_id,
                                            status=0,
                                            issuance_date=datetime.now(),
                                            validity_start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                                            validity_end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                                            issuance_channel=issuance_channel)
        status_code = int(result.get('status_code'))

        if status_code == 0:
            member_offer_data.status = 1
            member_offer_data.activation_date = datetime.now()
            member_offer_data.put()

            offer = offer_key.get()
            offer.OfferEndDate = end_date
            offer.OfferStartDate = start_date
            offer.put()
        elif status_code == 1 or status_code == 99:
            # TODO : check response from telluride when user is trying to activate an expired offer.
            member_offer_data.status = 0  # TODO: 1 or 0?
            member_offer_data.put()
        else:
            logging.error("Telluride call failed. %s", result.get('error_message'))

        return result.get('message')
