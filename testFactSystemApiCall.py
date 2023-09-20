import requests
from flask import Flask, jsonify
import inspect
import pprint


# only works now from hte local machine
# i think the problem lies from the service on the app itself not accepting requests from different origins
# i did not debug it since i dont need it

# response = requests.request(
#     "POST",
#     "http://192.168.1.121/api/MachineStatusService.asmx/updateMachine_Status",
#     headers={},
#     data={
#         "machineid": 2,
#         "status": 0,
#     },
# )
# print(response, response.status_code)

# response = requests.request(
#     "POST",
#     "http://192.168.1.121/api/MachineStatusService.asmx/getMachines",
#     headers={},
#     data={},
# )
# # print(response, response.status_code, response.reason)
# # print(response.__dir__())
# print(inspect.getmembers(response))

# Now test the RAW request --------------------------------------

response = requests.request(
    "POST",
    "http://localhost/api/MachineStatusService.asmx/updateMachine_Status",
    headers={},
    data={
        "machineid": 2,
        "machinestatus": 0,
    },
)
print(response)
print()
print(response.status_code)
print()
print(response.content)


# Now test the Requester --------------------------------------

from Helpers.Th_SendRequests import Requester

factSystemRequester = Requester(1)
factSystemRequester.resetMachine()

input("Press Enter to continue...")
