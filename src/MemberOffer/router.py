import webapp2
from webapp2 import Route

app = webapp2.WSGIApplication([
    Route('/', handler='main.IndexPageHandler'),
    Route('/members', handler='main.AllMemberOffers'),
    Route('/getMember', handler='main.SingleMemberOffer'),
    Route('/activateOffer', handler='main.ActivateEmailOffer'),
    Route('/kposOffer', handler='main.IssueActivateKPOSOffer'),
    Route('/sendOffer', handler='main.SendOfferToMember'),
    Route('/getModelData', handler='main.GetModelData'),
], debug=True)
