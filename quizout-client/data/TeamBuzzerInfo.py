from configparser import ConfigParser
from typing import Dict,List

class TeamBuzzerInfo:
    buzzerTeams:Dict[str,str]
    teams:List[str]

    def __init__(self, config:ConfigParser):
        self.buzzerTeams = dict[str,str]()
        self.teams = []

        for team in config.keys():
            self.teams.append(team)
            keyListStr = config.get(team)
            keyList = keyListStr.split(',')
            for key in keyList:
                if key in self.buzzerTeams.keys():
                    if self.buzzerTeams[key] is team:
                        continue

                    raise ValueError(f"The team_keys configuration assigns the '{key}' to more than one team.")
                    
                self.buzzerTeams[key] = team