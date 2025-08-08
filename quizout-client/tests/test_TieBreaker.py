import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from configparser import ConfigParser
from PySide6.QtWidgets import QMainWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.TieBreaker import TieBreaker
from data.TeamBuzzerInfo import TeamBuzzerInfo


@pytest.fixture
def team_buzzer_info():
    testTeams = {
        "team_buzzer_keys": {
            "Team A": "1,2,3",
            "Team B": "4,5,6",
            "Team C": "7,8,9"
    }}
    config = ConfigParser()
    config.read_dict(testTeams)
    return TeamBuzzerInfo(config["team_buzzer_keys"])


@pytest.fixture
def tie_breaker(team_buzzer_info, qtbot):
    tie_breaker = TieBreaker(team_buzzer_info, tieThresholdMS=2)
    qtbot.addWidget(TestWindow(tie_breaker))
    return tie_breaker

class TestWindow(QMainWindow):
    tieBreaker:TieBreaker

    def __init__(self, new_tie_breaker):
        tie_breaker = new_tie_breaker


class TestTieBreakerInitialization:
    
    def test_initialization(self, team_buzzer_info):
        tie_breaker = TieBreaker(team_buzzer_info, tieThresholdMS=5)
        
        assert tie_breaker.teamBuzzerInfo == team_buzzer_info
        assert tie_breaker.allTeams == team_buzzer_info.teams
        assert tie_breaker.chosenTeams == []
        assert tie_breaker.tieThresholdMS == 5
        assert tie_breaker.keypress is None
        assert tie_breaker.timer.isSingleShot()
    
    def test_default_tie_threshold(self, team_buzzer_info):
        tie_breaker = TieBreaker(team_buzzer_info, tieThresholdMS=10)
        assert tie_breaker.tieThresholdMS == 10


class TestActivateMethod:
    
    @patch('utils.TieBreaker.logger')
    def test_activate_ignores_inactive_teams(self, mock_logger, tie_breaker):
        keypress_info = ('Team A', 'a', 1000)
        inactive_teams = ['Team A']
        
        tie_breaker.activate(keypress_info, inactive_teams)
        
        mock_logger.info.assert_called_once_with(
            "Keypress ignored because Team A is one of the inactive teams. (['Team A'])"
        )
        assert not tie_breaker.timer.isActive()
    
    def test_activate_starts_timer_on_first_keypress(self, tie_breaker):
        keypress_info = ('Team A', 'a', 1000)
        
        tie_breaker.activate(keypress_info)
        
        assert tie_breaker.timer.isActive()
        assert tie_breaker.timer.interval() == 500
        assert tie_breaker.keypress == keypress_info
        assert tie_breaker.randomlyChosenTeam is None
    
    def test_activate_calls_pick_winner_on_second_keypress(self, tie_breaker):
        first_keypress = ('Team A', 'a', 1000)
        second_keypress = ('Team B', 'd', 1001)
        
        with patch.object(tie_breaker, 'pickAWinner', return_value=first_keypress) as mock_pick:
            tie_breaker.activate(first_keypress)
            tie_breaker.activate(second_keypress)
            
            mock_pick.assert_called_once_with(second_keypress, first_keypress)


class TestPickAWinnerMethod:
    
    def test_picks_faster_buzz_outside_threshold(self, tie_breaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1005)
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress1
    
    def test_picks_faster_buzz_reverse_order(self, tie_breaker):
        keypress1 = ('Team A', 'a', 1005)
        keypress2 = ('Team B', 'd', 1000)
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress2
    
    @patch('utils.TieBreaker.random.choice')
    def test_random_choice_for_same_team_tie(self, mock_choice, tie_breaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team A', 'b', 1001)
        mock_choice.return_value = keypress1
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        mock_choice.assert_called_once_with([keypress1, keypress2])
        assert result == keypress1
    
    @patch('utils.TieBreaker.random.choice')
    @patch('utils.TieBreaker.logger')
    def test_random_choice_for_different_teams_no_history(self, mock_logger, mock_choice, tie_breaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        mock_choice.return_value = keypress1
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        mock_choice.assert_called_once_with([keypress1, keypress2])
        mock_logger.info.assert_called_with("TIE! Team A chosen by coin toss.")
        assert result == keypress1
        assert 'Team A' in tie_breaker.chosenTeams
        assert tie_breaker.randomlyChosenTeam == 'Team A'
    
    @patch('utils.TieBreaker.logger')
    def test_prefers_less_recently_chosen_team(self, mock_logger, tie_breaker):
        tie_breaker.chosenTeams = ['Team B', 'Team A']
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team C', 'g', 1001)
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress2
        mock_logger.info.assert_called_with("TIE! Team C chosen because Team A was randomly chosen more recently.")
        assert tie_breaker.chosenTeams[-1] == 'Team C'
    
    @patch('utils.TieBreaker.logger')
    def test_sticks_with_previously_randomly_chosen_team(self, mock_logger, tie_breaker):
        tie_breaker.randomlyChosenTeam = 'Team A'
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress1
        mock_logger.info.assert_called_with("TIE! Team A chosen because they were already randomly chosen in the current tiebreaker session.")
    
    def test_resets_chosen_teams_when_all_chosen(self, tie_breaker):
        tie_breaker.chosenTeams = ['Team A', 'Team B', 'Team C']
        tie_breaker.allTeams = ['Team A', 'Team B', 'Team C']
        
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        
        with patch('utils.TieBreaker.random.choice', return_value=keypress1):
            tie_breaker.pickAWinner(keypress1, keypress2)
            
            assert len(tie_breaker.chosenTeams) == 1


class TestTimeoutBehavior:
    
    def test_on_timeout_emits_keypress(self, tie_breaker):
        keypress_info = ('Team A', 'a', 1000)
        tie_breaker.keypress = keypress_info
        
        with patch.object(tie_breaker, 'playerChosen') as mock_signal:
            tie_breaker.onTimeout()
            
            mock_signal.emit.assert_called_once_with(keypress_info)


class TestEdgeCases:
    
    def test_exact_tie_threshold_boundary(self, tie_breaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1002)
        
        with patch('utils.TieBreaker.random.choice', return_value=keypress1):
            result = tie_breaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress1
    
    def test_zero_time_difference(self, tie_breaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1000)
        
        with patch('utils.TieBreaker.random.choice', return_value=keypress2):
            result = tie_breaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress2
    
    def test_negative_time_difference_within_threshold(self, tie_breaker):
        keypress1 = ('Team A', 'a', 1002)
        keypress2 = ('Team B', 'd', 1000)
        
        with patch('utils.TieBreaker.random.choice', return_value=keypress1):
            result = tie_breaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress1


class TestSignalEmission:
    
    def test_signal_connection(self, tie_breaker):
        assert hasattr(tie_breaker, 'playerChosen')
        assert tie_breaker.playerChosen is not None


class TestMultipleActivations:
    
    def test_multiple_activations_with_timer_active(self, tie_breaker):
        first_keypress = ('Team A', 'a', 1000)
        second_keypress = ('Team B', 'd', 1001)
        third_keypress = ('Team C', 'g', 1002)
        
        tie_breaker.activate(first_keypress)
        assert tie_breaker.timer.isActive()
        
        with patch.object(tie_breaker, 'pickAWinner', side_effect=[second_keypress, third_keypress]) as mock_pick:
            tie_breaker.activate(second_keypress)
            tie_breaker.activate(third_keypress)
            
            assert mock_pick.call_count == 2
            assert tie_breaker.keypress == third_keypress


@pytest.mark.parametrize("threshold,time_diff,expected_tie", [
    (2, 1, True),
    (2, 2, True),
    (2, 3, False),
    (5, 4, True),
    (5, 6, False),
    (0, 0, True),
    (0, 1, False),
])
def test_tie_threshold_scenarios(team_buzzer_info, threshold, time_diff, expected_tie):
    tie_breaker = TieBreaker(team_buzzer_info, tieThresholdMS=threshold)
    
    keypress1 = ('Team A', 'a', 1000)
    keypress2 = ('Team B', 'd', 1000 + time_diff)
    
    with patch('utils.TieBreaker.random.choice', return_value=keypress1) as mock_choice:
        result = tie_breaker.pickAWinner(keypress1, keypress2)
        
        if expected_tie:
            mock_choice.assert_called_once()
        else:
            mock_choice.assert_not_called()
            assert result == keypress1