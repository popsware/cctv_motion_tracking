

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

    def startMachine(self, machineid):
        if not machineid == 0:
            return requests.request(
                "GET", "http://localhost:50011/api/machine/"+str(machineid)+"/status/10", headers={'key': 'api_key'}, data={})

    def stopMachine(self, machineid):
        if not machineid == 0:
            return requests.request(
                "GET", "http://localhost:50011/api/machine/"+str(machineid)+"/status/0", headers={'key': 'api_key'}, data={})
