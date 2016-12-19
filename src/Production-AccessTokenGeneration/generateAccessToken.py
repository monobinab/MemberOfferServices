import sys
sys.path.insert(0, 'lib')
import webapp2
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import json
import time
import logging
import httplib
from google.appengine.api import urlfetch
import urllib

class GenerateAccessTokenHandler(webapp2.RequestHandler):
    @classmethod
    def sign_data(cls, private_key, data):
        rsakey = RSA.importKey(private_key,passphrase=None)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(data)
        sign = signer.sign(digest)
        return base64.b64encode(sign)

    def get(self):
        header = """{"alg":"SHA256withRSA","typ":"JWT"})"""
        logging.info('header:: %s', header)
        encoded_header = base64.b64encode(bytearray(header))
        logging.info('encoded_header:: %s', encoded_header)

        issuance_time = int(round(time.time() * 1000))
        #exp_time =  issuance_time + 7200000

        claim = """{
           "iss":"OFFER_REC_SYS",
           "aud":"https://oauthas.searshc.com/oauthAS/service/oAuth/token.json",
           "exp":"""+str(issuance_time)+""",
           "iat":"""+str(issuance_time)+"""}"""
        logging.info('claim:: %s', claim)
        encoded_claim = base64.b64encode(bytearray(claim))
        logging.info('encoded_claim:: %s', encoded_claim)

        combined_header_claim = encoded_header + "." + encoded_claim
        input_signature = bytearray(combined_header_claim)
        logging.info('input_signature:: %s', input_signature)

        RSA_PRIVATE_KEY = open('privateKey.properties').read()
        logging.info('RSA_PRIVATE_KEY:: %s', RSA_PRIVATE_KEY)


        encoded_sign = GenerateAccessTokenHandler.sign_data(RSA_PRIVATE_KEY, input_signature)
        logging.info('encoded_sign:: %s', encoded_sign)


        jwt = str(encoded_header + "." + encoded_claim + "."+ encoded_sign)
        logging.info('jwt:: %s', jwt)

        payload = """{"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer","assertion":\""""+jwt+"""\"}"""
        request_header = {"content-type": "application/json"}

        logging.info('payload:: %s', payload)

        #https://trstoaapp1.vm.itg.corp.us.shldcorp.com:8553/oauthAS/service/oAuth/token.json

        try:
            retry_count = 5
            count = 1
            while(count <= retry_count):
                headers = {'Content-Type': 'application/json'}
                urlfetch.set_default_fetch_deadline(10)
                result = urlfetch.fetch(
                    url='https://oauthas.searshc.com/oauthAS/service/oAuth/token.json',
                    payload=payload,
                    method=urlfetch.POST,
                    headers=headers)
                logging.info('****Try #: %s', count)
                logging.info('****result.status_code: %s', result.status_code)
                logging.info('****result.content: %s', result.content)
                if(result.status_code != 200):
                    count = count + 1
                    continue
                else:
                    break

            self.response.write(result.content)
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')


# [START app]
app = webapp2.WSGIApplication([
    ('/generateAccessToken', GenerateAccessTokenHandler)
], debug=True)

# [END app]


def main():
    app.run()


if __name__ == '__main__':
    main()
