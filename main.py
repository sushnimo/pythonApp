from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH

import requests

# prepare pssh
pssh = PSSH("AAAAMnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAABISEPaoezBThlbPj8zXz9qpcyg=")

# load device
device = Device.load("device.wvd")

# load cdm
cdm = Cdm.from_device(device)

# open cdm session
session_id = cdm.open()

# get license challenge
challenge = cdm.get_license_challenge(session_id, pssh)

# send license challenge (assuming a generic license server SDK with no API front)
licence = requests.post("https://tataplay.live.ott.irdeto.com/Widevine/getlicense?CrmId=tatasky&AccountId=tatasky&ContentId=400000077&ls_session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvbnRyb2xfc2lnbmluZ19rZXlfcHJvZHVjdGlvbl8xNzIyOTY3MDk3ODc1In0.eyJzdWIiOiIxMTcyNTEyNzcyIiwiaXNlIjp0cnVlLCJqdGkiOiJhYjMyNTFjNi1mMjMwLTQ3ZGEtOWNkNC04MzJkNjJkMjJkNWQiLCJhaWQiOiJ0YXRhc2t5IiwiZXhwIjoxNzQ0MTU2MDI4LCJuYW1lIjoidXNoYSAuIiwiaWF0IjoxNzQ0MTQxMzI4LCJlbnQiOlt7ImVwaWQiOiJTdWJzY3JpcHRpb25fQnJvd3Nlcl9TdHJlYW1pbmciLCJiaWQiOiIxMDAwMDAwOTI3In1dLCJpc3MiOiJ0cG1hX3dlYiJ9.JhVim8CpYop_YDczlw3o8CW1jpmcbj2Mg_4PXklotyQ", data=challenge)
licence.raise_for_status()

# parse license challenge
cdm.parse_license(session_id, licence.content)

# print keys
for key in cdm.get_keys(session_id):
    print(f"[{key.type}] {key.kid.hex}:{key.key.hex()}")

# close session, disposes of session data
cdm.close(session_id)
