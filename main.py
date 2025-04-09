from flask import Flask, request, jsonify
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests

app = Flask(__name__)

# Load device once
device = Device.load("device.wvd")

@app.route('/get_keys', methods=['POST'])
def get_keys():
    data = request.json
    pssh_str = data.get("pssh")

    if not pssh_str:
        return jsonify({"error": "Missing PSSH string"}), 400

    try:
        pssh = PSSH(pssh_str)
        cdm = Cdm.from_device(device)
        session_id = cdm.open()

        # Generate license challenge
        challenge = cdm.get_license_challenge(session_id, pssh)

        # Request license
        license_url = "https://tataplay.live.ott.irdeto.com/Widevine/getlicense?CrmId=tatasky&AccountId=tatasky&ContentId=400000077&ls_session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvbnRyb2xfc2lnbmluZ19rZXlfcHJvZHVjdGlvbl8xNzIyOTY3MDk3ODc1In0.eyJzdWIiOiIxMTcyNTEyNzcyIiwiaXNlIjp0cnVlLCJqdGkiOiI2MzNkMmU2ZC0yOGI0LTQwYTctOGU0Ny0zNGVjMmJkNjczYzEiLCJhaWQiOiJ0YXRhc2t5IiwiZXhwIjoxNzQ0MTEyMjg4LCJuYW1lIjoidXNoYSAuIiwiaWF0IjoxNzQ0MDk3NTg4LCJlbnQiOlt7ImVwaWQiOiJTdWJzY3JpcHRpb25fQnJvd3Nlcl9TdHJlYW1pbmciLCJiaWQiOiIxMDAwMDAwOTI3In1dLCJpc3MiOiJ0cG1hX3dlYiJ9.RRPpn-pVTO9rjJpWzcfca_QUXM-vIWS9rrlBqkYjXPE"
        license_response = requests.post(license_url, data=challenge)
        license_response.raise_for_status()

        # Parse license
        cdm.parse_license(session_id, license_response.content)

        keys = [
            {
                "type": key.type,
                "kid": key.kid.hex(),
                "key": key.key.hex()
            }
            for key in cdm.get_keys(session_id)
        ]

        cdm.close(session_id)
        return jsonify({"keys": keys})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
