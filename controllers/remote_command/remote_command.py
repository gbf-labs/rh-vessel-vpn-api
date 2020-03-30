# -*- coding: utf-8 -*-
import string, time, subprocess
from flask import  request
from datetime import datetime
from library.common import Common

from configparser import ConfigParser
from library.config_parser import configSectionParser
import paramiko

class RemoteCommand(Common):

    # INITIALIZE 
    def __init__(self):
        
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.token = configSectionParser(self.config,"TOKEN")['token']

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys()

    # GET VESSEL FUNCTION
    def remote_command(self):
        """
        This API is for VPN
        ---
        tags:
          - Remote Command
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: query
            in: body
            description: Remote Command
            required: true
            schema:
              id: remote_command
              properties:
                host:
                    type: string
                port:
                    type: string
                user:
                    type: string
                password:
                    type: string
                key:
                    type: string
                label:
                    type: string
                remote_addr:
                    type: string
                others:
                    type: json
                    example: {}

        responses:
          500:
            description: Error
          200:
            description: Sending command
        """

        # INIT DATA
        data = {}

        # GET DATA
        token =  request.headers.get('token')

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        host = query_json["host"]
        port = query_json["port"]
        user = query_json["user"]
        password = query_json["password"]
        key = query_json["key"]
        label = query_json["label"]
        remote_addr = query_json["remote_addr"]

        others = False
        if 'others' in query_json.keys():
            others = query_json['others']

        # # CHECK TOKEN
        if not token == self.token:

            data["alert"] = "Invalid Token"
            data['status'] ='Failed'

            # RETURN ALERT
            return self.return_data(data)

        try:

            self.ssh_client.connect(host, int(port), user, password)

            command_info, command = self.get_command(label, key, remote_addr, others)
            output = ""

            if key in ['Failover rule', 'Reset all gateways', 'Reboot Outlet', 'Reboot',
                'Beam Lock', 'Beam Switch', 'New Map', 'Remove Map']:
                final_command = "cd /home/rh/backendv1;" + command
                _, stdout, _ = self.ssh_client.exec_command(final_command, get_pty=True)

                for line in iter(stdout.readline, ""):
                    output += line

            else:
                _, stdout, _ = self.ssh_client.exec_command(command, get_pty=False)
                new_stdout = stdout.read().decode("utf-8")

                for line in new_stdout.split("\n"):
                    output += line + "\n"

            data['output'] = output
            data['command_info'] = command_info
            data['connection_info'] = 'Login OK (' + str(user) + '@' + str(host) + ')'
            data['status'] ='ok'
        except:
            print('error')
            data['status'] ='failed'

        return self.return_data(data)

    def get_command(self, label, key, remote_addr, others=False):

        if key == 'Load-average':

            command = """printf \'\033[4mNumber of cores:\033[0m\n\'
                grep \'model name\' /proc/cpuinfo | wc -l
                printf \'\n\033[4mList of cores:\033[0m\n\'
                grep \'model name\' /proc/cpuinfo
                printf \'\n\033[4mLoad-average:\033[0m (1min, 5min, 15min - \033[3m1.0 = 1 Core@Full load\033[0m)\n\'
                uptime | awk -F\'[a-z]:\' \'{print $2}\'"""

            command_info = "printf \'\033[4mNumber of cores:\033[0m\'\n"
            command_info += "grep \'model name\' /proc/cpuinfo | wc -l\n"
            command_info += "printf \'\033[4mList of cores:\033[0m\'\n"
            command_info += "grep \'model name\' /proc/cpuinfo\n"
            command_info += "printf \'\033[4mLoad-average:\033[0m (1min, 5min, 15min - \033[3m1.0 = 1 Core@Full load\033[0m)\'\n"
            command_info += "uptime | awk -F\'[a-z]:\' \'{print $2}\'\n"

            return [command_info, command]

        elif key == 'Uptime':
            command = """printf \'\033[4mUptime:\033[0m\'
                     uptime -p
                     printf \'\n\033[4mUp since:\033[0m\'
                     uptime -s"""

            command_info = "printf \'\033[4mUptime:\033[0m\'\n"
            command_info += "uptime -p\n"
            command_info += "printf \'\033[4mUp since:\033[0m\'\n"
            command_info += "uptime -s\n"

            return [command_info, command]

        elif key == 'Free RAM and Swap':
            command = 'free -h'

            return [command, command]

        elif key == 'Hardware info':
            command = 'sudo dmidecode -t system'

            return [command, command]
        
        elif key == 'Memory info':
            command = 'sudo dmidecode -t memory'

            return [command, command]
        
        elif key == 'Disk space':
            command = """df -T -h /
                    lsblk
                """
            
            command_info = "df -T -h /\n"
            command_info += "lsblk"

            return [command_info, command]

        elif key == 'Debian version':
            command = 'uname -v && uname -r'

            return [command, command]

        elif key == 'PWD':
            
            command = 'pwd'
            return [command, command]

        elif key == 'Initiate program cycle':
            command = """touch /home/rh/backendv1/ini/run && echo \"Program cycle initiated\" || (echo \"Initiating failed\" && exit)
                    sleep 2
                    test ! -e /home/rh/backendv1/ini/run && printf \'\n\033[92mNew program cycle started\033[0m\' || printf \'\n\033[95mNew cycle not started yet, probably still running previous cycle.\033[0m\'"""

            command_info = "touch /home/rh/backendv1/ini/run && echo \"Program cycle initiated\" || (echo \"Initiating failed\" && exit)"
            command_info += "sleep 2"
            command_info += "test ! -e /home/rh/backendv1/ini/run && printf \'\n\033[92mNew program cycle started\033[0m\' || printf \'\n\033[95mNew cycle not started yet, probably still running previous cycle.\033[0m\'"

            return [command_info, command]

        elif key == 'Date/Time':

            command = 'date'

            return [command, command]

        elif key == 'Temporary file server':

            directory = "/home/rh/backendv1/log"
            fileserver = 6
            if others:
                print("others: ", others)
                fileserver = others["File-server shuts down after..."]
                directory = others["Directory"]

            command = """cd """ + directory + """
                nohup timeout """ + str(fileserver) + """ python -m SimpleHTTPServer 8000 </dev/null >/dev/null 2>&1 & 
                disown
                #SKIP
                echo Running temporary fileserver on port 8000 for """ + str(fileserver) + """ seconds."""

            command_info = "cd " + directory + "\n"
            command_info += "nohup timeout " + str(fileserver) + " python -m SimpleHTTPServer 8000 </dev/null >/dev/null 2>&1 &\n"
            command_info += "disown\n"
            command_info += "#SKIP"
            command_info += "echo Running temporary fileserver on port 8000 for " + str(fileserver) + " seconds."


            return [command_info, command]

        elif key == 'Reset all gateways':
            command = "sudo python /home/rh/backendv1/Main.py -cmd setgateway -dev all -opt reset -wwwuserip {0}".format(remote_addr)

            return [command, command]

        elif key == 'Failover rule':

            rule = others["Rule"]
            failover = others["Failover"]
            command = "sudo python /home/rh/backendv1/Main.py -cmd setgateway -dev {0} -opt {1} -wwwuserip {2}".format(rule, failover, remote_addr)
            
            return [command, command]

        elif key == 'Ping':
            host = others["Destination IP"]
            count = others["Number of pings"]
            interface = others["Interface"]

            command = "ping " + str(host) + " -c " + str(count) + " " + str(interface)

            return [command, command]


        elif key == 'Ping':
            host = others["Destination IP"]
            count = others["Number of pings"]
            interface = others["Interface"]

            command = "ping " + str(host) + " -c " + str(count) + " " + str(interface)

            return [command, command]

        elif key == 'Network statistics':
            command = others["Method"]

            return [command, command]

        elif key == 'Interfaces':
            command = others["Method"]

            return [command, command]

        elif key == 'Routes':
            command = others["Method"]

            return [command, command]

        elif key == 'Connections':
            command = others["Method"]

            return [command, command]

        elif key == 'Scan host':
            host_to_scan = others["Host to scan"]
            option = others["Please select an option:"]

            command = "nmap " + str(option) + " " + str(host_to_scan)
            return [command, command]

        elif key == 'Reboot Outlet':

            opt = others['Outlet number']
            command = "sudo python /home/rh/backendv1/Main.py -cmd rebootoutlet -dev {0} -opt {1} -wwwuserip {2}".format(label, opt, remote_addr)

            return [command, command]

        elif key == 'Reboot':

            command = "sudo python /home/rh/backendv1/Main.py -cmd reboot -dev {0} -wwwuserip {1}".format(label, remote_addr)

            return [command, command]

        elif key == 'Beam Lock':

            command = "sudo python /home/rh/backendv1/Main.py -cmd beamlock -dev {0} -wwwuserip {1}".format(label, remote_addr)

            return [command, command]

        elif key == 'Beam Switch':

            opt = others['Please select the beam:']
            command = "sudo python /home/rh/backendv1/Main.py -cmd beamSwitch -dev {0} -opt {1} -wwwuserip {2}".format(label, opt, remote_addr)

            return [command, command]

        elif key == 'New Map':

            command = "sudo python /home/rh/backendv1/Main.py -cmd newmap -dev {0} -wwwuserip {1}".format(label, remote_addr)

            return [command, command]

        elif key == 'Remove Map':

            command = "sudo python /home/rh/backendv1/Main.py -cmd removemap -dev {0} -wwwuserip {1}".format(label, remote_addr)

            return [command, command]