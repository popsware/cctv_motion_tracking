

import requests
from threading import Thread


class Requester(object):
    def __init__(self, source=0):
        print("init Requester Thread for requests")

    def post(self, url, params):
        print("Requester post to "+url)
        try:
            return requests.post(url, params)
        except Exception as e:
            print("caught error "+str(e))
            return None

    def request(self, method, url, headers, data):
        print("Requester "+method+" to "+url)
        try:
            return requests.request(method, url, headers, data)
        except:
            print
            return None
