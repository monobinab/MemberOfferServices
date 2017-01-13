import sys
import logging
from utilities import make_request, get_telluride_host, get_email_host, get_emailconfig_data, get_member_offer_host
import json
from datetime import datetime, timedelta

class member_state_api_interface():
    def get_member_state(self, member_id):
        self.member_id = member_id
        host = get_member_offer_host()
        relative_url = str("getMember?member_id=" + member_id)
        result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
        try:
            response_state = json.loads(result)
        except ValueError, e:
            logging.info("Member state response not a valid json")
            response_state = {}

        return response_state

    def get_detail(self, prop, response_state) :
    	if prop in response_state :
    		return response_state[prop]
    	for each_prop in response_state :
    		val = response_state[each_prop]
    		if isinstance(val, list) :
    			for element in response_state[each_prop] :
    				ret = self.get_detail(prop, element)
    				if ret :
    					return ret
    		if isinstance(val, dict) :
    			ret = self.get_detail(prop, val)
    			if ret :
    				return ret
    	return {}

class member_update_state_api_interface():
    def update_member_state(self, member_id, campaign_name, amount):
        host = get_member_offer_host()
        offer_id = "{}_{}".format(str(campaign_name), str(amount))
        reg_start_date_full = datetime.now()
        reg_start_date = reg_start_date_full.strftime("%Y-%m-%d")
        emailChannel_config = get_emailconfig_data()
        offer_validity_days = emailChannel_config.EMAIL_CHANNEL_OFFER_VALIDITY_DAYS
        reg_end_date_full = reg_start_date_full + timedelta(days=offer_validity_days)
        reg_end_date = reg_end_date_full.strftime("%Y-%m-%d")
        channel = 'Email'

        relative_url = str("updateEmailOfferIssuanceData?offer_id=" + offer_id +
                           "&&member_id=" + member_id +
                           "&&reg_start_date=" + reg_start_date +
                           "&&reg_end_date=" + reg_end_date +
                           "&&channel=" + channel)

        logging.info("Email URL :: %s%s", host, relative_url)
        offer_issuance_result = make_request(host=host, relative_url=relative_url, request_type="GET", payload='')
        logging.info("offer_issuance_result :: %s", offer_issuance_result)
        return offer_issuance_result
