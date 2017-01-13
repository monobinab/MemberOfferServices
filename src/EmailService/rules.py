import sys
import logging
from utilities import make_request, get_member_offer_host
import json
from datetime import datetime, timedelta

class email_rules():
    def apply_rules(self,member_state_data) :
        email_opt_in = self.isEmailOptIn(member_state_data)
        recent_activity = self.isRecentActivity(member_state_data)
        ready = self.isIssueReady(member_state_data)
        logging.info("email_opt_in: %s ,  recent_activity: %s ,  ready: %s", email_opt_in, recent_activity, ready)

        if email_opt_in and recent_activity and ready:
            return True
        else:
            return False

    def isEmailOptIn(self, member_state_data) :
        member_detail = self.get_detail("member_details", member_state_data)
        if 'eml_opt_in' in member_detail:
            member_eml_opt_in = member_detail["eml_opt_in"]
        else:
            member_eml_opt_in = False
        logging.info("member_detail eml_opt_in: %s", member_eml_opt_in)

        if member_eml_opt_in == True or member_eml_opt_in == 'Y':
            return True
        else:
            return False

    def isRecentActivity(self, member_state_data) :
        member_detail = self.get_detail("member_details", member_state_data)
        if 'email_send' in member_detail:
            member_eml_send = member_detail["email_send"]
        else:
            member_eml_send = '0'

        if 'email_open' in member_detail:
            member_eml_open = member_detail["email_open"]
        else:
            member_eml_open = '0'

        logging.info("member_detail member_eml_send: %s, member_eml_open: %s", member_eml_send, member_eml_open)

        #member_eml_send = '7'
        #member_eml_open = '2'

        if int(member_eml_send) > 0 and int(member_eml_open) > 0:
            return True
        else:
            return False

    def isIssueReady(self, member_state_data) :
        #offer_detail = self.get_detail("offer_details", response_state)
        latest_offer_issued = self.get_detail("latest_offer_issued", member_state_data)
        is_offer_issued = bool(latest_offer_issued)
        if is_offer_issued:
            if 'validity_end_date' in latest_offer_issued:
                offer_validity_end_date = latest_offer_issued["validity_end_date"]
            else:
                return False

            logging.info("offer_validity_end_date: %s", offer_validity_end_date)
            #current_date = datetime.now().strftime('%Y-%m-%d %H:%m')
            current_date = datetime.now()
            #current_date = current_date_full.strftime('%Y-%m-%d %H:%m')
            logging.info("current_date: %s", current_date)

            validity_end_date = datetime.strptime(offer_validity_end_date, '%Y-%m-%d')

            offer_validity_end_past6days = validity_end_date + timedelta(days=6)
            logging.info("offer_validity_end_past6days: %s", offer_validity_end_past6days)

            if current_date > offer_validity_end_past6days:
                return True
            else:
                return False
        else:
            return True


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
