import requests
from threading import Thread
from configparser import ConfigParser

# ---------------------------------------------------------------------------
# Constants -----------------------------------------------------------------
# ---------------------------------------------------------------------------
STATUS_RESET = 0
STATUS_STOPPED = 10
STATUS_STARTED = 20

# ---------------------------------------------------------------------------
# Configuration -------------------------------------------------------------
# ---------------------------------------------------------------------------
config_network = ConfigParser()
config_network.read("config/config_network.ini")
API_KEY = config_network.get("factsystem", "API_KEY")
API_URL = config_network.get("factsystem", "API_URL")
print("Network Config Initialized @ Requester")


class Requester(object):
    machineid = 0

    def __init__(self, machineid):
        print("Requester init Thread for requests with machineid " + str(machineid))
        self.machineid = machineid

    def post(self, url, params):
        print("Requester post to " + url)
        try:
            return requests.post(url, params)
        except Exception as e:
            print("caught error " + str(e))
            return None

    def request(self, method, url, headers, data):
        print("Requester " + method + " to " + url)
        try:
            return requests.request(method, url, headers, data)
        except:
            print
            return None

    def resetMachine(self):
        if not self.machineid == 0:
            print("Requester factsystem resetMachine " + str(self.machineid))
            response = requests.request(
                "POST",
                API_URL,
                headers={
                    "key": API_KEY,
                },
                data={
                    "machineid": self.machineid,
                    "machinestatus": STATUS_RESET,
                },
            )

            if response is None:
                print("Requester factsystem resetMachine - failed")
            elif not (response.status_code == 200):
                print("Requester factsystem resetMachine - succeeded")

    def stopMachine(self):
        if not self.machineid == 0:
            print("Requester factsystem stopMachine " + str(self.machineid))
            response = requests.request(
                "POST",
                API_URL,
                headers={
                    "key": API_KEY,
                },
                data={
                    "machineid": self.machineid,
                    "machinestatus": STATUS_STOPPED,
                },
            )

            if response is None:
                print("Requester factsystem stopMachine - failed")
            elif not (response.status_code == 200):
                print("Requester factsystem stopMachine - succeeded")

    def startMachine(self):
        if not self.machineid == 0:
            print("Requester factsystem startMachine " + str(self.machineid))
            response = requests.request(
                "POST",
                API_URL,
                headers={
                    "key": API_KEY,
                },
                data={
                    "machineid": self.machineid,
                    "machinestatus": STATUS_STARTED,
                },
            )

            if response is None:
                print("Requester factsystem startMachine - failed")
            elif not (response.status_code == 200):
                print("Requester factsystem startMachine - succeeded")
