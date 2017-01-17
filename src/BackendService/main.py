import sys
sys.path.insert(0, 'lib')
import json
import logging
import httplib
import webapp2
import pubsub_utils
import csv
from models import CampaignData, MemberOfferData, ndb, StoreData, OfferData, EmailEventMetricsData, BUData
from datastore import CampaignDataService, MemberOfferDataService, OfferDataService, EmailEventMetricsDataService
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from utilities import create_pubsub_message, make_request, get_jinja_environment, \
    get_email_host, get_telluride_host, get_member_host
from datetime import datetime
from google.appengine.api import urlfetch
import time


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
        self.response.write("backend-service")


class SaveCampaignHandler(webapp2.RequestHandler):
    def get(self):
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

        host = get_telluride_host()
        relative_url = "createCampaign?campaign_id=" + campaign_name
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
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
        self.response.write(result)


class GetAllCampaignsHandler(webapp2.RequestHandler):
    def get(self):
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


class ActivateOfferHandler(webapp2.RequestHandler):
    def get(self):
        response_dict = dict()
        jinja_environment = get_jinja_environment()
        template = jinja_environment.get_template('activate-offer.html')
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        try:
            offer_id = self.request.get('offer_id')
            member_id = self.request.get('member_id')
            logging.info("Request offer_id: " + offer_id)
            logging.info("Request member_id: " + member_id)

            if not offer_id or not member_id:
                message = "Please provide offer_id and member_id with the request"
                message_dict = {'message': message,
                                'offer_success': 0
                                }
                rendered_template = template.render(message_dict)
                self.response.write(rendered_template)
                return

            offer_key = ndb.Key('OfferData', offer_id)
            member_key = ndb.Key('MemberData', member_id)

            logging.info("fetched offer_key and member key ")
            offer = offer_key.get()
            logging.info("THE OFFER FETCHED :: %s", offer)
            member = member_key.get()
            logging.info("THE Member FETCHED :: %s", member)

            # offer_data = OfferData.query(OfferData.campaign == campaign_key).get()
            offer_data = OfferData.get_by_id(offer_id)
            campaign_data = offer_data.campaign.get()
            logging.info(
                "OFFER DATA :: %s, %s, %s", offer_data.OfferDescription,
                offer_data.OfferStartDate,
                offer_data.OfferEndDate
            )
            logging.info("Campaign data :: %s, %s", campaign_data.category, campaign_data.format_level)

            start_date = offer_data.OfferStartDate
            end_date = offer_data.OfferEndDate
            offer_category = campaign_data.category
            offer_format = campaign_data.format_level

            if offer is not None and member is not None:
                logging.info("offer is not None")
                member_offer_obj = MemberOfferData.query(MemberOfferData.member == member_key,
                                                         MemberOfferData.offer == offer_key).get()

                today = datetime.now()
                today_ts = time.mktime(today.timetuple())
                end_date_ns = time.mktime(member_offer_obj.validity_end_date.timetuple())

                if member_offer_obj is not None:
                    if today_ts > end_date_ns:
                        logging.error("Dates are not valid.")
                        response_dict['message'] = "Sorry, Offer is not valid anymore"
                        message = "Sorry, Offer is not valid anymore"
                        offer_success = 0
                    else:
                        host = get_telluride_host()
                        relative_url = str("registerMember?offer_id="+offer_id+"&&member_id="+member_id
                                           + "&&start_date="+member_offer_obj.validity_start_date.strftime("%Y-%m-%d")
                                           + "&&end_date="+member_offer_obj.validity_end_date.strftime("%Y-%m-%d"))

                        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')

                        logging.info(json.loads(result))
                        result = json.loads(result).get('data')
                        logging.info(result)

                        status_code = int(result['status_code'])
                        logging.info("Status code:: %d" % status_code)
                        if status_code == 0 or status_code == 99:
                            response_dict['message'] = "Offer has been activated successfully."
                            message = "Offer has been activated successfully."
                            offer_success = 1
                            if status_code == 99:
                                response_dict['message'] = "Offer has already been activated for this member and expires in "+member_offer_obj.validity_end_date.strftime("%Y-%m-%d")"."
                                message = "Offer has already been activated for this member and expires in "+member_offer_obj.validity_end_date.strftime("%Y-%m-%d")"."
                                offer_success = 0

                            # Update MemberOfferData status call
                            relative_url = str("updateEmailOfferActivationData?offer_id="+offer_id +
                                               "&member_id="+member_id+"&channel="+"EMAIL" +
                                               "&reg_start_date="+member_offer_obj.validity_start_date.strftime('%Y-%m-%d') +
                                               "&reg_end_date="+member_offer_obj.validity_end_date.strftime('%Y-%m-%d'))
                            result = make_request(host=get_member_host(), relative_url=relative_url, payload='',
                                                  request_type='GET')
                            logging.info(json.loads(result))
                            result = json.loads(result).get('data')
                            logging.info("Response from member service::%s" + str(result))


                        else:
                            logging.error("Telluride call failed.")
                            response_dict['message'] = "Sorry, our servers are busy. The offer could not be activated at this time. Please try again later."
                            message = "Sorry, our servers are busy. The offer could not be activated at this time. Please try again later."
                            offer_success = 0

                else:
                    logging.error("Member Offer Object not found for offer key :: %s and member key:: %s",
                                  offer_key, member_key)

                    logging.info("Activated offer %s for member %s", str(offer_key), str(member_key))
                    response_dict['message'] = "Sorry, Offer could not be activated. Member Offer Object not found."
                    message = "Sorry, Offer could not be activated. Member Offer Object not found."
                    offer_success = 0

            else:
                logging.error("could not fetch offer or member details for key:: %s", offer_key)
                response_dict['message'] = "Sorry, could not fetch member offer details."
                message = "Sorry, could not fetch member offer details."
                offer_success = 0

        except httplib.HTTPException as exc:
            logging.error(exc)
            response_dict['message'] = "Sorry, could not fetch offer details because of the request time out."
            message = "Sorry, could not fetch offer details because of the request time out."
            offer_success = 0

        message_dict = {'message': message,
                        'offer_start_date': start_date,
                        'offer_end_date': end_date,
                        'offer_category': offer_category,
                        'offer_format': offer_format,
                        'offer_success': offer_success
                        }
        rendered_template = template.render(message_dict)
        self.response.write(rendered_template)


class UIListItemsHandler(webapp2.RequestHandler):
    def get(self):
        key = ndb.Key('FrontEndData', '1')
        result = key.get(use_datastore=True, use_memcache=False, use_cache=False)
        sears_entity = ndb.Key('StoreData', 'SEARS FORMAT').get()
        kmart_entity = ndb.Key('StoreData', 'KMART FORMAT').get()

        sears_bu_list = ndb.Key('BUData', 'sears').get()
        kmart_bu_list = ndb.Key('BUData', 'kmart').get()

        result_dict = dict()
        # result_dict['categories'] = list(result.Categories)
        result_dict['offer_type'] = list(result.Offer_Type)
        result_dict['conversion_ratio'] = list(result.Conversion_Ratio)
        result_dict['minimum_surprise_points'] = result.Minimum_Surprise_Points
        result_dict['maximum_surprise_points'] = result.Maximum_Surprise_Points
        result_dict['format_level'] = list(result.Format_Level)

        store_dict = dict()
        store_dict['kmart'] = list(kmart_entity.Locations)
        store_dict['sears'] = list(sears_entity.Locations)
        result_dict['store_locations'] = store_dict

        bu_dict = dict()
        bu_dict['sears'] = sears_bu_list.Business_Units
        bu_dict['kmart'] = kmart_bu_list.Business_Units
        result_dict['categories'] = bu_dict

        logging.info(result_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result_dict}))


class MetricsHandler(webapp2.RequestHandler):
    def get(self):
        campaign_id = self.request.get("campaign_id")
        result_dict = MemberOfferDataService.get_offer_metrics(campaign_id=campaign_id)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'data': result_dict}))


class BatchJobHandler(webapp2.RequestHandler):

    def get(self):

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

        campaign_key = ndb.Key('CampaignData', campaign_name)
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
                            # response_telluride = TellurideService.create_offer(offer)
                            host = get_telluride_host()
                            relative_url = "createOffer?offer_id=" + offer.OfferNumber
                            response_telluride = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
                            if response_telluride['message'] == success_msg:
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
                                    host = get_email_host()
                                    relative_url = "emailMembers?offer_id=%s&&member_id=%s", offer.OfferNumber, member_id
                                    result = make_request(host=host, relative_url=relative_url, request_type="GET",
                                                          payload='')
                                    data = json.loads(result).get('data')
                                    if data is not None:
                                        status = data.get('status')
                                        if status == "Success":
                                            member_offer_data_key = MemberOfferDataService.create(offer, member)
                                            logging.info('member_offer_key:: %s', member_offer_data_key)
                                            logging.info('Offer %s email has been sent to:: %s', offer.OfferNumber, member.email)
                                            response_dict['message'] = response_dict['message'] + new_line + " Offer " \
                                                                       +offer.OfferNumber+" emails has been sent to: " \
                                                                       +member.email
                                        else:
                                            logging.info(
                                                'Error creating offer %s in telluride system. Response from telluride call is: %s',
                                                offer.OfferNumber, response_dict['message'])
                                            response_dict['message'] = response_dict[
                                                                           'message'] + new_line + " Error creating offer " + offer.OfferNumber + " in telluride system. Response from telluride call is:: " + \
                                                                       response_dict['message']
                                    else:
                                        logging.info(
                                            'Error creating offer %s in telluride system. Response from telluride call is: %s',
                                            offer.OfferNumber, response_dict['message'])
                                        response_dict['message'] = response_dict[
                                                                       'message'] + new_line + " Error creating offer " + offer.OfferNumber + " in telluride system. Response from telluride call is:: " + \
                                                                   response_dict['message']
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


class UploadStoreIDHandler(webapp2.RequestHandler):
    def get(self):
        with open('shc_locn.csv', 'rb') as f:
            reader = csv.reader(f)
            schema = next(reader, None)

        for index, column in enumerate(schema):
            if column.upper() == "LOCNNBR":
                location_number_index = index

            if column.upper() == "LOCNNM":
                location_name_index = index

            if column.upper() == "NATLDESC":
                nat_description_index = index

        SEARS = list()
        KMART = list()

        with open('shc_locn.csv', 'rU') as f:
            reader = csv.reader(f)
            next(reader, None)

            for row in reader:
                try:
                    location_number = row[location_number_index]
                    location_name = row[location_name_index]
                    location_id = str(location_number) + "-" + location_name
                except Exception as e:
                    logging.info(e)
                    logging.info("Location name or number missing")
                    pass

                if row[nat_description_index].upper() == "KMART FORMAT":
                    KMART.append(location_id)

                if row[nat_description_index].upper() == "SEARS FORMAT":
                    SEARS.append(location_id)

        formats_list = ["SEARS FORMAT", "KMART FORMAT"]
        locations_list = [SEARS, KMART]

        for format, values in zip(formats_list, locations_list):
            store_data = StoreData(Format_Level=format, Locations=values)
            store_data.key = ndb.Key('StoreData', format)
            store_data.put()


class SoarBuHandler(webapp2.RequestHandler):
    def get(self):
        credentials = GoogleCredentials.get_application_default()
        bigquery_service = build('bigquery', 'v2', credentials=credentials)

        query_request = bigquery_service.jobs()
        urlfetch.set_default_fetch_deadline(60)

        KMART_BU_QUERY = (
            """SELECT SOAR_NO, SOAR_NM
            FROM [syw-analytics-repo-prod:cbr_mart_tbls.sywr_kmt_soar_bu]
            group by
            SOAR_NO, SOAR_NM"""
        )

        SEARS_BU_QUERY = (
            """SELECT SOAR_NO, SOAR_NM
            FROM [syw-analytics-repo-prod:cbr_mart_tbls.sywr_srs_soar_bu]
            group by
            SOAR_NO, SOAR_NM"""
        )

        logging.info("Kmart Query :: %s", KMART_BU_QUERY)
        logging.info("Sears Query :: %s", SEARS_BU_QUERY)

        kmart_bu_names = set()
        sears_bu_names = set()
        bu_names = dict()

        query_data = {
            'query': KMART_BU_QUERY
        }

        query_response = query_request.query(
            projectId='syw-offers',
            body=query_data).execute()

        logging.info("Kmart Query response :: %s", query_response)

        for row in query_response['rows']:
            kmart_bu_names.add(row['f'][0]['v'] + " - " + row['f'][1]['v'])

        kmart_bu_names = sorted(kmart_bu_names)
        logging.info("List of kmart BU's :: %s", kmart_bu_names)
        bu_names.update({"kmart": kmart_bu_names})

        query_data = {
            'query': SEARS_BU_QUERY
        }

        query_response = query_request.query(
            projectId='syw-offers',
            body=query_data).execute()

        logging.info("Sears Query response :: %s", query_response)

        for row in query_response['rows']:
            sears_bu_names.add(row['f'][0]['v'] + "-" + row['f'][1]['v'])

        sears_bu_names = sorted(sears_bu_names)
        logging.info("List of sears BU's :: %s", sears_bu_names)

        bu_names.update({"sears": sears_bu_names})
        logging.info("BU names dictionary :: %s", bu_names)

        for format, business_units in bu_names.items():
            bu_data = BUData(Format=format, Business_Units=business_units)
            bu_data.key = ndb.Key('BUData', format)
            bu_data.put()

        self.response.write(json.dumps({"data": "BU data uploaded to datastore - BUData."}))


class SendGridEvents(webapp2.RequestHandler):
    def post(self):
        logging.info(self.request.body)
        self.response.write(json.dumps({'data': str(self.request.body)}))


class MigrateNamespaceData(webapp2.RequestHandler):
    @staticmethod
    def migrate_config_data(from_ns, to_ns):
        configurations = ['URLConfig', 'PubSubConfig', 'SendGridConfig']

        for conf in configurations:
            url_entity = ndb.Key('ConfigData', conf, namespace=from_ns).get()
            url_entity.key = ndb.Key('ConfigData', conf, namespace=to_ns)
            url_entity.put()

    @staticmethod
    def migrate_frontend_data(from_ns, to_ns):
        entity = ndb.Key('FrontEndData', '1', namespace=from_ns).get()
        entity.key = ndb.Key('FrontEndData', '1', namespace=to_ns)
        entity.put()

    @staticmethod
    def migrate_member_data(from_ns, to_ns):
        ids = ['1', '7081327663412819', '3', '4']

        for idx in ids:
            entity = ndb.Key('MemberData', idx, namespace=from_ns).get()
            entity.key = ndb.Key('MemberData', idx, namespace=to_ns)
            entity.put()

    @staticmethod
    def migrate_sendgrid_data(from_ns, to_ns):
        entity = ndb.Key('SendgridData', '1', namespace=from_ns).get()
        entity.key = ndb.Key('SendgridData', '1', namespace=to_ns)
        entity.put()

    @staticmethod
    def migrate_endpoints_data(from_ns, to_ns):
        entity = ndb.Key('ServiceEndPointData', 'endpoints', namespace=from_ns).get()
        entity.key = ndb.Key('ServiceEndPointData', 'endpoints', namespace=to_ns)
        entity.put()

    @staticmethod
    def migrate_budata_data(from_ns, to_ns):
        ids = ['kmart', 'kmart_soar_numbers', 'sears', 'sears_soar_numbers']

        for idx in ids:
            entity = ndb.Key('BUData', idx, namespace=from_ns).get()
            entity.key = ndb.Key('BUData', idx, namespace=to_ns)
            entity.put()

    def get(self):
        from_ns = self.request.get('from_ns')
        to_ns = self.request.get('to_ns')
        # self.migrate_config_data(from_ns=from_ns, to_ns=to_ns)
        # self.migrate_frontend_data(from_ns=from_ns, to_ns=to_ns)
        # self.migrate_member_data(from_ns=from_ns, to_ns=to_ns)
        # self.migrate_sendgrid_data(from_ns=from_ns, to_ns=to_ns)
        # self.migrate_endpoints_data(from_ns=from_ns, to_ns=to_ns)
        self.migrate_budata_data(from_ns=from_ns, to_ns=to_ns)

        self.response.write("Data migrated successfully!!!")

class AllEvents(webapp2.RequestHandler):

    def post(self):
        logging.info(self.request.body)
        logging.info(self.request)
        json_data_list = json.loads(self.request.body)
        EmailEventMetricsDataService.save_allEventsData(json_data_list)


class GetAllEmailActivities(webapp2.RequestHandler):

    def get(self):
        query = EmailEventMetricsData.query().order(-EmailEventMetricsData.timestamp)
        activity_list = query.fetch(100)
        result = list()
        logging.info('len of the list: %s', len(activity_list))
        logging.info(activity_list)
        for each_entity in activity_list:

            activity_dict = dict()
            logging.info('each entry: %s', each_entity)
            logging.info('each entry email: %s', each_entity.email)
            activity_dict['email'] = each_entity.email
            activity_dict['timestamp'] = each_entity.timestamp
            activity_dict['smtp-id'] = each_entity.smtp_id
            activity_dict['event'] = each_entity.event
            activity_dict['sg_event_id'] = each_entity.sg_event_id
            activity_dict['sg_message_id'] = each_entity.sg_message_id
            activity_dict['response'] = each_entity.response
            activity_dict['attempt'] = each_entity.attempt
            activity_dict['useragent'] = each_entity.useragent
            activity_dict['ip'] = each_entity.ip
            activity_dict['url'] = each_entity.url
            activity_dict['reason'] = each_entity.reason
            activity_dict['status'] = each_entity.status
            activity_dict['asm_group_id'] = each_entity.asm_group_id

            result.append(activity_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))

class AllEvents(webapp2.RequestHandler):
    def post(self):
        logging.info(self.request.body)
        logging.info(self.request)
        json_data_list = json.loads(self.request.body)
        EmailEventMetricsDataService.save_allEventsData(json_data_list)


class GetAllEmailActivities(webapp2.RequestHandler):

    def get(self):
        query = EmailEventMetricsData.query().order(-EmailEventMetricsData.timestamp)
        activity_list = query.fetch(100)
        result = list()
        logging.info('len of the list: %s', len(activity_list))
        logging.info(activity_list)
        for each_entity in activity_list:

            activity_dict = dict()
            logging.info('each entry: %s', each_entity)
            logging.info('each entry email: %s', each_entity.email)
            activity_dict['email'] = each_entity.email
            activity_dict['timestamp'] = each_entity.timestamp
            activity_dict['smtp-id'] = each_entity.smtp_id
            activity_dict['event'] = each_entity.event
            activity_dict['sg_event_id'] = each_entity.sg_event_id
            activity_dict['sg_message_id'] = each_entity.sg_message_id
            activity_dict['response'] = each_entity.response
            activity_dict['attempt'] = each_entity.attempt
            activity_dict['useragent'] = each_entity.useragent
            activity_dict['ip'] = each_entity.ip
            activity_dict['url'] = each_entity.url
            activity_dict['reason'] = each_entity.reason
            activity_dict['status'] = each_entity.status
            activity_dict['asm_group_id'] = each_entity.asm_group_id

            result.append(activity_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps({'data': result}))

# [START app]
app = webapp2.WSGIApplication([
    ('/', IndexPageHandler),
    ('/saveCampaign', SaveCampaignHandler),
    ('/campaigns', GetAllCampaignsHandler),
    ('/activateOffer', ActivateOfferHandler),
    ('/getListItems', UIListItemsHandler),
    ('/getMetrics', MetricsHandler),
    ('/batchJob', BatchJobHandler),
    ('/uploadStoreIDs', UploadStoreIDHandler),
    ('/buNames', SoarBuHandler),
    ('/sendgridEvents', SendGridEvents),
    ('/migrateEntities', MigrateNamespaceData),
    ('/allEventsNotification', AllEvents),
    ('/getemailactivities', GetAllEmailActivities)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()
