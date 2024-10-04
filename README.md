<h2 id="ixia-upgrade-utility">Ixia Upgrade Utility</h2>
<hr>
<p>This python based tool will help customer upgrade their Linux bases IxOS Chassis in an automated way and at scale.</p>
<p>Before running this tool customer needs to identify</p>
<ol>
<li><p>Controller Chassis - Chassis where the customer will upload the upgrade version .tgz</p>
</li>
<li><p>Target Chassis - Chassis that need to be upgraded to a version whose .tgz was uploaded to Controller Chassis</p>
</li>
</ol>
<p>Next,  add the entries in config.py files in this repo. There is a sample config already present in there.</p>
<p>Upload the .tgz version you wish to upgrade to, on your controller chassis using SFTP. </p>

Before running the script, `pip install -r requirments.txt`
<h1 id="sample-output">Sample Output</h1>
<pre><code class="language-python">
(base) ashwjosh@C0HD4NKHCX ixupgradeutility % /usr/local/bin/python3 /Users/ashwjosh/ixupgradeutility/controller.py
INFO:root:Controller Chassis is 10.36.236.121 with username : admin and password : Kimchi123Kimchi123!
INFO:root:===== Fetching exisiting upgrade packages present on Controller Chassis 10.36.236.121
ID - VERSION
1 - 9.20.2700.12
2 - 9.30.3001.12
Please enter ID of version you want to upgeade to: 
2
You have selected to update target chassis to ID: 2. Please enter [Y/y] to proceed or [N/n] to re-enter: y
INFO:root:===== Adding Target Chassis from config file on Controller Chassis 10.36.236.121
Polling for async operation ...
Completed async operation
INFO:root:===== Target Chassis added on Controller Chassis 10.36.236.121. Please check at https://10.36.236.121/chassislab/chassisui/settings/ixos-install
INFO:root:===== Consolidating chassis credentials and target chassis id&#39;s added in previous step
INFO:root:[{&#39;id&#39;: 22, &#39;ip&#39;: &#39;10.36.237.131&#39;, &#39;activeVersion&#39;: &#39;NA&#39;, &#39;username&#39;: &#39;admin&#39;, &#39;password&#39;: &#39;Ixiaixiaixia!23&#39;}]
INFO:root:===== Authenticating all target chassis added on Controller Chassis 10.36.236.121
Polling for async operation ...
Completed async operation
INFO:root:===== Authentication complete for target chassis. Please check at https://10.36.236.121/chassislab/chassisui/settings/ixos-install
INFO:root:===== Sleeping for 30 secs to ensure all target chassis complete authentication =====
INFO:root:===== Updating Target Chassis =====
INFO:root:Upgrade started on 10.36.237.131
Polling for async operation ...
Completed async operation
22
Polling for async operation ...

Completed async operation

-----------------------------------
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
------------------------------

