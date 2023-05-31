import logging
import time

from RestApi.IxOSRestInterface import IxRestSession
from config import TARGET_CHASSIS_DICT, CONTROLLER_CHASSIS_DICT

def get_controller_chassis_packages(ip=None, username=None, password=None):
    """This method will return list of available updates"""
    new_packages_dict = []
    session = IxRestSession(ip, username, password, verbose=False)
    out = session.get_packages()
    for updates in out:
        updates.pop('links')
        new_packages_dict.append(updates)
    return new_packages_dict
    

def add_target_ixia_chassis_to_controller_chassis(ip=None, username=None, password=None, target_chassis_list=None):
    session = IxRestSession(ip, username, password, verbose=False)
    result_url = session.add_target_chassis_to_controller_chassis(target_chassis_list)
    return result_url
     
     
def authenticate_target_chassis(ip=None, username=None, password=None, list_target_chassis_only_dict=None):
    session = IxRestSession(ip, username, password, verbose=False)
    return session.authenticate_target_chassis(list_target_chassis_only_dict)
    
    
def get_target_chassis_information(ip=None, username=None, password=None, target_chassis_list=None):
    session = IxRestSession(ip, username, password, verbose=False)
    target_chassis_only_dict = {}
    list_target_chassis_only_dict = []
    existing_target_chassis =  session.get_target_chassis_information()
    for item in existing_target_chassis['data']:
        if not item['local']:
            target_chassis_only_dict['id'] = item['id']
            target_chassis_only_dict['ip'] = item['address']
            target_chassis_only_dict['activeVersion'] = item['status'].get('activeVersion', 'NA')
            target_chassis_only_dict['username'] = target_chassis_list[item['address']]['username']
            target_chassis_only_dict['password'] = target_chassis_list[item['address']]['password']
            list_target_chassis_only_dict.append(target_chassis_only_dict)
    return list_target_chassis_only_dict


def upgrade_target_chassis(ip=None, username=None, password=None,uploadId=None, list_target_chassis_only_dict=None):
    session = IxRestSession(ip, username, password, verbose=False)
    return session.upgrade_target_chassis(uploadId=uploadId, list_target_chassis_only_dict=list_target_chassis_only_dict)
<<<<<<< controller.py

=======
>>>>>>> controller.py


def upgrade_commander():
    ip = CONTROLLER_CHASSIS_DICT["ip"]
    username = CONTROLLER_CHASSIS_DICT["username"]
    password = CONTROLLER_CHASSIS_DICT["password"]
    
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Controller Chassis is {ip} with username : {username} and password : {password}")

    logging.info(f"===== Fetching exisiting upgrade packages present on Controller Chassis {ip}")
    # Please select what version you want to upgrade to.
    packages = get_controller_chassis_packages(ip=ip, username=username, password=password)
    print(f"ID - VERSION")
    for p in packages:
        print(f"{p['id']} - {p['version']}")
    uploadId = input('Please enter ID of version you want to upgeade to: \n')
    confirmation = input(f"You have selected to update target chassis to ID: {uploadId}. Please enter [Y/y] to proceed or [N/n] to re-enter: ")
    if confirmation.lower() == "y":
        logging.info(f"===== Adding Target Chassis from config file on Controller Chassis {ip}")
        add_target_ixia_chassis_to_controller_chassis(ip=ip, username=username, password=password, target_chassis_list=list(TARGET_CHASSIS_DICT.keys()))
        logging.info(f"===== Target Chassis added on Controller Chassis {ip}. Please check at https://{ip}/chassislab/chassisui/settings/ixos-install")
        
        logging.info(f"===== Consolidating chassis credentials and target chassis id's added in previous step")
        list_target_chassis_only_dict = get_target_chassis_information(ip=ip, username=username, password=password, target_chassis_list=TARGET_CHASSIS_DICT)
        logging.info(list_target_chassis_only_dict)
        
        logging.info(f"===== Authenticating all target chassis added on Controller Chassis {ip}")
        authenticate_target_chassis(ip=ip, username=username, password=password, list_target_chassis_only_dict=list_target_chassis_only_dict)
        logging.info(f"===== Authentication complete for target chassis. Please check at https://{ip}/chassislab/chassisui/settings/ixos-install")
        
        logging.info(f"===== Sleeping for 30 secs to ensure all target chassis complete authentication =====")
        time.sleep(30)
        
        logging.info(f"===== Updating Target Chassis =====")
        try:
            upgrade_target_chassis(ip=ip, username=username, password=password, uploadId=uploadId, list_target_chassis_only_dict=list_target_chassis_only_dict)
        except Exception as e:
           if "timeout" not in str(e):
               raise     
    elif confirmation.lower() == "n":
        upgrade_commander()
        
        
if __name__ == "__main__":
    upgrade_commander()


"""Output:

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
"""

