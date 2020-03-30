import requests
import json

from flask import Flask
from flasgger import Swagger
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app)
Swagger(app)

from controllers.ovpn import ovpn

ovpn = ovpn.Ovpn()

# ROUTE
app.route('/ovpn', methods=['POST'])(ovpn.ovpn)

from controllers.ovpn import vessel_vpn

vessel_vpn = vessel_vpn.VesselVPN()

# ROUTE
app.route('/vessel/vpn', methods=['POST'])(vessel_vpn.vessel_vpn)

from controllers.remote_command import remote_command

remote_command = remote_command.RemoteCommand()

# ROUTE
app.route('/remote/command', methods=['POST'])(remote_command.remote_command)

from controllers.ovpn import delete_vessel_vpn

delete_vessel_vpn = delete_vessel_vpn.DeleteVesselVPN()

# ROUTE
app.route('/delete/vessel/vpn', methods=['DELETE'])(delete_vessel_vpn.delete_vessel_vpn)


from controllers.update_inifiles import update_inifiles

update_inifiles = update_inifiles.UpdateINIFiles()

# ROUTE
app.route('/update/ini/files', methods=['PUT'])(update_inifiles.update_inifiles)


if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port = 5000)
