import webapp2
from webapp2 import Route

app = webapp2.WSGIApplication([
    Route('/', handler='main.IndexPageHandler'),
    Route('/members', handler='main.AllMemberOffers'),
    Route('/getMember', handler='main.SingleMemberOffer'),
    Route('/kposOffer', handler='main.KPOSOfferHandler'),
    Route('/getModelData', handler='main.GetModelData'),
    Route('/updateEmailOfferIssuanceData', handler='main.UpdateEmailOfferIssuanceHandler'),
    Route('/updateEmailOfferActivationData', handler='main.UpdateEmailOfferActivationData'),
], debug=True)
