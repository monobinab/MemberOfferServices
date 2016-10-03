from google.appengine.ext import ndb


class CampaignData(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    money = ndb.IntegerProperty(indexed=False)
    category = ndb.StringProperty(indexed=True)
    conversion_ratio = ndb.IntegerProperty(indexed=False)
    period = ndb.StringProperty(indexed=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class OfferData(ndb.Model):
    campaign = ndb.KeyProperty(kind="CampaignData")
    offer_number = ndb.StringProperty(indexed=False)
    offer_points = ndb.StringProperty(indexed=False)
    surprise_points = ndb.IntegerProperty(indexed=True)
    expiration_date = ndb.StringProperty(indexed=True)
    threshold = ndb.IntegerProperty(indexed=True)
    offer_type = ndb.StringProperty(indexed=True)
    max_per_member_issuance_frequency = ndb.StringProperty(indexed=False)
    max_value = ndb.IntegerProperty(indexed=False)
    min_value = ndb.IntegerProperty(indexed=False)
    valid_till = ndb.StringProperty(indexed=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)


class MemberData(ndb.Model):
    member_id = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    address = ndb.StringProperty(indexed=False)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)


class MemberOfferData(ndb.Model):
    offer = ndb.KeyProperty(OfferData)
    member = ndb.KeyProperty(MemberData)
    status = ndb.StringProperty(default="PENDING")
    created_at = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated_at = ndb.DateTimeProperty(auto_now=True, auto_now_add=False)