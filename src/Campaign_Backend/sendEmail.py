from sendgrid import sendgrid
from sendgrid.helpers import mail
import Utilities
import webapp2
import sys
import httplib
import logging
import json, xml.etree.ElementTree as ET
from google.appengine.ext import ndb
from models import CampaignData, OfferData, MemberData, MemberOfferData, ndb
import os


def offer_email(campaign_id):
    campaign_key = ndb.Key('CampaignData', campaign_id)
    member_emails = ''
    fetch_offers = OfferData.query(OfferData.campaign == campaign_key)
    is_entity = fetch_offers.get()

    if is_entity is None:
        logging.info('Could not fetch required offers for the campaign: %s', campaign_id)
        obj = {'status': 'Failure', 'message': 'Could not fetch required offers for the campaign'}
        return obj
    else:
        logging.info('Fetched offers for the campaign: %s', campaign_id)
        members = MemberData.query()
        for offer_entity in fetch_offers.iter():
            for member_entity in members.iter():
                send_mail(member_entity, offer_entity)
                member_offer_data = MemberOfferData(offer=offer_entity.key, member=member_entity.key, status=False)
                member_offer_data_key = member_offer_data.put()
                logging.info('member_offer_key:: %s', member_offer_data_key)
                if member_entity.email not in member_emails:
                        member_emails = member_emails + member_entity.email + ' '

        logging.info('Offer emails have been sent to: : %s', member_emails)
        obj = {'status': 'Success', 'message': 'Offer emails have been sent to: ' + member_emails}
        return obj


def send_mail(member_entity, offer_entity):
    member_dict = dict()
    member_dict['email'] = member_entity.email
    member_dict['name'] = member_entity.first_name + " " + member_entity.last_name
    member_dict['memberid'] = member_entity.member_id

    offer_dict = dict()
    offer_dict['surprisepoints'] = offer_entity.surprise_points
    offer_dict['threshold'] = offer_entity.threshold
    offer_dict['expiration'] = offer_entity.OfferEndDate
    offer_dict['offer_id'] = offer_entity.OfferNumber

    response = send_template_message(member_dict, offer_dict)
    # logging.info("Sendgrid response for member %s Response_Status_Code:: %s, Response_Headers:: %s,  "
    #              "Response_Body:: %s" % (member_entity.email, response.status_code, response.headers, response.body))

    if response.status_code == 202:
        logging.info("Mail has been sent successfully to %s" % member_entity.email)
    else:
        logging.info("Sendgrid response for member %s Response_Status_Code:: %s, Response_Headers:: %s,  Response_Body"
                     ":: %s" % (member_entity.email, response.status_code, response.headers, response.body))
        logging.error("Mail to %s has failed from sendgrid" % member_entity.email)


def send_template_message(member_dict, offer_dict):
    config_dict = Utilities.get_configuration()
    # logging.info("config_dict[SENDGRID_API_KEY]::" + config_dict['SENDGRID_API_KEY'])

    sg = sendgrid.SendGridAPIClient(apikey=config_dict['SENDGRID_API_KEY'])
    to_email = mail.Email(member_dict['email'].encode("utf-8"))
    from_email = mail.Email(config_dict['SENDGRID_SENDER'].encode("utf-8"))
    subject = ' '
    content = mail.Content('text/html', '')
    message = mail.Mail(from_email, subject, to_email, content)
    message = mail.Mail()
    message.set_from(from_email)
    personalization = mail.Personalization()
    personalization.add_to(to_email)
    # https://syw-offers-services-qa-dot-syw-offers.appspot.com/
    activation_url = "https://" + os.environ['CURRENT_VERSION_ID'].split('.')[0] + "-dot-syw-offers.appspot.com/" \
                     "activateOffer?offer_id=" + offer_dict['offer_id'].encode("utf-8") + "&&member_id=" + member_dict['memberid'].encode("utf-8")

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
    message.add_personalization(personalization)
    message.set_template_id(config_dict['TEMPLATE_ID'].encode("utf-8"))
    logging.info("Activation URL included in email::" + activation_url)
    logging.info('message.get(): %s', message.get())

    response = sg.client.mail.send.post(request_body=message.get())

    return response
