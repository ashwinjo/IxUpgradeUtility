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
                 poll_interval=2, verbose=False, insecure_request_warning=False, operation=None):

        self.chassis_ip = chassis_address
        self.api_key = api_key
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.verbose = verbose


        # Depending upon where you are working with ixNetworkWeb aut URI will change
        if operation == "updatestandalonevm":
            self._authUri = '/ixnetworkweb/api/v1/auth/session'
        elif operation == "newinstallonchassis":
            self._authUri = '/platform/api/v2/auth/session'
        elif operation == "updateonchassis":
            self._authUri = '/platform/api/v2/auth/session'
        elif operation == "uninstallonchassis":
            self._authUri = '/platform/api/v2/auth/session'


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

    def get_headers(self, content_type= "application/json"):
        # headers should at least contain these two
        return {
            "Content-Type": content_type,
            'x-api-key': self.api_key
        }

    def authenticate(self, username="admin", password="admin"):
        """
        we need to obtain API key to be able to perform any REST
        calls on IxNetwork platfrom and IxNetwork API;s
        """
        
        payload = {"password": password, 
                   "rememberMe": False, 
                   "username": username} 
        
        """
        Note:

        If you are not using strong passoword then update payload as

        payload = {
            'username': username,
            'password': password,
            'rememberMe': False,
            'resetWeakPassword': False
        }
        """

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
                'accept': 'text/html'
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
                print(response.text)
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
    
    def upload_file_to_ixnetwork(self, ip=None, file_name=None):
        """Upload the IxNetworkweb .waf file (Docker/ VM/ ESxI )

        Args:
            ip (_type_, optional): _description_. Defaults to None.
            file_name (_type_, optional): _description_. Defaults to None.
        """

        url = f"https://{ip}/ixnetworkweb/api/v1/admin/applications/uploads/operations/upload"

        # Path to the file you want to upload
        file_path = file_name

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
                self.remote_installer_path = response.data['path']
            else:
                print('Failed to upload file. Status code:', response.status_code)
                print('Response:', response.text)

    def install_ixnetwork_versions(self, ip=None):
        """Install the uploaded IxNetworkWeb update .waf (Docker/ VM/ ESxI )

        Args:
            ip (_type_, optional): _description_. Defaults to None.
            file_name (_type_, optional): _description_. Defaults to None.
        """
        url = f"https://{ip}/ixnetworkweb/api/v1/admin/applications/operations/install"
        payload = {"updateRemotePath": self.remote_installer_path ,
                   "updateType": "PACKAGE_UPDATE"}

        self.http_request('POST', url, payload=payload)

    
    def upload_file_for_onchassis_install(self, ip="10.36.237.131", file_name=None):
        """Upload the IxNetworkweb .waf file (OnChassis Update )

        Args:
            ip (_type_, optional): _description_. Defaults to None.
            file_name (_type_, optional): _description_. Defaults to None.
        """
        url = f"https://{ip}/platform/api/v2/admin/applications/operations/upload"

        #file_name = "/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-10.00.2312.14.el7.x86_64.waf"
        # Path to the file you want to upload
        file_path = file_name


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
                self.remote_installer_path = response.data['path']
            else:
                print('Failed to upload file. Status code:', response.status_code)
                print('Response:', response.text)

    def install_ixnetwork_versions_on_chassis(self, ip=None):
        """Install the IxNetworkweb .waf file (OnChassis Update )

        Args:
            ip (_type_, optional): _description_. Defaults to None.
            file_name (_type_, optional): _description_. Defaults to None.
        """
        path = self.remote_installer_path
        payload = {
                    "updateRemotePath": path,
                    "updateType": "PACKAGE_INSTALL",
                    "persistent": True,
                    "privacyNoticeAccepted": True
                    }
        url = f"https://{ip}/platform/api/v2/admin/applications/operations/install"
        self.http_request('POST', url, payload=payload)

    def uninstall_ixnetwork_onchassis(self, ip=None, app_id=None):
        """Uninstall IxNetwork Web OnChassis Deployment

        Args:
            ip (_type_, optional): _description_. Defaults to None.
            app_id (_type_, optional): _description_. Defaults to None.
        """
        app_url = f"https://{ip}/platform/api/v2/platform/apps?links=false"
        response = self.http_request('GET', app_url)
        for app in response.json():
            if app['name'].lower() == "ixnetworkweb":
                app_id = app['id']

        url = f"https://{ip}/platform/api/v2/platform/apps/{app_id}/operations/uninstall"
        response = self.http_request('POST', url)


@click.command()
@click.option('--ixnetworkwebip', help="ixNetworkWebIP")
@click.option('--username', help="ixNetworkWebIP UN")
@click.option('--password', default='admin', help="ixNetworkWebIP PW")
@click.option('--filepath', default='admin', help="filepath")
@click.option('--operation', default='update', help="operation")
def parse_args(ixnetworkwebip, username, password, filepath, operation):
    
    session = IxNRestSessions(chassis_address=ixnetworkwebip, username=username, password=password, operation=operation)
    
    if operation  == "newinstallonchassis":
        session.upload_file_for_onchassis_install(ip=ixnetworkwebip, file_name=filepath)
        session.install_ixnetwork_versions_on_chassis(ip=ixnetworkwebip)
    elif operation == "updatestandalonevm":
        session.upload_file_to_ixnetwork(ip=ixnetworkwebip, file_name=filepath)
        session.install_ixnetwork_versions(ip=ixnetworkwebip)
    elif operation == "updateonchassis":
        session.upload_file_to_ixnetwork(ip=ixnetworkwebip, file_name=filepath)
        session.install_ixnetwork_versions(ip=ixnetworkwebip)
    elif operation == "uninstallonchassis":
        session.uninstall_ixnetwork_onchassis(ip=ixnetworkwebip)


if __name__ == '__main__':
    parse_args()


"""
Pre-requisites:

pip3 install 
requests
json
urllib3
click

==========
On Chassis
==========
Upload: Tested
Install: Tested
Uninstall: Tested
Update: Tested

=============
KVM/ESXI/Docker
=============
Upload: Tested
Install:  Tested

----------------------------------------------------
Case 1: Standalone IxNetworkWeb upload and install
-----------------------------------------------------

Go to : https://support.ixiacom.com/version/ixnetwork-1020 ( You can choose your specific version) and then download package that says
"Update existing deployment:" --> "KVM/ESXi/Docker deployment updater"


Save and note the path of package on local system. In my case it was /Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-10.00.2312.14.el7.x86_64.waf


Run the IxNetworkWeb Updater
==============================

python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.36.229.70" --username="admin" --password="XXXXXX" --filepath="/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-9.39.2310.23.el7.x86_64.waf"  --operation="updatestandalonevm"

Upload Ixia File:
==================
File uploaded successfully!
Response: {"success":true,"details":"Successfully uploaded application update.","path":"/var/tmp/ixia/waf/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-9.39.2310.23.el7.x86_64.waf"}

Chassis upgrading:
=================

{'id': 3, 'type': 'Package Installation', 'state': 'IN_PROGRESS', 'progress': 0, 'message': 'Operation in progress', 'url': 'https://10.36.229.70/ixnetworkweb/api/v1/admin/applications/operations/install/3', 'updateApplicationArgs': {'updateRemotePath': '/var/tmp/ixia/waf/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-vm-update-9.39.2310.23.el7.x86_64.waf', 'updateSlotsList': [], 'updateType': 'PACKAGE_UPDATE', 'persistent': False}}
Polling for async operation ...
.
.
.
.

< Chassis goes down and comes up >


----------------------------------------------------
Case 2: On Chassis Workflow
-----------------------------------------------------
***. Install new IxNetwork Version on Chassis

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.36.237.131" --username="admin" --password='XXXXXX!' --filepath="/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-10.00.2312.14.el7.x86_64.waf" --operation="newinstallonchassis"
python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.39.51.127" --username="admin" --password="Keysight@12345" --filepath="C:\ixia-app-ixnetworkweb-10.00.2312.40.el7.x86_64.waf"  --operation="newinstallonchassis" (Windows)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
File uploaded successfully!
Response: {"success":true,"details":"Successfully uploaded application update.","path":"/home/ixia_apps/web/platform/server/tmp/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-10.00.2312.14.el7.x86_64.waf"}

/home/ixia_apps/web/platform/server/tmp/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-10.00.2312.14.el7.x86_64.waf
{'id': 8, 'type': 'Package Installation', 'state': 'IN_PROGRESS', 'progress': 0, 'message': 'Operation in progress', 'url': 'https://10.36.237.131/platform/api/v2/admin/applications/operations/install/8', 'updateApplicationArgs': {'updateRemotePath': '/home/ixia_apps/web/platform/server/tmp/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-10.00.2312.14.el7.x86_64.waf', 'updateSlotsList': [], 'updateType': 'PACKAGE_INSTALL', 'persistent': True, 'privacyNoticeAccepted': True}}
Polling for async operation ...
Completed async operation


***. Update IxNetwork version on chassis
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.36.237.131" --username="admin" --password='Kimchi123Kimchi123!' --filepath="/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-update-10.00.2312.14.el7.x86_64.waf" --operation="updateonchassis"
python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.39.51.127" --username="admin" --password="XXXXXX!" --filepath="C:\ixia-app-ixnetworkweb-update-10.00.2312.40.el7.x86_64.waf"  --operation="updateonchassis" ( Windows)

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

File uploaded successfully!
Response: {"success":true,"details":"Successfully uploaded application update.","path":"/var/tmp/ixia/waf/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-update-10.00.2312.14.el7.x86_64.waf"}

{'id': 2, 'type': 'Package Installation', 'state': 'IN_PROGRESS', 'progress': 0, 'message': 'Operation in progress', 'url': 'https://10.36.237.131/ixnetworkweb/api/v1/admin/applications/operations/install/2', 'updateApplicationArgs': {'updateRemotePath': '/var/tmp/ixia/waf/updates/Users/ashwjosh/configScripts/ixia-app-ixnetworkweb-update-10.00.2312.14.el7.x86_64.waf', 'updateSlotsList': [], 'updateType': 'PACKAGE_UPDATE', 'persistent': False}}
Polling for async operation ...
Completed async operation


***. Uninstall IxNetwork version on chassis
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
python3 ixNetworkWebUpdater.py --ixnetworkwebip="10.36.237.131" --username="admin" --password='XXXXXX!' --operation="uninstallonchassis" ( same command for wWndows & Linux)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

{'id': 10, 'type': 'Remove Application', 'state': 'IN_PROGRESS', 'progress': 0, 'message': 'Operation in progress', 'url': 'https://10.36.237.131/platform/api/v2/platform/apps/5/operations/uninstall/10'}
Polling for async operation ...
Completed async operation

"""
