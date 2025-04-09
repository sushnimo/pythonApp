from flask import Flask, request, Response
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import base64

app = Flask(__name__)

@app.route('/getkeys', methods=['GET'])
def get_keys():
    pssh_b64 = request.args.get('pssh')
    license_b64 = request.args.get('license')

    if not pssh_b64 or not license_b64:
        return "Missing pssh or license", 400

    try:
        # Decode base64 values
        pssh_decoded = base64.b64decode(pssh_b64)
        license_decoded = base64.b64decode(license_b64)

        # Prepare PSSH object
        pssh = PSSH(pssh_decoded)

        # Load device & CDM
        device = Device.load("device.wvd")
        cdm = Cdm.from_device(device)
        session_id = cdm.open()

        # Parse license
        cdm.parse_license(session_id, license_decoded)

        # Extract keys
        keys_output = ""
        for key in cdm.get_keys(session_id):
            keys_output += f"[{key.type}] {key.kid.hex()}:{key.key.hex()}\n"

        cdm.close(session_id)
        return Response(keys_output, mimetype='text/plain')

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
