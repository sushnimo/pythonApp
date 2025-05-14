from flask import Flask, jsonify, Response, request
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests

app = Flask(__name__)

@app.route('/get-keys', methods=['GET'])
def get_keys() -> Response:
    try:
        # Get PSSH and license URL from query params (or use hardcoded values)
        pssh_value = "AAAAMnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAABISEIFrlmdj6VtdvHCh5xeGRK0="
        license_url = "https://tataplay.live.ott.irdeto.com/Widevine/getlicense?CrmId=tatasky&AccountId=tatasky&ContentId=400000253&ls_session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNvbnRyb2xfc2lnbmluZ19rZXlfcHJvZHVjdGlvbl8xNzIyOTY3MDk3ODc1In0.eyJzdWIiOiIxMTA5NzQ3MjkzIiwiaXNlIjp0cnVlLCJqdGkiOiJmNGFkYmUzZS00ZTI2LTQ5MzUtYTI2ZC1kYmY3NDA0ZTY5NWEiLCJhaWQiOiJ0YXRhc2t5IiwiZXhwIjoxNzQ2MDU3NzQ5LCJuYW1lIjoiTXVrZXNoIEt1bWFyIiwiaWF0IjoxNzQ2MDQzMDQ5LCJlbnQiOlt7ImVwaWQiOiJTdWJzY3JpcHRpb25fQnJvd3Nlcl9TdHJlYW1pbmciLCJiaWQiOiIxMDAwMDAzMDU0In1dLCJpc3MiOiJ0cG1hX3dlYiJ9.m4OsY7cYJpdXrx9UeEfl1uNxdIehnLGsGz5MvKmOGYw"

        if not pssh_value or not license_url:
            return jsonify({
                "status": "error",
                "message": "Missing 'pssh' or 'licence' parameter"
            }), 400

        # Prepare PSSH
        pssh = PSSH(pssh_value)

        # Load Widevine device credentials (you must have device.wvd)
        device = Device.load("device.wvd")

        # Load CDM and open session
        cdm = Cdm.from_device(device)
        session_id = cdm.open()

        # Create license challenge
        challenge = cdm.get_license_challenge(session_id, pssh)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Content-Type": "application/octet-stream"
        }

        # Define proxy with authentication
        proxies = {
            "http": "http://Vv8IHp2g:kMhGaCi9XZ@103.172.84.179:50100",
            "https": "http://Vv8IHp2g:kMhGaCi9XZ@103.172.84.179:50100"
        }

        # Send license request using proxy
        response = requests.post(license_url, data=challenge, headers=headers, proxies=proxies)
        response.raise_for_status()

        # Parse license and extract keys
        cdm.parse_license(session_id, response.content)
        keys = [
            {
                "type": key.type,
                "kid": key.kid.hex() if isinstance(key.kid, bytes) else key.kid,
                "key": key.key.hex() if isinstance(key.key, bytes) else key.key
            }
            for key in cdm.get_keys(session_id)
        ]

        # Close CDM session
        cdm.close(session_id)

        return jsonify({"status": "success", "keys": keys})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = 5000
    app.run(host='0.0.0.0', port=port)
