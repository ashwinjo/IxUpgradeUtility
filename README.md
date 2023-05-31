
## Ixia Upgrade Utility


# Sample Output

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
INFO:root:===== Consolidating chassis credentials and target chassis id's added in previous step
INFO:root:[{'id': 22, 'ip': '10.36.237.131', 'activeVersion': 'NA', 'username': 'admin', 'password': 'Ixiaixiaixia!23'}]
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