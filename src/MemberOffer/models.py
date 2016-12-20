from google.appengine.ext import ndb


class CampaignData(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    money = ndb.IntegerProperty(indexed=False)
    category = ndb.StringProperty(indexed=True)
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

    surprise_points = ndb.IntegerProperty(indexed=False)
    threshold = ndb.IntegerProperty(indexed=False)

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


class MemberData(ndb.Model):
    member_id = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    address = ndb.StringProperty(indexed=False)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)


class MemberOfferData(ndb.Model):
    offer = ndb.KeyProperty(kind="OfferData")
    member = ndb.KeyProperty(kind="MemberData")
    status = ndb.BooleanProperty(default=False)
    channel = ndb.StringProperty(indexed=True)
    email_sent_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    activated_at = ndb.DateTimeProperty(indexed=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


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


class MemberDataMS(ndb.Model):
    member_id = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    address = ndb.StringProperty(indexed=False)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    email_opted_in = ndb.BooleanProperty(default=False)


class MemberOfferDataMS(ndb.Model):
    offer = ndb.KeyProperty(kind="OfferData")
    member = ndb.KeyProperty(kind="MemberDataMS")
    issuance_date = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    issuance_channel = ndb.StringProperty(indexed=True)
    activated_channel = ndb.StringProperty(indexed=True)
    activated_date = ndb.DateTimeProperty(indexed=True)
    redeemed = ndb.BooleanProperty(default=False)
    redeemed_date = ndb.DateTimeProperty(indexed=True)
    validity_start_date = ndb.DateTimeProperty(indexed=False)
    validity_end_date = ndb.DateTimeProperty(indexed=True)
    status = ndb.BooleanProperty(default=False)
