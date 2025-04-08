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
licence = requests.post("http://jtv.jonatv.website/tsky/widevine.php?id=78", data=challenge)
licence.raise_for_status()

# parse license challenge
cdm.parse_license(session_id, licence.content)

# print keys
for key in cdm.get_keys(session_id):
    print(f"[{key.type}] {key.kid.hex}:{key.key.hex()}")

# close session, disposes of session data
cdm.close(session_id)
