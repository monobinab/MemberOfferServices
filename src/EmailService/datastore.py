import logging
from datetime import datetime, timedelta
from google.appengine.api import datastore_errors
from models import CampaignData, OfferData, MemberOfferData, EmailEventMetricsData, ndb, BuDvsnMappingData


class OfferDataService(CampaignData):
    @classmethod
    def create_offer_obj(cls, campaign, offer_value, rules_condition):
        campaign_key = ndb.Key('CampaignData', campaign.name)

        start_date = campaign.start_date
        # Calculating end date based on validity value which is in weeks.
        end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=7*int(campaign.valid_till) - 1)
        end_date = end_date.strftime("%Y-%m-%d")
        logging.info("Offer Start_date:: %s and end_date %s", start_date, end_date)

        offer_name = "%s_%s" % (str(campaign.name), str(offer_value))

        category_list = campaign.category.split('-')
        logging.info("Category list:: %s", category_list)
        logging.info("BU Name:: %s", ",".join(category_list[1]))
        BU_NAME = category_list[1]
        offer_obj = OfferData(surprise_points=int(offer_value), threshold=10, OfferNumber=offer_name,
                              OfferPointsDollarName=offer_name, OfferDescription=offer_name,
                              OfferType="Xtreme Redeem", OfferSubType="Item", OfferStartDate=start_date,
                              OfferStartTime="00:00:00", OfferEndDate=end_date, OfferEndTime="23:59:00",
                              OfferBUProgram_BUProgram_BUProgramName="BU - "+BU_NAME,
                              OfferBUProgram_BUProgram_BUProgramCost=0.00, ReceiptDescription="TELL-16289",
                              OfferCategory="Stackable", OfferAttributes_OfferAttribute_Name="MULTI_TRAN_IND",
                              OfferAttributes_OfferAttribute_Values_Value="N", Rules_Rule_Entity="Product",
                              Rules_Conditions_Condition_Name="PRODUCT_LEVEL",
                              Rules_Conditions_Condition_Operator="IN",
                              Rules_Conditions_Condition_Values_Value=rules_condition,
                              RuleActions_ActionID="ACTION-1", Actions_ActionID="ACTION-1",
                              Actions_ActionName="XR",
                              Actions_ActionProperty_PropertyType="Tier",
                              Actions_ActionProperty_Property_Name="MIN",
                              Actions_ActionProperty_Property_Values_Value="0.01",
                              created_at=datetime.now())
        offer_obj.key = ndb.Key('OfferData', offer_name)
        offer_obj.campaign = campaign_key

        return offer_obj

    @classmethod
    def save_offer(cls, campaign, offer_value, rules_condition):
        response_dict = dict()
        offer = OfferDataService.create_offer_obj(campaign, offer_value, rules_condition)
        response_dict['offer'] = offer

        try:
            offer_key = offer.put()
            logging.info("Offer created:: %s", offer_key)
            logging.info("OfferNumber:: %s", offer.OfferNumber)
            response_dict['message'] = 'success'
            return response_dict
        except datastore_errors.Timeout:
            logging.exception('Put failed Timeout')
            response_dict['message'] = 'error'
            return response_dict
        except datastore_errors.TransactionFailedError:
            logging.exception('Put failed TransactionFailedError')
            response_dict['message'] = 'error'
            return response_dict
        except datastore_errors.InternalError:
            logging.exception('Put failed InternalError')
            response_dict['message'] = 'error'
            return response_dict


class CampaignDataService(CampaignData):
    DEFAULT_CAMPAIGN_NAME = 'default_campaign'

    @classmethod
    def get_campaign_key(cls, campaign_name=DEFAULT_CAMPAIGN_NAME):
        return ndb.Key('CampaignData', campaign_name)

    @classmethod
    # @ndb.transactional(xg=True)
    def save_campaign(cls, json_data, created_time):
        campaign_dict = json_data['campaign_details']
        offer_dict = json_data['offer_details']

        campaign_name = campaign_dict['name']
        campaign_budget = int(campaign_dict['money'])

        campaign_category = campaign_dict['category']

        campaign_format_level = campaign_dict['format_level'] if campaign_dict['format_level'] is not None else ""
        campaign_convratio = int(campaign_dict['conversion_ratio'])

        store_location = campaign_dict['store_location'] if campaign_dict['store_location'] is not None else ""
        campaign_period = campaign_dict['period']
        start_date = campaign_dict['start_date']

        offer_type = offer_dict['offer_type']
        offer_min_val = int(offer_dict['min_value'])
        offer_max_val = int(offer_dict['max_value'])
        offer_valid_till = offer_dict['valid_till']
        offer_mbr_issuance = offer_dict['member_issuance']
        campaign = CampaignData(name=campaign_name, money=campaign_budget, category=campaign_category,
                                format_level=campaign_format_level, conversion_ratio=campaign_convratio,
                                period=campaign_period, offer_type=offer_type,
                                max_per_member_issuance_frequency=offer_mbr_issuance, max_value=offer_max_val,
                                min_value=offer_min_val, store_location=store_location, valid_till=offer_valid_till, start_date=start_date)

        campaign.key = CampaignDataService.get_campaign_key(campaign_name)
        campaign_key = campaign.put()
        logging.info('campaign_key:: %s', campaign_key)

        rules_condition = ""
        if campaign.format_level == 'Sears':
            rules_condition = "SEARSLEGACY~803~~~~~~" if campaign.category == "Apparel" else \
                "SEARSLEGACY~803~615~~~~~~"
        elif campaign.format_level == 'Kmart':
            # If more than one category is selected we need to add all prod hierarchy for
            # both the soar numbers
            category_list = campaign_category.split('-')
            logging.info("Category list:: %s", category_list)
            product_hierarchy_list = list()
            logging.info("SOAR_NO:: %s", category_list[0])
            mapping_list = BuDvsnMappingData.query(BuDvsnMappingData.soar_no == int(category_list[0])).fetch()
            logging.info("Number of mappings found:: %s", len(mapping_list))
            for each_entity in mapping_list:
                product_hierarchy_list.append(each_entity.product_hierarchy)
            product_hierarchy_list = list(set(product_hierarchy_list))
            logging.info("List:: %s", product_hierarchy_list)
            rules_condition = ",".join(product_hierarchy_list)
            logging.info("Rules condition:: %s", rules_condition)

        # Creating offers from min values to max values
        for surprise_point in range(offer_min_val, offer_max_val+1):
            OfferDataService.save_offer(campaign, surprise_point, rules_condition)


class MemberOfferDataService(MemberOfferData):
    date_format = '%Y-%m-%d'

    @classmethod
    def create(cls, offer_entity, member_entity, channel, reg_start_date, reg_end_date, offer_id, member_id):
        reg_start_datetime = datetime.strptime(reg_start_date, "%Y-%m-%d")
        reg_end_datetime = datetime.strptime(reg_end_date, "%Y-%m-%d")

        member_offer_data = MemberOfferData(offer=offer_entity.key,
                                            member=member_entity.key,
                                            status=0,
                                            issuance_date=datetime.now(),
                                            issuance_channel=channel.upper(),
                                            validity_start_date=reg_start_datetime,
                                            validity_end_date=reg_end_datetime,
                                            offer_id=offer_id, member_id=member_id)

        member_offer_data.key = ndb.Key('MemberOfferData', offer_entity.key.id() + "_" + member_entity.key.id())

        member_offer_data_key = member_offer_data.put()
        return member_offer_data_key

    @classmethod
    def create_object(cls, offer_id, member_id, issuance_channel, start_date, end_date):
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
                                            issuance_channel=issuance_channel.upper())
        return member_offer_data

    @classmethod
    def get_offer_metrics(cls, campaign_id):
        response_dict = dict()
        if campaign_id is not None:
            campaign_key = ndb.Key('CampaignData', campaign_id)
            if campaign_key.get() is not None:
                offer_list = OfferData.query(OfferData.campaign == campaign_key).fetch()
                if len(offer_list) != 0:
                    logging.info("Total offers found for the campaign %d" % len(offer_list))
                    redeem_count = 0
                    non_redeem_count = 0
                    for each_offer in offer_list:
                        result = MemberOfferData.query(MemberOfferData.offer == each_offer.key).fetch()
                        logging.info(
                            "Total member-offers found for the offer %s are %d" % (each_offer.key, len(result)))

                        for each_entity in result:
                            if each_entity.status > 0:
                                redeem_count += 1
                            else:
                                non_redeem_count += 1
                    offer_dict = dict()
                    offer_dict['Redeem_Count'] = redeem_count
                    offer_dict['Not_Redeem_Count'] = non_redeem_count
                    offer_dict['Offers_Created'] = len(offer_list)
                    offer_dict['Offers_Activated'] = len(offer_list)

                    email_dict = dict()
                    email_dict['Emails_Sent'] = redeem_count + non_redeem_count
                    email_dict['Emails_Opened'] = redeem_count
                    email_dict['Emails_Unopened'] = non_redeem_count
                    email_dict['Emails_Click_Rate'] = redeem_count

                    response_dict['offer_metrics'] = offer_dict
                    response_dict['email_metrics'] = email_dict
                    response_dict['message'] = 'Metrics details fetched successfully.'
                    response_dict['status'] = 'Success'
                else:
                    response_dict['message'] = 'No offers are associated with this campaign.'
                    response_dict['status'] = 'Failure'
            else:
                response_dict['message'] = 'Campaign details not found.'
                response_dict['status'] = 'Failure'
        else:
            response_dict['message'] = 'Please provide campaign id.'
            response_dict['status'] = 'Failure'
        return response_dict

    @classmethod
    def create_response_object(cls, item):
        response_dict = dict()
        response_dict["member_id"] = item.member_id
        response_dict["status"] = item.status if item.status is not None else 0
        response_dict["offer_id"] = item.offer_id
        response_dict["issuance_date"] = item.issuance_date.strftime(MemberOfferDataService.date_format) if \
            item.issuance_date is not None else None

        response_dict["activation_date"] = item.activation_date.strftime(MemberOfferDataService.date_format) if \
            item.activation_date is not None else None

        response_dict["user_action_date"] = item.user_action_date.strftime(MemberOfferDataService.date_format) if \
            item.user_action_date is not None else None

        response_dict["validity_end_date"] = item.validity_end_date.strftime(MemberOfferDataService.date_format) if \
            item.validity_end_date is not None else None

        response_dict["redeemed_date"] = item.redeemed_date.strftime(MemberOfferDataService.date_format) if \
            item.redeemed_date is not None else None

        response_dict["redeemed"] = item.redeemed
        response_dict["validity_start_date"] = item.validity_start_date.strftime(MemberOfferDataService.date_format) if \
            item.validity_start_date is not None else None

        response_dict["activated_channel"] = item.activated_channel
        response_dict["issuance_date"] = item.issuance_date.strftime(MemberOfferDataService.date_format) if \
            item.issuance_date is not None else None
        response_dict["issuance_channel"] = str(item.issuance_channel)

        offer = item.offer.get()
        campaign = offer.campaign.get()
        logging.info("Campaign :: %s ", campaign.to_dict())
        response_dict["offer_value"] = offer.surprise_points
        response_dict["category"] = campaign.category

        soar_no = campaign.category.split('-', 1)[0]
        soar_name = campaign.category.split('-', 1)[1]
        logging.info("Soar number from campaign category :: %s", soar_no)
        logging.info("Soar name from campaign category :: %s", soar_name)

        bu_entities = BuDvsnMappingData.query(BuDvsnMappingData.soar_no == int(soar_no)).fetch()
        division_nos = list()
        division_names = list()

        for entity in bu_entities:
            division_nos.append(entity.dvsn_nbr)
            division_names.append(entity.fp_dvsn_desc)

        logging.info("Division numbers :: %s", division_nos)
        response_dict["div_no"] = division_nos
        response_dict["div_name"] = division_names

        return response_dict


class EmailEventMetricsDataService(EmailEventMetricsData):
    @classmethod
    def get_emailActivity_key(cls):
        return ndb.Key('EmailEventMetricsData')

    @classmethod
    @ndb.transactional(xg=True)
    def save_allEventsData(cls, json_data_list):
        logging.info('list data :: %s', json_data_list)
        for activity_dict in json_data_list:
            logging.info('Json data:: %s', activity_dict)
            email = activity_dict['email']
            timestamp = activity_dict.get('timestamp',None)
            smtp_id = activity_dict.get('smtp_id',None)
            event = activity_dict.get('event',None)
            category = activity_dict.get('category',None)
            sg_event_id = activity_dict.get('sg_event_id',None)
            sg_message_id = activity_dict.get('sg_message_id',None)
            response = activity_dict.get('response',None)
            attempt = activity_dict.get('attempt',None)
            useragent = activity_dict.get('useragent',None)
            ip = activity_dict.get('ip',None)
            url = activity_dict.get('url',None)
            reason = activity_dict.get('reason',None)
            status = activity_dict.get('status',None)
            asm_group_id = activity_dict.get('asm_group_id',None)
            memberActivity = EmailEventMetricsData(
                category=category,
                email=email,
                timestamp=timestamp,
                smtp_id=smtp_id,
                event=event,
                sg_event_id=sg_event_id,
                sg_message_id=sg_message_id,
                response=response,
                attempt=attempt,
                useragent=useragent,
                ip=ip,
                url=url,
                reason=reason,
                status=status,
                asm_group_id=asm_group_id
            )

            memberActivity_key = memberActivity.put()
            logging.info('memberActivity_key:: %s', memberActivity_key)
