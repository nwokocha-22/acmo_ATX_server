import time
import pickle
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict

#: The copy Policy class loads the user's copy Policy on start up. 
#: a new policy config file is created if it does not already exist
#: The loaded policy config file can be used to check if the user has defaulted and the time that occured
#: from the time, we can estimate if it is up to 24 hours
#: if 24hrs has passed, the restriction is relaxed
#: if not the user is restricted from copying anything at all


def _createPolicyConfig():
    """ 
    Creates and saves the logConfig file
    ---------------------------
    Keys                default values
    ---
    hasDefauted:bool    False
    time_defauted: datetime = None
    """

    config = {"hasDefaulted":False, "timeDefaulted":None}
    try:
        with open('policyConfig', 'xb') as logConfig:
            pickle.dump(config, logConfig)
    except FileExistsError:
        print("log config file already exists")

def _loadPolicyConfig():
    """ Loads the log config for writing """

    if not Path("policyConfig").exists():
        _createPolicyConfig()

    with open('policyConfig', 'rb') as logConfig:
        log_config = pickle.load(logConfig)
        print("log config", log_config)
    return log_config
     
        

@dataclass
class CopyPolicy():

    #policy:Dict = field(default_factory=_loadPolicyConfig)
    policy = _loadPolicyConfig()
    def checkPolicyStatus(self):
        """ 
            When Script is started, checks if the current user has defaulted by copying file size more than
            500 in one hour, or 1500 in 24 hours. 
            if yes, checks if it has been more than 24 hours.
            If more than 24 hours, enables the clipboard. If less, ensures the clipboard remain disabled.
        """
       
        if self.policy["hasDefaulted"]:
            seconds = datetime.timedelta(time.time() - self.policy["timeDefaulted"]).seconds
            if seconds:
                time_elapsed_hour = seconds // 3600
                if time_elapsed_hour >= 24:
                    #: Enable clipboard
                    print("clipboard Enabled")
                    pass
                else:
                    #: Keep clipboard disabled
                    print("clipboard disabled. elapse time:", time_elapsed_hour)
                    pass

    def updatePolicy(self, hasDefaulted=False, timeDefaulted=None):
        """
        updates the copyPolicy loaded on script startup
        """
        policy = {**self.policy, 'hasDefaulted':hasDefaulted, 'timeDefaulted': timeDefaulted}
        with open('policyConfig', 'wb') as config:
            pickle.dump(policy, config)
       

# if __name__=="__main__":
#     from datetime import datetime
#     date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#     copyPolicy =CopyPolicy()
#     print(copyPolicy.policy)
#     policy = copyPolicy.policy
#     copyPolicy.updatePolicy(True, date)
  


        