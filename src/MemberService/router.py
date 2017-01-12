import webapp2
from webapp2 import Route

app = webapp2.WSGIApplication([
    Route('/', handler='main.IndexPageHandler'),
    Route('/getMember', handler='main.SingleMemberOffer'),
    Route('/kposOffer', handler='main.KPOSOfferHandler'),
    Route('/getModelData', handler='main.ModelDataHandler'),
    Route('/updateEmailOfferIssuanceData', handler='main.UpdateEmailOfferIssuanceHandler'),
    Route('/updateEmailOfferActivationData', handler='main.UpdateEmailOfferActivationData'),
], debug=True)
