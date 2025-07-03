from configparser import ConfigParser

class QuizSessionConfig:
    def __init__(self, config:ConfigParser):
        self.buzzerTeams = dict[str,str]()

        for team in config.keys():
            keyListStr = config.get(team)
            keyList = keyListStr.split(',')
            for key in keyList:
                if key in self.buzzerTeams.keys():
                    if self.buzzerTeams[key] is team:
                        continue

                    raise ValueError(f"The team_keys configuration assigns the '{key}' to more than one team.")
                    
                self.buzzerTeams[key] = team