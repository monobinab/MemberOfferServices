import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
import pubsub_utils
import csv
from models import CampaignData, MemberData, MemberOfferData, FrontEndData, ndb, OfferData, StoreData, \
    ConfigData
from datastore import CampaignDataService, MemberOfferDataService, OfferDataService
from telluride_service import TellurideService
from sendEmail import send_mail
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials

from google.appengine.api import namespace_manager
from Utilities import dev_namespace as namespace_var, config_namespace, create_pubsub_message
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
        self.response.write("campaign-backend-service")


class SaveCampaignHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
        except Exception as e:
            logging.error(e)
        offer_data = self.request.get('offer_data')
        logging.info('****campaign data: %s', offer_data)
        json_data = json.loads(offer_data)

        campaign_dict = json_data['campaign_details']
        campaign_name = campaign_dict['name']
        is_entity = ndb.Key('CampaignData', campaign_name).get()
        logging.info('is_entity: %s', is_entity)
        logging.info('type is_entity: %s', type(is_entity))

        # Check for create new entity or update an existing entity
        if is_entity is None:
            CampaignDataService.save_campaign(json_data, datetime.now())
        else:
            CampaignDataService.save_campaign(json_data, is_entity.created_at)

        logging.info('Campaign: %s saved in datastore', campaign_name)

        logging.info('Creating pubsub publish message')
        campaign_json_data = create_pubsub_message(json_data)
        logging.info('Created pubsub publish message')

        # Sending pubsub message to topic
        if campaign_json_data is not None:
            pubsub_response = pubsub_utils.post_pubsub(campaign_json_data)
            logging.info('pubsub_response:: %s', pubsub_response)

            if pubsub_response == 200:
                logging.info('Campaign: %s save notification to pubsub: Success', campaign_name)
            else:
                logging.info('Campaign: %s save notification to pubsub: Fail', campaign_name)
        else:
            logging.info('pubsub message is None')
            logging.info('Campaign: %s save notification to pubsub: Fail', campaign_name)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'message': 'Campaign is saved successfully!!!',
                                        'status': 'success'}))


class GetAllCampaignsHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        # Save the current namespace.
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
        except Exception as e:
            logging.error(e)
        query = CampaignData.query().order(-CampaignData.created_at)
        entity_list = query.fetch(100)
        result = list()
        logging.info('len of the list: %s', len(entity_list))
        for each in entity_list:
            key = ndb.Key('CampaignData', each.name)
            each_entity = key.get()
            campaign_dict = dict()
            offer_dict = dict()
            campaign_dict['campaign_id'] = each_entity.key.id()
            campaign_dict['name'] = each_entity.name
            campaign_dict['money'] = each_entity.money
            campaign_dict['category'] = each_entity.category
            campaign_dict['conversion_ratio'] = each_entity.conversion_ratio
            campaign_dict['period'] = each_entity.period
            campaign_dict['format_level'] = str(each_entity.format_level)
            campaign_dict['store_location'] = str(each_entity.store_location)
            campaign_dict['start_date'] = str(each_entity.start_date)
            campaign_dict['created_at'] = str(each_entity.created_at)

            offer_dict['offer_id'] = each_entity.key.id()
            offer_dict['offer_type'] = each_entity.offer_type
            offer_dict['min_value'] = each_entity.min_value
            offer_dict['max_value'] = each_entity.max_value
            offer_dict['valid_till'] = each_entity.valid_till
            offer_dict['member_issuance'] = each_entity.max_per_member_issuance_frequency
            each_dict = dict()
            each_dict['campaign_details'] = campaign_dict
            each_dict['offer_details'] = offer_dict
            result.append(each_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))


class GetAllMembersHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
        except Exception as e:
            logging.error(e)
        query = MemberData.query()
        member_list = query.fetch(10)
        result = []
        for member in member_list:
            result.append(member.to_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))


class ActivateOfferHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        response_dict = dict()
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
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
                    status_code = TellurideService.register_member(offer, member)
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


class EmailOfferMembersHandler(BaseHandler):
    def get(self, namespace=config_namespace):
        try:
            logging.info("Member id:: %s", self.request.get('member_id'))
            logging.info("Offer id:: %s", self.request.get('offer_id'))
            member_entity = ndb.Key('MemberData', self.request.get('member_id'), namespace=namespace).get()
            offer_entity = ndb.Key('OfferData', self.request.get('offer_id'), namespace=namespace_var).get()
            logging.info("Member :: %s", member_entity)
            logging.info("Offer :: %s", offer_entity)
            if member_entity is None or offer_entity is None:
                response_dict = {'status': 'Failure', 'message': "Details not found for the request"}
            else:
                campaign_entity = offer_entity.campaign.get()
                send_mail(member_entity=member_entity, offer_entity=offer_entity, campaign_entity=campaign_entity)
                member_offer_data_key = MemberOfferDataService.create(offer_entity=offer_entity,
                                                                      member_entity=member_entity)
                logging.info('member_offer_key:: %s', member_offer_data_key)
                logging.info('Offer %s email has been sent to: : %s', offer_entity, member_entity.email)
                response_dict = {'status': 'Success', 'message': "Offer email has been sent successfully!!!"}
        except Exception as e:
            logging.error(e)
            response_dict = {'status': 'Failure', 'message': "Server error has encountered an error"}
        finally:
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.headers['Content-type'] = 'application/json'
            self.response.write(json.dumps(response_dict))


class UIListItemsHandler(webapp2.RequestHandler):
    def get(self, namespace=config_namespace):
        key = ndb.Key('FrontEndData', '1', namespace=namespace)
        result = key.get(use_datastore=True, use_memcache=False, use_cache=False)
        sears_entity = ndb.Key('StoreData', 'SEARS FORMAT', namespace=namespace).get()
        kmart_entity = ndb.Key('StoreData', 'KMART FORMAT', namespace=namespace).get()

        result_dict = dict()
        result_dict['categories'] = list(result.Categories)
        result_dict['offer_type'] = list(result.Offer_Type)
        result_dict['conversion_ratio'] = list(result.Conversion_Ratio)
        result_dict['minimum_surprise_points'] = result.Minimum_Surprise_Points
        result_dict['maximum_surprise_points'] = result.Maximum_Surprise_Points
        result_dict['format_level'] = list(result.Format_Level)

        store_dict = dict()
        store_dict['kmart'] = list(kmart_entity.Locations)
        store_dict['sears'] = list(sears_entity.Locations)

        result_dict['store_locations'] = store_dict

        logging.info(result_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result_dict}))


class MetricsHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
        except Exception as e:
            logging.error(e)
        campaign_id = self.request.get("campaign_id")
        result_dict = MemberOfferDataService.get_offer_metrics(campaign_id=campaign_id)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'data': result_dict}))


class BatchJobHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        try:
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
        except Exception as e:
            logging.error(e)
        if self.request.get('dataset_name') is None or not self.request.get('dataset_name') or \
            self.request.get('table_name') is None or not self.request.get('table_name') or \
            self.request.get('project_id') is None or not self.request.get('project_id') or \
            self.request.get('campaign_name') is None or not self.request.get('campaign_name'):
            response_html = "<html><head><title>Batch Job Execution</title></head><body><h3> " \
                             + "Please provide dataset_name, table_name, project_id and campaign_name with the " \
                               "request</h3></body></html>"
            self.response.write(response_html)
            return

        # dataset = 'test_member_offer'
        # table_name = 'memberofferdata'
        # project = 'syw-offers'
        dataset_name = self.request.get('dataset_name')
        table_name = self.request.get('table_name')
        project = self.request.get('project_id')
        campaign_name = self.request.get('campaign_name')
        response = BatchJobHandler.list_rows(dataset_name, table_name, campaign_name, project)
        response_html = "<html><head><title>Batch Job Execution</title></head><body><h3> " \
                        + response['message']
        self.response.write(response_html)

    @classmethod
    def list_rows(cls, dataset_name, table_name, campaign_name, project_id=None):
        response_dict = dict()
        new_line = '\n'
        # [START build_service]
        # Grab the application's default credentials from the environment.
        credentials = GoogleCredentials.get_application_default()
        # Construct the service object for interacting with the BigQuery API.
        bigquery_service = build('bigquery', 'v2', credentials=credentials)
        # [END build_service]

        campaign_key = ndb.Key('CampaignData', campaign_name, namespace=namespace_var)
        logging.info("fetched campaign_key")

        campaign = campaign_key.get()
        if campaign is None:
            logging.info("campaign is None")
            response_dict['message'] = "Campaign "+campaign_name+" not found"
            return response_dict
        else:
            logging.info("campaign is not None")
            try:
                # [START run_query]
                query_request = bigquery_service.jobs()
                query_data = {
                    'query': (
                        'SELECT LYL_ID_NO as Member, '
                        'ofr_val as Offer '
                        'FROM ['+project_id+':'+dataset_name+'.'+table_name+'] LIMIT 20;')
                }
                logging.info('query formed: %s', query_data)

                query_response = query_request.query(
                    projectId='syw-offers',
                    body=query_data).execute()
                # [END run_query]
                logging.info('Query response formed')
                logging.info('Query results:')

                # [START print_results]
                member_offer_list = list()

                for row in query_response['rows']:
                    logging.info('row[f]:: %s', row['f'])

                    memberOffer_dict = dict()
                    memberOffer_dict['member'] = row['f'][0]['v']
                    memberOffer_dict['offervalue'] = row['f'][1]['v']
                    member_offer_list.append(memberOffer_dict)

                offer_list = list()
                success_msg = "Offer has been created and activated successfully"
                response_dict['message'] = ""

                for memberoffer in member_offer_list:
                    logging.info('len(offer_list): %s', len(offer_list))

                    if len(offer_list) == 5:
                        break

                    logging.info('memberoffer[member]: %s', memberoffer['member'])
                    logging.info('memberoffer[offervalue]: %s', memberoffer['offervalue'])

                    offer_name = "%s_%s" % (str(campaign.name), str(memberoffer['offervalue']))

                    if offer_name in offer_list:
                        logging.info('Offer %s already created and activated', offer_name)
                        continue
                    else:
                        # Create offer in datastore
                        response_offer = OfferDataService.save_offer(campaign, memberoffer['offervalue'])

                    if response_offer['message'] == 'success':
                        offer = response_offer['offer']

                        # Create offer in telluride
                        if offer_name in offer_list:
                            logging.info('Offer %s already created and activated', offer_name)
                        else:
                            response_telluride = TellurideService.create_offer(offer)
                            if(response_telluride['message'] == success_msg):
                                logging.info('Offer created in Telluride system:: %s', offer_name)
                                logging.info('Offer %s has been created and activated successfully', offer_name)
                                logging.info('Adding it to offers created list')
                                offer_list.append(offer_name)

                                member_emails = ''
                                member_id = '7081327663412819'
                                member_key = ndb.Key('MemberData', member_id)
                                logging.info("Fetched member_key for member: %s", member_id)

                                member = member_key.get()
                                if member is None:
                                    logging.info("member is None")
                                    response_dict['message'] = "Member ID "+member_id+" not found in datastore"
                                    return response_dict
                                else:
                                    send_mail(member_entity=member, offer_entity=offer,
                                              campaign_entity=offer.campaign.get())
                                    member_offer_data_key = MemberOfferDataService.create(offer, member)

                                    logging.info('member_offer_key:: %s', member_offer_data_key)
                                    logging.info('Offer %s email has been sent to:: %s', offer.OfferNumber, member.email)
                                    response_dict['message'] = response_dict['message'] + new_line + " Offer "+offer.OfferNumber+" emails has been sent to: "+member.email
                            else:
                                logging.info('Error creating offer %s in telluride system. Response from telluride call is: %s', offer.OfferNumber,response_dict['message'])
                                response_dict['message'] = response_dict['message'] + new_line +" Error creating offer "+offer.OfferNumber+" in telluride system. Response from telluride call is:: "+response_dict['message']

                    # [END print_results]

            except HttpError as err:
                print('Error: {}'.format(err.content))
                logging.error('Error: {}'.format(err.content))
                response_dict['message'] = "HttpError exception: "+ err.content
                raise err

        logging.info('response_dict[message]: %s', response_dict['message'])
        return response_dict


class BalanceHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            logging.info(str(self))
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
            result = TellurideService.get_balance()
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write("Request has timed out. Please try again.")
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write("Internal Server Error")


class RedeemOfferHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        try:
            logging.info(str(self))
            namespace_manager.set_namespace(namespace)
            logging.info("Namespace set::" + namespace)
            result = TellurideService.redeem_offer()
            self.response.write(json.dumps({'data': result}))
        except httplib.HTTPException as exc:
            logging.error(exc)
            self.response.set_status(408)
            self.response.write("Request has timed out. Please try again.")
        except Exception as e:
            logging.error(e)
            self.response.set_status(500)
            self.response.write("Internal Server Error")


class UploadStoreIDHandler(webapp2.RequestHandler):
    def get(self, namespace=namespace_var):
        with open('shclocn.csv', 'rb') as f:
            reader = csv.reader(f)
            header = next(reader, None)

        for index, column in enumerate(header):
            if column.upper() == "LOCATION NUMBER":
                location_number_index = index

            if column.upper() == "LOCATION NAME":
                location_name_index = index

            if column.upper() == "NATIONAL DESCRIPTION":
                nat_description_index = index

            if column.upper() == "ROW CREATE TIMESTAMP":
                shop_status_index = index

        KMART, SEARS, ACCTG, DISTR = (list() for _ in range(4))
        sears_format = "SEARS FORMAT"
        kmart_format = "KMART FORMAT"
        acctg_format = "ACCTG FORMAT"
        distr_format = "DISTR FORMAT"

        with open('shclocn.csv', 'rU') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row
            for index, row in enumerate(reader):
                if row[shop_status_index].upper() == "OPEN":
                    location_number = row[location_number_index]
                    location_name = row[location_name_index]
                    location_id = location_number + "-" + location_name

                    if row[nat_description_index].upper() == "KMART FORMAT":
                        KMART.append(location_id)

                    if row[nat_description_index].upper() == "SEARS FORMAT":
                        SEARS.append(location_id)

                    if row[nat_description_index].upper() == "ACCTG FORMAT":
                        ACCTG.append(location_id)

                    if row[nat_description_index].upper() == "DISTR FORMAT":
                        DISTR.append(location_id)

        formats_list = [sears_format, kmart_format, acctg_format, distr_format]
        nmbr_nm_list = [sorted(SEARS), sorted(KMART), sorted(ACCTG), sorted(DISTR)]

        for format, values in zip(formats_list, nmbr_nm_list):
            store_data = StoreData(Format_Level=format, Locations=values)
            store_data.key = ndb.Key('StoreData', format)
            store_data.put()


class MigrateNamespaceData(webapp2.RequestHandler):
    def migrateConfigData(self, namespace_var):
        configurations = ['URLConfig', 'PubSubConfig', 'SendGridConfig']

        for conf in configurations:
            url_entity = ndb.Key('ConfigData', conf, namespace=config_namespace).get()
            url_entity.key = ndb.Key('ConfigData', conf, namespace=namespace_var)
            url_entity.put()

    def migrateFrontendData(self, namespace_var):
        entity = ndb.Key('FrontEndData', '1', namespace=config_namespace).get()
        entity.key = ndb.Key('FrontEndData', '1', namespace=namespace_var)
        entity.put()

    def migrateMemberData(self, namespace_var):
        ids = ['1', '7081327663412819', '3', '4']

        for idx in ids:
            entity = ndb.Key('MemberData', idx, namespace=config_namespace).get()
            entity.key = ndb.Key('MemberData', idx, namespace=namespace_var)
            entity.put()

    def migrateSendGridData(self, namespace_var):
        entity = ndb.Key('SendgridData', '1', namespace=config_namespace).get()
        entity.key = ndb.Key('SendgridData', '1', namespace=namespace_var)
        entity.put()

    def get(self):
        ns = self.request.get('namespace')
        self.migrateConfigData(namespace_var=ns)
        self.migrateFrontendData(namespace_var=ns)
        self.migrateMemberData(namespace_var=ns)
        self.migrateSendGridData(namespace_var=ns)
        self.response.write("Data migrated successfully!!!")


class ModelDataSendEmailHandler(webapp2.RequestHandler):
    def get(self):
        if self.request.get('member_id') is None or not self.request.get('member_id') or self.request.get('offer_value') is None or not self.request.get('offer_value') or self.request.get('campaign_name') is None or not self.request.get('campaign_name') :
            response_html = "<html><head><title>Batch Job Execution</title></head><body><h3> " \
                             + "Please provide member_id, offer_value and campaign_name with the request</h3></body></html>"
            self.response.write(response_html)
            return

        member_id =  self.request.get('member_id')
        offer_value =  self.request.get('offer_value')
        campaign_name =  self.request.get('campaign_name')
        channel = "EMAIL"

        response = self.process_data(member_id, offer_value, campaign_name, channel)

        self.response.write(response['message'])

    def process_data(self,member_id, offer_value, campaign_name, channel):
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
                        send_mail(member_entity=member, offer_entity=offer)
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


# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/saveCampaign', SaveCampaignHandler),
    ('/campaigns', GetAllCampaignsHandler),
    ('/members', GetAllMembersHandler),
    ('/activateOffer', ActivateOfferHandler),
    ('/emailMembers', EmailOfferMembersHandler),
    ('/getListItems', UIListItemsHandler),
    ('/getMetrics', MetricsHandler),
    ('/batchJob', BatchJobHandler),
    ('/getBalance', BalanceHandler),
    ('/redeemOffer', RedeemOfferHandler),
    ('/uploadStoreIDs', UploadStoreIDHandler),
    ('/migrateEntities', MigrateNamespaceData),
    ('/sendEmailJob', ModelDataSendEmailHandler)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()