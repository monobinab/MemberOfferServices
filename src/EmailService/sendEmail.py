from sendgrid import sendgrid
from sendgrid.helpers import mail
from utilities import get_backend_host, get_sendgrid_configuration
import logging
from datetime import datetime
import os
from models import ConfigData, ndb, ServiceEndPointData, CampaignData, OfferData, MemberData

def email_process(member_id, offer_value, campaign_name ):
    campaign_key = ndb.Key('CampaignData', campaign_name)
    logging.info("fetched campaign_key for: %s", campaign_name)
    campaign = campaign_key.get()
    response_dict = dict()

    if campaign is None:
        logging.info("campaign is None")
        # TO DO: send response
        response_dict['message'] = "Error: Campaign not found"
        return response_dict
    else:
        logging.info("campaign is not None")
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
            # To check if this needed
            #offer = OfferDataService.create_offer_obj(campaign, offer_value)

            # HACK: Need to remove later. Only for testing purpose. <>
            if os.environ.get('NAMESPACE') in ['qa','dev']:
                member_id = '7081327663412819'

            member_key = ndb.Key('MemberData', member_id)
            logging.info("Fetched member_key for member: %s", member_id)

            member = member_key.get(use_datastore=True, use_memcache=False, use_cache=False)
            if member is None:
                logging.info("member is None")
                response_dict['message'] = "Member ID " + member_id + " not found in database."
            else:
                response = send_mail(member_entity=member, offer_entity=offer_entry, campaign_entity=campaign)
                if response.status_code == 202:
                    response_dict['message'] = "Success"
                else:
                    response_dict['message'] = "Error sending email. Response code: " + response.status_code

        return response_dict

def send_mail(member_entity, offer_entity, campaign_entity):
    member_dict = dict()
    member_dict['email'] = member_entity.email
    member_dict['name'] = member_entity.first_name + " " + member_entity.last_name
    member_dict['memberid'] = member_entity.member_id
    member_dict['fname'] = member_entity.first_name
    member_dict['lname'] = member_entity.last_name

    offer_dict = dict()
    date = offer_entity.OfferEndDate
    date_format = datetime.strptime(date, "%Y-%m-%d")
    date = date_format.strftime('%m/%d/%Y')

    offer_dict['surprisepoints'] = offer_entity.surprise_points
    offer_dict['threshold'] = offer_entity.threshold
    offer_dict['expiration'] = date
    offer_dict['offer_id'] = offer_entity.OfferNumber
    offer_dict['formatlevel'] = campaign_entity.format_level
    offer_dict['category'] = campaign_entity.category
    logging.info("Mail offer dict:: %s", offer_dict)
    response = send_template_message(member_dict, offer_dict)

    if response.status_code == 202:
        logging.info("***Response_Status_code:: %d" % response.status_code)
        logging.info("Mail has been sent successfully to %s" % member_entity.email)
    else:
        logging.info("Sendgrid response for member %s Response_Status_Code:: %s, Response_Headers:: %s,  Response_Body"
                     ":: %s" % (member_entity.email, response.status_code, response.headers, response.body))
        logging.error("Mail to %s has failed from sendgrid" % member_entity.email)

    return response


def send_template_message(member_dict, offer_dict):
    config_dict = get_sendgrid_configuration()

    sg = sendgrid.SendGridAPIClient(apikey=config_dict['SENDGRID_API_KEY'])
    to_email = mail.Email(member_dict['email'].encode("utf-8"))
    from_email = mail.Email(config_dict['SENDGRID_SENDER'].encode("utf-8"), 'Shop Your Way')
    subject = ' '
    content = mail.Content('text/html', '')
    message = mail.Mail(from_email, subject, to_email, content)
    message = mail.Mail()
    message.set_from(from_email)
    personalization = mail.Personalization()
    personalization.add_to(to_email)
    # https://syw-offers-services-qa-dot-syw-offers.appspot.com/
    activation_url = get_backend_host() + "activateOffer?offer_id=" + offer_dict['offer_id'].encode("utf-8") + "&&member_id=" + member_dict['memberid'].encode("utf-8")
    logging.info("Activation URL included in email::" + activation_url)

    substitution = mail.Substitution(key="%email%", value=member_dict['email'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%fname%", value=member_dict['fname'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%lname%", value=member_dict['lname'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%name%", value=member_dict['name'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%dollarsurprisepoints%", value=str(offer_dict['surprisepoints']).encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%expirationdate%", value=offer_dict['expiration'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%memberid%", value=member_dict['memberid'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%offerid%", value=offer_dict['offer_id'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%dollarthresholdvalue%", value='25')
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%activationurl%", value=activation_url.encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%category%", value=offer_dict['category'].encode("utf-8"))
    personalization.add_substitution(substitution)
    substitution = mail.Substitution(key="%formatlevel%", value=offer_dict['formatlevel'].encode("utf-8"))
    personalization.add_substitution(substitution)
    message.add_personalization(personalization)
    message.set_template_id(config_dict['TEMPLATE_ID'].split('\n')[0].encode("utf-8"))
    logging.info('message.get(): %s', message.get())

    response = sg.client.mail.send.post(request_body=message.get())

    return response
