from RestApi.IxOSRestInterface import IxRestSession
import ixUpgradeUtility
from config import TARGET_CHASSIS_DICT

def get_controller_chassis_packages(ip=None, username=None, password=None):
    """This method will return list of available updates"""
    new_updates = []
    session = IxRestSession(ip, username, password, verbose=False)
    out = ixUpgradeUtility.get_packages_on_controller_chassis(session)
    for updates in out:
        updates.pop('links')
        new_updates.append(updates)
    return new_updates
    

def add_target_ixia_chassis_to_controller_chassis(ip=None, username=None, password=None, target_chassis_list=None):
    session = IxRestSession(ip, username, password, verbose=False)
    result_url =  ixUpgradeUtility.add_target_chassis_to_controller_chassis(session, target_chassis_list)
    return result_url
     
     
def authenticate_target_chassis(ip=None, username=None, password=None, list_target_chassis_only_dict=None):
    session = IxRestSession(ip, username, password, verbose=False)
    ixUpgradeUtility.authenticate_target_chassis(session, list_target_chassis_only_dict)
    
    
def get_target_chassis_information(ip=None, username=None, password=None, target_chassis_list=None):
    session = IxRestSession(ip, username, password, verbose=False)
    target_chassis_only_dict = {}
    list_target_chassis_only_dict = []
    existing_target_chassis =  ixUpgradeUtility.get_target_chassis_information(session)
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
    ixUpgradeUtility.upgrade_target_chassis(session, uploadId=uploadId, list_target_chassis_only_dict=list_target_chassis_only_dict)

# Please select what version you want to upgrade to.
packages = get_controller_chassis_packages(ip="10.36.236.121", username="admin", password="somepassword")
print(packages)


# Add chassis as per configuration file
add_target_ixia_chassis_to_controller_chassis(ip="10.36.236.121", username="admin", password="somepassword", 
                                            target_chassis_list=list(TARGET_CHASSIS_DICT.keys()))


# Make consolidated, list of IDs, username, password
list_target_chassis_only_dict = get_target_chassis_information(ip="10.36.236.121", username="admin", password="somepassword", 
                                                               target_chassis_list=TARGET_CHASSIS_DICT)
print(list_target_chassis_only_dict)

print(list_target_chassis_only_dict)

# Authenticate all the added chassis
authenticate_target_chassis(ip="10.36.236.121", username="admin", password="somepassword", list_target_chassis_only_dict=list_target_chassis_only_dict)

import time; time.sleep(30)
# Upgrade all the added chassis
try:
    upgrade_target_chassis(ip="10.36.236.121", username="admin", password="somepassword", uploadId=2, list_target_chassis_only_dict=list_target_chassis_only_dict)
except Exception as e:
   if "timeout" not in str(e):
       raise 