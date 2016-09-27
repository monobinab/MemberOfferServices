from django.db import models
from django.contrib.auth.models import User
# from google.appengine.ext import ndb


# class Campaign(db.Model):
#     name = db.StringProperty(default="", required=True)
#     money = db.IntegerProperty(default=0, required=True)
#     category = db.StringProperty(default="", required=True)
#     conversion_ratio = db.IntegerProperty(default=0, required=True)
#     period = db.StringProperty(default="", required=True)
#     offer_list = db.ListProperty(required=False)
#     owner = db.StringProperty(default="", required=True)
#
#
# class Offers(db.Model):
#     offer_type = db.StringProperty()
#     max_per_member_issuance_frequency = db.StringProperty()
#     max_value = db.IntegerProperty(default=100)
#     min_value = db.IntegerProperty(default=0)
#     valid_till = db.StringProperty()


# # Create your models here.
class Campaign(models.Model):
    name = models.CharField(default="", max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    money = models.IntegerField(default=0)
    category = models.CharField(default="", max_length=64)
    conversion_ratio = models.IntegerField(default=0)
    period = models.CharField(default="", max_length=64)
    offer = models.ForeignKey('Offers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    @classmethod
    def create(cls, data, user):
        new_campaign = cls()
        new_offer = Offers.create(data)
        campaign_dict = data.get('campaign_details')
        new_campaign.name = campaign_dict['name']
        new_campaign.category = campaign_dict['category']
        new_campaign.conversion_ratio = campaign_dict['conversion_ratio']
        new_campaign.period = campaign_dict['period']
        new_campaign.money = campaign_dict['money']
        new_campaign.owner = user
        new_campaign.offer = new_offer
        new_campaign.save()

    @classmethod
    def update(cls, data, user):
        campaign_dict = data.get('campaign_details')
        new_campaign = Campaign.objects.get(pk=int(campaign_dict.get('campaign_id')))
        new_campaign.name = campaign_dict['name']
        new_campaign.category = campaign_dict['category']
        new_campaign.conversion_ratio = campaign_dict['conversion_ratio']
        new_campaign.period = campaign_dict['period']
        new_campaign.money = campaign_dict['money']
        new_campaign.owner = user
        # updated_offer = Offers.update(data)
        # new_campaign.offer = updated_offer
        new_campaign.save()

    def __str__(self):
        return self.name


class Offers(models.Model):
    offer_type = models.CharField(max_length=64, default="")
    max_per_member_issuance_frequency = models.CharField(max_length=128, default="")
    max_value = models.IntegerField(default=100)
    min_value = models.IntegerField(default=0)
    valid_till = models.DateTimeField(auto_now_add=False, auto_now=False)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    @classmethod
    def create(cls, data):
        new_offer = cls()
        offer_dict = data.get('offer_details')
        new_offer.offer_type = offer_dict['offer_type']
        new_offer.max_per_member_issuance_frequency = offer_dict['member_issuance']
        new_offer.max_value = offer_dict['max_value']
        new_offer.min_value = offer_dict['min_value']
        new_offer.valid_till = offer_dict['valid_till']
        new_offer.save()
        return new_offer

    @classmethod
    def update(cls, data):
        offer_dict = data.get('offer_details')
        new_offer = Offers.objects.get(pk=int(offer_dict.get('offer_id')))
        new_offer.offer_type = offer_dict['offer_type']
        new_offer.max_per_member_issuance_frequency = offer_dict['member_issuance']
        new_offer.max_value = offer_dict['max_value']
        new_offer.min_value = offer_dict['min_value']
        new_offer.valid_till = offer_dict['valid_till']
        new_offer.save()
        return new_offer

    def __str__(self):
        return self.name

