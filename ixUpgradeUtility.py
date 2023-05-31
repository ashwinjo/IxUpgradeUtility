import json
from datetime import datetime, timezone

def get_packages_on_controller_chassis(session):
    return session.get_packages()
     
def add_target_chassis_to_controller_chassis(session, target_chassis_list):
    return session.add_target_chassis_to_controller_chassis(target_chassis_list)

def upgrade_target_chassis(session, uploadId=None, list_target_chassis_only_dict=None):
    return session.upgrade_target_chassis(uploadId=uploadId, list_target_chassis_only_dict=list_target_chassis_only_dict)

def authenticate_target_chassis(session, list_target_chassis_only_dict):
    return session.authenticate_target_chassis(list_target_chassis_only_dict)

def get_target_chassis_information(session):
    return session.get_target_chassis_information()
