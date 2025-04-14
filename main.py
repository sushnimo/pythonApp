from flask import Flask, jsonify, Response, request
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests
#from pyngrok import ngrok

app = Flask(__name__)

@app.route('/get-keys', methods=['GET'])
def get_keys() -> Response:
    try:
        # Get PSSH and license URL from query params
        pssh_value = "AAAAMnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAABISEM/vBFx4B1mcvc2RLgoZ+7M="
        license_url = "https://tataplay.live.ott.irdeto.com/Widevine/getlicense?CrmId=tatasky&AccountId=tatasky&ContentId=400000077&ls_session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvbnRyb2xfc2lnbmluZ19rZXlfcHJvZHVjdGlvbl8xNzIyOTY3MDk3ODc1In0.eyJzdWIiOiIxMTcyNTEyNzcyIiwiaXNlIjp0cnVlLCJqdGkiOiJlNjcxNWYzNS0wOWZiLTQzNjAtYjRhZi1mNmU3MGM0Y2ZlODMiLCJhaWQiOiJ0YXRhc2t5IiwiZXhwIjoxNzQ0NjQ4MzU0LCJuYW1lIjoidXNoYSAuIiwiaWF0IjoxNzQ0NjMzNjU0LCJlbnQiOlt7ImVwaWQiOiJTdWJzY3JpcHRpb25fQnJvd3Nlcl9TdHJlYW1pbmciLCJiaWQiOiIxMDAwMDAwOTI3In1dLCJpc3MiOiJ0cG1hX3dlYiJ9.vSf1T2B_hOK_L-Dev5C5cVU_8-Yx4JI3xCS2aA7pHts"

        if not pssh_value or not license_url:
            return jsonify({
                "status": "error",
                "message": "Missing 'pssh' or 'licence' parameter"
            }), 400

        # Prepare PSSH
        pssh = PSSH(pssh_value)

        # Load device
        device = Device.load("device.wvd")

        # Load CDM
        cdm = Cdm.from_device(device)

        # Open CDM session
        session_id = cdm.open()

        # Get license challenge
        challenge = cdm.get_license_challenge(session_id, pssh)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        # Send license challenge
        response = requests.post(license_url, data=challenge, headers=headers)
        response.raise_for_status()

        # Parse license
        cdm.parse_license(session_id, response.content)

        # Collect keys
        keys = [
            {
                "type": key.type,
                "kid": key.kid.hex() if isinstance(key.kid, bytes) else key.kid,
                "key": key.key.hex() if isinstance(key.key, bytes) else key.key
            }
            for key in cdm.get_keys(session_id)
        ]

        # Close session
        cdm.close(session_id)

        return jsonify({"status": "success", "keys": keys})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = 5000
   # public_url = ngrok.connect(port).public_url
   # print(f" * Ngrok tunnel available at: {public_url}")
   # print(f" * Access the API at: {public_url}/get-keys?pssh=<your_pssh>&licence=<your_license_url>")

    app.run(host='0.0.0.0', port=port)
