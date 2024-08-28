import requests
import json
import sys
import urllib3
import os
import time
import click


class IxNRestSessions(object):
    """
    class for handling HTTP requests/response for IxOS REST APIs
    Constructor arguments:
    chassis_address:    addrress of the chassis
    Optional arguments:
        api_key:        API key or you can use authenticate method \
                        later to get it by providing user/pass.
        verbose:        If True, will print every HTTP request or \
                        response header and body.
        timeout:        Time to wait (in seconds) while polling \
                        for async operation.
        poll_interval:  Polling inteval in seconds.
    """

    def __init__(self, chassis_address, username=None, password=None, api_key=None,timeout=600, 
                 poll_interval=2, verbose=False, insecure_request_warning=False):

        self.chassis_ip = chassis_address
        self.api_key = api_key
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.verbose = verbose
        self._authUri = '/ixnetworkweb/api/v1/auth/session'
        self.username = username
        self.password = password

        # ignore self sign certificate warning(s) if insecure_request_warning=False
        if not insecure_request_warning:
            try:
                if sys.version_info[0] == 2 and ((sys.version_info[1] == 7 and sys.version_info[2] < 9) or sys.version_info[1] < 7):
                    requests.packages.urllib3.disable_warnings()
                else:
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except AttributeError:
                print('WARING:You are using an old urllib3 version which does not support handling the certificate validation warnings. Please upgrade urllib3 using: pip install urllib3 --upgrade')

    # try to authenticate with default user/password if no api_key was provided
        if not api_key:
            self.authenticate(username=self.username, password=self.password)

    def get_ixos_uri(self):
        return 'https://%s/chassis/api/v2/ixos' % self.chassis_ip

    def get_headers(self, content_type= "application/json"):
        # headers should at least contain these two
        return {
            "Content-Type": content_type,
            'x-api-key': self.api_key,
        }

    def authenticate(self, username="admin", password="admin"):
        """
        we need to obtain API key to be able to perform any REST
        calls on IxOS
        """
        payload = {
            'username': username,
            'password': password,
            'rememberMe': False,
            'resetWeakPassword': False
        }
        response = self.http_request(
            'POST',
            'https://{address}{uri}'.format(address=self.chassis_ip,
                                            uri=self._authUri),
            payload=payload
        )
        self.api_key = response.data['apiKey']

    def http_request(self, method, uri, payload=None, params=None, files=None):
        """
        wrapper over requests.requests to pretty-print debug info
        and invoke async operation polling depending on HTTP status code (e.g. 202)
        """
        try:
            # lines with 'debug_string' can be removed without affecting the code
            if not uri.startswith('http'):
                uri = self.get_ixos_uri() + uri

            if payload is not None:
                payload = json.dumps(payload, indent=2, sort_keys=True)

            if "upload" in uri:
               headers = {
            'x-api-key': self.api_key,
        }
            else:
                headers = self.get_headers()
            response = requests.request(
                method, uri, data=payload, params=params, files=files,
                headers=headers, verify=False, timeout=600
            )

            # debug_string = 'Response => Status %d\n' % response.status_code
            data = None
            try:
                data = response.content.decode()
                data = json.loads(data) if data else None
            except:
                print('Invalid/Non-JSON payload received: %s' % data)
                data = None

            if str(response.status_code)[0] == '4':
                raise Exception("{code} {reason}: {data}.{extraInfo}".format(
                    code=response.status_code,
                    reason=response.reason,
                    data=data,
                    extraInfo="{sep}{msg}".format(
                        sep=os.linesep,
                        msg="Please check that your API key is correct or call IxRestSession.authenticate(username, password) in order to obtain a new API key."
                    ) if str(response.status_code) == '401' and uri[-len(self._authUri):] != self._authUri else ''
                )
                )

            if response.status_code == 202:
                result_url = self.wait_for_async_operation(data)
                return result_url
            else:
                response.data = data
                return response
        except:
            raise

    def wait_for_async_operation(self, response_body):
        """
        method for handeling intermediate async operation results
        """
        try:
            print(response_body)
            print('Polling for async operation ...')
            operation_status = response_body['state']
            start_time = int(time.time())
            while operation_status == 'IN_PROGRESS':
                response = self.http_request('GET', response_body['url'])
                response_body = response.data
                operation_status = response_body['state']
                if int(time.time() - start_time) > self.timeout:
                    raise Exception(
                        'timeout occured while polling for async operation')
                time.sleep(self.poll_interval)

            if operation_status == 'SUCCESS':
                return response.data.get('resultUrl', 'NA')
            elif operation_status == 'COMPLETED':
                return response.data['resultUrl']
            elif operation_status == 'ERROR':
                return response.data['message']
            else:
                raise Exception("async failed")
        except:
            raise
        finally:
            print('Completed async operation')
    
    def upload_file_to_ixnetwork(self, file_name=None):
        url = "https://10.36.229.70/ixnetworkweb/api/v1/admin/applications/uploads/operations/upload"


        # Path to the file you want to upload
        file_path = file_name

        # Headers for the request, excluding Content-Type
        headers = {
            'accept': 'text/html'
        }

        # Open the file in binary mode and prepare it for upload
        with open(file_path, 'rb') as file:
            # Create the multipart/form-data request with the specified file
            files = {
                'file': (file_path, file)  # Let requests set the content type and boundary
            }
            
            # Make the POST request
            response = self.http_request('POST', url, files=files)

            # Check the response
            if response.status_code == 200:
                print('File uploaded successfully!')
                print('Response:', response.text)
            else:
                print('Failed to upload file. Status code:', response.status_code)
                print('Response:', response.text)

    def install_ixnetwork_versions(self, file_name=None):
        url = "https://10.36.229.70/ixnetworkweb/api/v1/admin/applications/operations/install"
        payload = {"updateRemotePath": f"/var/tmp/ixia/waf/updates/{file_name}",
                   "updateType": "PACKAGE_UPDATE"}

        response = self.http_request('POST', url, payload=payload)
        # Check the response
        if response.status_code == 200:
            print('File uploaded successfully!')
            print('Response:', response.text)
        else:
            print('Failed to upload file. Status code:', response.status_code)
            print('Response:', response.text)


@click.command()
@click.option('--ixnetworkwebip', help="ixNetworkWebIP")
@click.option('--username', help="ixNetworkWebIP UN")
@click.option('--password', default='admin', help="ixNetworkWebIP PW")
@click.option('--filepath', default='admin', help="filepath")
def parse_args(ixnetworkwebip, username, password, filepath):
    
    session = IxNRestSessions(chassis_address=ixnetworkwebip, username=username, password=password)
    file_name = filepath.split('/')[-1]
    print(session.upload_file_to_ixnetwork(file_name=filepath))
    print(session.install_ixnetwork_versions(file_name=file_name))

if __name__ == '__main__':
    parse_args()




"""

Pre-requisites:

pip3 install 
requests
json
urllib3
click


Go to : https://support.ixiacom.com/version/ixnetwork-1020 ( You can choose your specific version) and then download package that says
"Update existing deployment:" --> "KVM/ESXi/Docker deployment updater"


Save and note the path of package on local system. In my case it was /Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-10.00.2312.14.el7.x86_64.waf


Run the IxNetworkWeb Updater
==============================

python3 ixnetwork_upgrade.py --ixnetworkwebip="10.36.229.70" --username="admin" --password="admin" --filepath="/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-10.00.2312.14.el7.x86_64.waf"

Upload Ixia File:
==================
File uploaded successfully!
Response: {"success":true,"details":"Successfully uploaded application update.","path":"/var/tmp/ixia/waf/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-10.00.2312.14.el7.x86_64.waf"}

Chassis upgrading:
=================

{'id': 4, 'type': 'Package Installation', 'state': 'IN_PROGRESS', 'progress': 0, 'message': 'Operation in progress', 
'url': 'https://10.36.229.70/ixnetworkweb/api/v1/admin/applications/operations/install/4', 
'updateApplicationArgs': {'updateRemotePath': '/var/tmp/ixia/waf/updates//Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-10.00.2312.14.el7.x86_64.waf', 
'updateSlotsList': [], 'updateType': 'PACKAGE_UPDATE', 'persistent': False}}

.
.
.
.
.
.



<< This is an sync operation. It will run for 10 minutes, till it succeeds. Keep pinging chassis UI to check if chassis upgraded" >>

"""
