from flask import Flask, jsonify, Response
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests
#from pyngrok import ngrok  # Added for ngrok integration

app = Flask(__name__)

@app.route('/get-keys', methods=['GET'])
def get_keys() -> Response:
    try:
        # prepare pssh
        pssh = PSSH("AAAAMnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAABISEAqrGqFxzV2upZ2Ef8Zndfo=")

        # load device
        device = Device.load("device.wvd")

        # load cdm
        cdm = Cdm.from_device(device)

        # open cdm session
        session_id = cdm.open()

        # get license challenge
        challenge = cdm.get_license_challenge(session_id, pssh)

        proxies = {
            "http": "http://rukgppbz:7m1ljtkt5j20@
38.153.152.244:9594",
            "https": "http://rukgppbz:7m1ljtkt5j20@
38.153.152.244:9594"
        }

        # send license challenge
        licence = requests.post(
            "https://tataplay.live.ott.irdeto.com/Widevine/getlicense?CrmId=tatasky&AccountId=tatasky&ContentId=400000077&ls_session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvbnRyb2xfc2lnbmluZ19rZXlfcHJvZHVjdGlvbl8xNzIyOTY3MDk3ODc1In0.eyJzdWIiOiIxMTcyNTEyNzcyIiwiaXNlIjp0cnVlLCJqdGkiOiIwMGJlMTMxMS03MjI1LTRjNTgtOGZmZS02OGJkNDkwNDY1MTMiLCJhaWQiOiJ0YXRhc2t5IiwiZXhwIjoxNzQ0MzA4MjIxLCJuYW1lIjoidXNoYSAuIiwiaWF0IjoxNzQ0MjkzNTIxLCJlbnQiOlt7ImVwaWQiOiJTdWJzY3JpcHRpb25fQnJvd3Nlcl9TdHJlYW1pbmciLCJiaWQiOiIxMDAwMDAwOTI3In1dLCJpc3MiOiJ0cG1hX3dlYiJ9.vjGaC1J-mA_7FonSUdxppyETyZpeNmjctZ6aqVolZuI",
            data=challenge,
            proxies=proxies,
            timeout=10
        )
        licence.raise_for_status()

        # parse license
        cdm.parse_license(session_id, licence.content)

        # collect keys
        keys = [
        {
            "type": key.type,
            "kid": key.kid.hex() if isinstance(key.kid, bytes) else key.kid,
            "key": key.key.hex() if isinstance(key.key, bytes) else key.key
        }
        for key in cdm.get_keys(session_id)
    ]


        # close session
        cdm.close(session_id)

        return jsonify({"status": "success", "keys": keys})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Set up ngrok
    # port = 8000
    # public_url = ngrok.connect(port).public_url
    # print(f" * Ngrok tunnel available at: {public_url}")
    # print(f" * Access the API at: {public_url}/get-keys")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)

