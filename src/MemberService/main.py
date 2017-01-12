import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
from models import MemberData, MemberOfferData, ndb, ModelData, BuDvsnMappingData
from datastore import MemberOfferDataService
from googleapiclient.errors import HttpError
from utilities import create_pubsub_message, make_request, get_telluride_host, get_email_host, \
    get_offer_id
from datetime import datetime


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


class SingleMemberOffer(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        member_id = self.request.get('member_id')
        member = MemberData.get_by_id(member_id)
        if member is None:
            result = {"data": "That member does not exist!"}
            self.response.set_status(404)
            self.response.write(json.dumps(result))
            return

        logging.info("Member object :: %s", member)
        result = list()
        member_dict = dict()

        member_details_dict = member.to_dict()
        member_details_dict["last_updated_at"] = member.last_updated_at.strftime('%Y-%m-%d')
        member_details_dict["eml_opt_in"] = True if member.eml_opt_in == "Y" else False
        member_dict["member_details"] = member_details_dict

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
                issued_offer = MemberOfferDataService.create_response_object(item=item)

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
                updated_offer = MemberOfferDataService.create_response_object(item=item)

                logging.info("Added latest offer issued information for the member."
                             "Offer details dict :: %s", updated_offer)
                member_dict["offer_details"]["latest_offer_updated"] = updated_offer

        result.append(member_dict)

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
            reg_start_date = self.request.get('start_date')
            logging.info("Request start_date: " + reg_start_date)
            reg_end_date = self.request.get('end_date')
            logging.info("Request end_date: " + reg_end_date)

            if not offer_id or not member_id or not reg_start_date or not reg_end_date:
                response_dict['message'] = "Please provide offer id, member id, start date, end date."
                self.response.set_status(404)
                self.response.write(json.dumps(response_dict))
                return

            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)

            if offer_key is None:
                result = {"data": "Invalid offer!"}
                self.response.set_status(404)
                self.response.write(json.dumps(result))
                return
            if member_key is None:
                result = {"data": "That member does not exist!"}
                self.response.set_status(404)
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
                    relative_url = str("registerMember?offer_id=" + offer_id +
                                       "&&member_id=" + member_id +
                                       "&&start_date=" + reg_start_date +
                                       "&&end_date=" + reg_end_date)

                    logging.info("Telluride URL :: %s, %s", host, relative_url)
                    result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                    logging.info(json.loads(result))
                    result = json.loads(result).get('data')
                    logging.info(result)

                    status_code = result['status_code']
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


class KPOSOfferHandler(webapp2.RequestHandler):
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
            reg_start_date = self.request.get('start_date')
            logging.info("Request start_date: " + reg_start_date)
            reg_end_date = self.request.get('end_date')
            logging.info("Request end_date: " + reg_end_date)
            issuance_channel = self.request.get("channel")
            logging.info("Request channel :: %s", issuance_channel)

            if not offer_id or not member_id or not reg_start_date or not reg_end_date or not issuance_channel:
                response_dict['message'] = """Please provide offer_id, member_id, start date, end date and channel."""
                self.response.set_status(404)
                self.response.write(json.dumps(response_dict))
                return

            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)

            if offer_key is None:
                result = {"data": "Invalid offer!"}
                self.response.set_status(404)
                self.response.write(json.dumps(result))
                return

            if member_key is None:
                result = {"data": "That member does not exist!"}
                self.response.set_status(404)
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

                # Ideally, offer end date will be after member registration end date, i.e reg is within offer period.
                # If registration end date is LATER THAN offer's current end date, extend the offer's end date.
                if offer_end_date >= reg_end_date:
                    logging.info("Start and end date is within campaign date range. Registering member...")
                    message = self.register_offer(offer_id, member_id, reg_start_date, reg_end_date, issuance_channel)
                    response_dict['message'] = message
                else:
                    logging.info("Registration date > offer end date. Offer end date needs to be extended.")
                    message = self.update_offer(offer_id, member_id, reg_start_date, reg_end_date, issuance_channel)
                    response_dict['message'] = message

                    logging.info("Offer end date updated! Registering member...")
                    register_message = self.register_offer(offer_id, member_id, reg_start_date, reg_end_date, issuance_channel)
                    logging.info("Register member to offer message :: %s", register_message)

                    offer.OfferEndDate = reg_end_date
                    offer.put()
                    logging.info("Updated OfferData with new dates.")
            else:
                logging.error("could not fetch offer or member details for key:: %s", offer_key)
                response_dict['message'] = "Sorry could not fetch member offer details."
        except httplib.HTTPException as exc:
            logging.error(exc)
            response_dict['message'] = "Sorry could not fetch offer details because of the request time out."

        self.response.write(json.dumps({'data':response_dict}))

    def register_offer(self, offer_id, member_id, reg_start_date, reg_end_date, issuance_channel):
        host = get_telluride_host()
        relative_url = str("registerMember?offer_id=" + offer_id +
                           "&&member_id=" + member_id +
                           "&&start_date=" + reg_start_date +
                           "&&end_date=" + reg_end_date)
        logging.info("Telluride URL :: %s, %s", host, relative_url)
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

        logging.info(json.loads(result))
        result = json.loads(result).get('data')
        logging.info(result)

        status_code = int(result.get('status_code'))
        member_offer_data = MemberOfferDataService.create_object(offer_id, member_id, issuance_channel,
                                                                 reg_start_date, reg_end_date)

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
                           "&&end_date=" + end_date)

        logging.info("Telluride URL :: %s, %s", host, relative_url)
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
        logging.info("RESULT ::%s", result)

        logging.info(json.loads(result))
        result = json.loads(result).get('data')
        logging.info(result)

        offer_key = ndb.Key('OfferData', offer_id)

        member_offer_data = MemberOfferDataService.create_object(offer_id, member_id, issuance_channel,
                                                                 start_date, end_date)
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


class ModelDataHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        member_id = self.request.get('member_id')

        if not member_id:
            result = {"data": "Please provide a member ID."}
            self.response.set_status(404)
            self.response.write(json.dumps(result))
            return

        # TODO: handle when there are > 1 entries with a certain member_id
        model_data = ModelData.query(ModelData.member_id == member_id).get()

        if model_data is None:
            result = {"data": "Model data for this member does not exist."}
            self.response.set_status(404)
            logging.info("Model data is None.")
            self.response.write(json.dumps(result))
            return

        if model_data.offer_value == 0:
            result = {"data": "Model data for this member does not exist."}
            self.response.set_status(404)
            logging.info("Offer amount is 0.")
            self.response.write(json.dumps(result))
            return

        campaign_name = model_data.campaign_name
        offer_value = model_data.offer_value
        offer_id = get_offer_id(campaign_name, offer_value)

        div_no = model_data.div_no
        bu_entities = BuDvsnMappingData.query(BuDvsnMappingData.dvsn_nbr == int(div_no)).fetch()
        soar_nos = list()
        soar_names = list()
        for entity in bu_entities:
            soar_nos.append(entity.soar_no)
            soar_names.append(entity.soar_nm)

        logging.info("List of soar_nos for the division %s is %s", div_no, soar_nos)

        model_dict = model_data.to_dict()

        model_dict["created_at"] = model_data.created_at.strftime('%Y-%m-%d')

        model_dict["offer_id"] = offer_id
        model_dict["soar_no"] = soar_nos
        model_dict["soar_name"] = soar_names

        logging.info("Model data :: %s", model_dict)

        self.response.write(json.dumps({'data': model_dict}))


class UpdateEmailOfferIssuanceHandler(webapp2.RequestHandler):
    def get(self):
        response_dict = dict()
        try:
            logging.info("Member id:: %s", self.request.get('member_id'))
            logging.info("Offer id:: %s", self.request.get('offer_id'))
            logging.info("Registration start date:: %s", self.request.get('reg_start_date'))
            logging.info("Registration end date:: %s", self.request.get('reg_end_date'))
            logging.info("Channel:: %s", self.request.get('channel'))

            offer_id = self.request.get('offer_id')
            member_id = self.request.get('member_id')
            member_entity = ndb.Key('MemberData', member_id).get()
            offer_entity = ndb.Key('OfferData', offer_id).get()
            reg_start_date = self.request.get('reg_start_date')
            reg_end_date = self.request.get('reg_end_date')
            channel = self.request.get('channel')

            logging.info("Member :: %s", member_entity)
            logging.info("Offer :: %s", offer_entity)
            if member_entity is None or offer_entity is None:
                response_dict = {'status': 'Failure', 'message': "Details not found for the request"}
            else:
                member_offer_data_key = MemberOfferDataService.create(offer_entity=offer_entity,
                                                                      member_entity=member_entity,
                                                                      channel=channel.upper(),
                                                                      reg_start_date=reg_start_date,
                                                                      reg_end_date=reg_end_date,
                                                                      offer_id=offer_id,
                                                                      member_id=member_id)
                logging.info("Member offer object created:: %s", member_offer_data_key)
                response_dict = {'status': 'Success',
                                 'message': "Member Offer entity created successfully!!!"}

        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            response_dict = {'status': 'Failure', 'message': "Server error has encountered an error"}

        finally:
            logging.info(response_dict)
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.headers['Content-type'] = 'application/json'
            self.response.write(json.dumps({'data': response_dict}))


class UpdateEmailOfferActivationData(webapp2.RequestHandler):
    def get(self):
        response_dict = dict()
        try:
            logging.info("Member id:: %s", self.request.get('member_id'))
            logging.info("Offer id:: %s", self.request.get('offer_id'))
            offer_id = self.request.get('offer_id')
            member_id = self.request.get('member_id')
            member_offer_entity = ndb.Key('MemberOfferData', offer_id+"_"+member_id).get()

            if member_offer_entity is None:
                response_dict = {'status': 'Failure', 'message': "Details not found for the request"}
            else:
                member_offer_entity.status = 1
                member_offer_entity.activation_date = datetime.now()
                member_offer_entity.activated_channel = 'EMAIL'
                member_offer_data_key = member_offer_entity.put()
                logging.info("Member offer object updated:: %s", member_offer_data_key)
                response_dict = {'status': 'Success',
                                 'message': "Member Offer entity updated successfully!!!"}

        except Exception as e:
            logging.error(e)
            response_dict = {'status': 'Failure', 'message': "Server error has encountered an error"}

        finally:
            logging.info(response_dict)
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.headers['Content-type'] = 'application/json'
            self.response.write(json.dumps({'data': response_dict}))
