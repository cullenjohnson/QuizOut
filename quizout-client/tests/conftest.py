import pytest
import sys
import os
from configparser import ConfigParser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.TeamBuzzerInfo import TeamBuzzerInfo


@pytest.fixture
def sample_config():
    config = ConfigParser()
    config.read_dict({
        'Team A': 'a,b,c',
        'Team B': 'd,e,f', 
        'Team C': 'g,h,i'
    })
    return config


@pytest.fixture 
def team_buzzer_info(sample_config):
    return TeamBuzzerInfo(sample_config)