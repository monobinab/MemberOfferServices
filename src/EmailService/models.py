from google.appengine.ext import ndb


class CampaignData(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    money = ndb.IntegerProperty(indexed=False)
    category = ndb.StringProperty(indexed=True)
    divisions = ndb.StringProperty(indexed=False)  # New Column
    format_level = ndb.StringProperty(indexed=False)
    conversion_ratio = ndb.IntegerProperty(indexed=False)
    period = ndb.StringProperty(indexed=False)
    offer_type = ndb.StringProperty(indexed=False)
    max_per_member_issuance_frequency = ndb.StringProperty(indexed=False)
    max_value = ndb.IntegerProperty(indexed=False)
    min_value = ndb.IntegerProperty(indexed=False)
    store_location = ndb.StringProperty(indexed=False)
    valid_till = ndb.StringProperty(indexed=False)
    start_date = ndb.StringProperty(indexed=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class OfferData(ndb.Model):
    campaign = ndb.KeyProperty(kind="CampaignData")

    surprise_points = ndb.IntegerProperty(indexed=True)
    threshold = ndb.IntegerProperty(indexed=False)

    soar_no = ndb.IntegerProperty(indexed=True)

    OfferNumber = ndb.StringProperty(indexed=False)
    OfferPointsDollarName = ndb.StringProperty(indexed=False)
    OfferDescription = ndb.StringProperty(indexed=False)
    OfferType = ndb.StringProperty(indexed=False)
    OfferSubType = ndb.StringProperty(indexed=False)
    OfferStartDate = ndb.StringProperty(indexed=False)
    OfferStartTime = ndb.StringProperty(indexed=False)
    OfferEndDate = ndb.StringProperty(indexed=False)
    OfferEndTime = ndb.StringProperty(indexed=False)
    OfferBUProgram_BUProgram_BUProgramName = ndb.StringProperty(indexed=False)
    OfferBUProgram_BUProgram_BUProgramCost = ndb.FloatProperty(indexed=False)
    ReceiptDescription = ndb.StringProperty(indexed=False)
    OfferCategory = ndb.StringProperty(indexed=False)
    OfferAttributes_OfferAttribute_Name = ndb.StringProperty(indexed=False)
    OfferAttributes_OfferAttribute_Values_Value = ndb.StringProperty(indexed=False)
    Rules_Rule_Entity = ndb.StringProperty(indexed=False)
    Rules_Conditions_Condition_Name = ndb.StringProperty(indexed=False)
    Rules_Conditions_Condition_Operator = ndb.StringProperty(indexed=False)
    Rules_Conditions_Condition_Values_Value = ndb.StringProperty(indexed=False)
    RuleActions_ActionID = ndb.StringProperty(indexed=False)
    Actions_ActionID = ndb.StringProperty(indexed=False)
    Actions_ActionName = ndb.StringProperty(indexed=False)
    Actions_ActionProperty_PropertyType = ndb.StringProperty(indexed=False)
    Actions_ActionProperty_Property_Name = ndb.StringProperty(indexed=False)
    Actions_ActionProperty_Property_Values_Value = ndb.StringProperty(indexed=False)

    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class OfferDivisionMappingData(ndb.Model):
    offer = ndb.KeyProperty(kind="OfferData")
    offer_id = ndb.StringProperty(indexed=True)
    soar_no = ndb.IntegerProperty(indexed=True)
    division_no = ndb.IntegerProperty(indexed=True)
    campaign_name = ndb.StringProperty(indexed=True)
    offer_value = ndb.IntegerProperty(indexed=True)


class MemberData(ndb.Model):
    member_id = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)

    email = ndb.StringProperty(indexed=True)
    eml_opt_in = ndb.StringProperty(default='N')
    email_open = ndb.IntegerProperty(default=0)
    email_send = ndb.IntegerProperty(default=0)

    store_id = ndb.StringProperty(indexed=True)
    format_level = ndb.StringProperty(indexed=True)
    last_updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class MemberOfferData(ndb.Model):
    offer = ndb.KeyProperty(kind="OfferData")
    offer_id = ndb.StringProperty(indexed=False)

    member = ndb.KeyProperty(kind="MemberData")
    member_id = ndb.StringProperty(indexed=False)

    issuance_channel = ndb.StringProperty(indexed=True)
    issuance_date = ndb.DateTimeProperty(auto_now_add=True, indexed=True)

    activated_channel = ndb.StringProperty(indexed=True)
    activation_date = ndb.DateTimeProperty(indexed=True, default=None)

    redeemed = ndb.BooleanProperty(default=False)
    redeemed_date = ndb.DateTimeProperty(indexed=True)

    validity_start_date = ndb.DateTimeProperty(indexed=False)
    validity_end_date = ndb.DateTimeProperty(indexed=True)

    status = ndb.IntegerProperty(default=0)
    user_action_date = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class SendgridData(ndb.Model):
    SENDGRID_API_KEY = ndb.StringProperty(indexed=True)
    SENDGRID_SENDER = ndb.StringProperty(indexed=True)
    TEMPLATE_ID = ndb.StringProperty(indexed=False)


class ConfigData(ndb.Model):
    SENDGRID_API_KEY = ndb.StringProperty(indexed=True)
    SENDGRID_SENDER = ndb.StringProperty(indexed=True)
    TEMPLATE_ID = ndb.StringProperty(indexed=False)

    GENERATE_TOKEN_HOST = ndb.StringProperty(indexed=False)
    GENERATE_TOKEN_URL = ndb.StringProperty(indexed=False)

    TELLURIDE_CLIENT_ID = ndb.StringProperty(indexed=False)

    CREATE_OFFER_URL = ndb.StringProperty(indexed=False)
    CREATE_OFFER_REQUEST = ndb.StringProperty(indexed=False)

    ACTIVATE_OFFER_URL = ndb.StringProperty(indexed=False)
    ACTIVATE_OFFER_REQUEST = ndb.StringProperty(indexed=False)
    ACTIVATE_OFFER_PORT = ndb.StringProperty(indexed=False)

    REGISTER_OFFER_URL = ndb.StringProperty(indexed=False)
    REGISTER_OFFER_REQUEST = ndb.StringProperty(indexed=False)

    REDEEM_OFFER_REQUEST = ndb.StringProperty(indexed=False)

    SERVICE_TOPIC = ndb.StringProperty(indexed=False)
    PUBLISH_TOKEN = ndb.StringProperty(indexed=False)
    EMAIL_CHANNEL_OFFER_VALIDITY_DAYS = ndb.IntegerProperty(indexed=False)


class FrontEndData(ndb.Model):
    Categories = ndb.StringProperty(indexed=True, repeated=True)
    Conversion_Ratio = ndb.IntegerProperty(indexed=True, repeated=True)
    Offer_Type = ndb.StringProperty(indexed=False, repeated=True)
    Minimum_Surprise_Points = ndb.IntegerProperty(indexed=True)
    Maximum_Surprise_Points = ndb.IntegerProperty(indexed=True)
    Format_Level = ndb.StringProperty(indexed=True, repeated=True)


class StoreData(ndb.Model):
    Format_Level = ndb.StringProperty(indexed=True)
    Locations = ndb.StringProperty(indexed=False, repeated=True)


class BUData(ndb.Model):
    Format = ndb.StringProperty(indexed=True)
    Business_Units = ndb.StringProperty(indexed=True, repeated=True)


class ServiceEndPointData(ndb.Model):
    backend = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    telluride = ndb.StringProperty(indexed=True)
    member = ndb.StringProperty(indexed=True)


class EmailEventMetricsData(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    timestamp = ndb.IntegerProperty(indexed=True)
    smtp_id = ndb.StringProperty(indexed=False)
    event = ndb.StringProperty(indexed=True)
    category = ndb.StringProperty(indexed=True)
    sg_event_id = ndb.StringProperty(indexed=False)
    sg_message_id = ndb.StringProperty(indexed=False)
    response = ndb.StringProperty(indexed=False)
    attempt = ndb.StringProperty(indexed=False)
    useragent = ndb.StringProperty(indexed=False)
    ip = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    reason = ndb.StringProperty(indexed=True)
    status = ndb.StringProperty(indexed=False)
    asm_group_id = ndb.IntegerProperty(indexed=False)


class BuDvsnMappingData(ndb.Model):
    soar_no = ndb.IntegerProperty(indexed=True)
    soar_nm = ndb.StringProperty(indexed=True)
    format_level = ndb.StringProperty(indexed=True)

    fp_dvsn_desc = ndb.StringProperty(indexed=False)
    bus_nbr = ndb.IntegerProperty(indexed=True)
    unit_nbr = ndb.IntegerProperty(indexed=True)
    dvsn_nbr = ndb.IntegerProperty(indexed=True)
    # dept_nbr = ndb.StringProperty(indexed=False)
    # catg_cluster_nbr = ndb.StringProperty(indexed=False)
    # catg_nbr = ndb.StringProperty(indexed=False)
    # sub_catg_nbr = ndb.StringProperty(indexed=False)
    product_hierarchy = ndb.StringProperty(indexed=False)


class ModelData(ndb.Model):
    campaign_name = ndb.StringProperty(indexed=True)
    div_no = ndb.IntegerProperty(indexed=True)
    div_name = ndb.StringProperty(indexed=False)
    offer_value = ndb.IntegerProperty(indexed=True)
    member_id = ndb.StringProperty(indexed=True)
    store_id = ndb.StringProperty(indexed=True)
    created_at = ndb.DateTimeProperty(indexed=False)

