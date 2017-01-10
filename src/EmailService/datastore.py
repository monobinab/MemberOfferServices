from models import CampaignData, OfferData, MemberOfferData, MemberData, ndb
import logging
from datetime import datetime, timedelta
from google.appengine.api import datastore_errors


class OfferDataService(CampaignData):
    @classmethod
    def create_offer_obj(cls, campaign, offer_value):
        campaign_key = ndb.Key('CampaignData', campaign.name)

        start_date = campaign.start_date
        # Calculating end date based on validity value which is in weeks.
        end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=7 * int(campaign.valid_till) - 1)
        end_date = end_date.strftime("%Y-%m-%d")
        logging.info("Offer Start_date:: %s and end_date %s", start_date, end_date)

        offer_name = "%s_%s" % (str(campaign.name), str(offer_value))
        rules_condition = ""
        if campaign.format_level == 'Sears':
            rules_condition = "SEARSLEGACY~803~~~~~~" if campaign.category == "Apparel" else \
                "SEARSLEGACY~803~615~~~~~~"
        elif campaign.format_level == 'Kmart':
            rules_condition = "KMARTSHC~1~35~~~~~~"
        offer_obj = OfferData(surprise_points=int(offer_value), threshold=10, OfferNumber=offer_name,
                              OfferPointsDollarName=offer_name, OfferDescription=offer_name,
                              OfferType="Xtreme Redeem", OfferSubType="Item", OfferStartDate=start_date,
                              OfferStartTime="00:00:00", OfferEndDate=end_date, OfferEndTime="23:59:00",
                              OfferBUProgram_BUProgram_BUProgramName="BU - "+campaign.category,
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
    def save_offer(cls, campaign, offer_value):
        response_dict = dict()

        offer = OfferDataService.create_offer_obj(campaign, offer_value)
        response_dict['offer'] = offer

        try:
            offer_key = offer.put()
            logging.info('Offer created in datastore with key:: %s', offer_key)
            # TellurideService.create_offer(offer)
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


class MemberOfferDataService(MemberOfferData):
    @classmethod
    def create(cls, offer_entity, member_entity, channel, reg_start_date, reg_end_date):
        reg_start_datetime = datetime.strptime(reg_start_date, "%Y-%m-%d")
        reg_end_datetime = datetime.strptime(reg_end_date, "%Y-%m-%d")

        member_offer_data = MemberOfferData(offer=offer_entity.key, member=member_entity.key, status=False,
                                            email_sent_at=datetime.now(), channel=channel,
                                            validity_start_date=reg_start_datetime, validity_end_date=reg_end_datetime)
        member_offer_data_key = member_offer_data.put()
        return member_offer_data_key

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
                        logging.info("Total member-offers found for the offer %s are %d" % (each_offer.key, len(result)))

                        for each_entity in result:
                            if each_entity.status:
                                redeem_count += 1
                            else:
                                non_redeem_count += 1
                    offer_dict = dict()
                    offer_dict['Redeem_Count'] = redeem_count
                    offer_dict['Not_Redeem_Count'] = non_redeem_count
                    offer_dict['Offers_Created'] = len(offer_list)
                    offer_dict['Offers_Activated'] = len(offer_list)

                    email_dict = dict()
                    email_dict['Emails_Sent'] = redeem_count+non_redeem_count
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
