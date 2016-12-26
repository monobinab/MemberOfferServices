import webapp2
from webapp2 import Route

app = webapp2.WSGIApplication([
    Route('/', handler='main.IndexPageHandler'),
    Route('/members', handler='main.AllMemberOffersHandler'),
    Route('/getMember', handler='main.SingleMemberOfferHandler'),
    Route('/activateOffer', handler='main.ActivateOfferHandler'),
    Route('/kposOffer', handler='main.KPOSOfferHandler'),
    Route('/sendOffer', handler='main.SendOfferToMemberHandler'),
], debug=True)
