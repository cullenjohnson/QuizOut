import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from configparser import ConfigParser
from PySide6.QtWidgets import QMainWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from buzzerlogic.TieBreaker import TieBreaker
from data.TeamBuzzerInfo import TeamBuzzerInfo


@pytest.fixture(scope="function")
def teamBuzzerInfo():
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
def tieBreaker(teamBuzzerInfo, qtbot):
    tieBreaker = TieBreaker(teamBuzzerInfo, tieThresholdMS = 2, freezeEarlyBuzzers = True, freezeTimeoutLengthMS = 500)
    qtbot.addWidget(TestWindow(tieBreaker))
    yield tieBreaker
    tieBreaker.fullReset()

class TestWindow(QMainWindow):
    tieBreaker:TieBreaker

    def __init__(self, newTieBreaker):
        tieBreaker = newTieBreaker


class TestTieBreakerInitialization:
    
    def test_initialization(self, teamBuzzerInfo):
        tieBreaker = TieBreaker(teamBuzzerInfo, tieThresholdMS=5)
        
        assert tieBreaker.teamBuzzerInfo == teamBuzzerInfo
        assert tieBreaker.allTeams == teamBuzzerInfo.teams
        assert tieBreaker.chosenTeams == []
        assert tieBreaker.tieThresholdMS == 5
        assert tieBreaker.keypress is None
        assert tieBreaker.afterBuzzTimer.isSingleShot()
    
    def test_default_tie_threshold(self, teamBuzzerInfo):
        tieBreaker = TieBreaker(teamBuzzerInfo, tieThresholdMS=10)
        assert tieBreaker.tieThresholdMS == 10


class TestHandleKeyPressMethod:
    
    @patch('buzzerlogic.TieBreaker.logger')
    def test_handleKeyPress_ignores_inactive_teams(self, mockLogger, tieBreaker):
        keypress_info = ('Team A', 'a', 1000)
        inactive_teams = ['Team A']
        tieBreaker.startListening()
        tieBreaker.handleKeyPress(keypress_info, inactive_teams)
        
        mockLogger.info.assert_called_once_with(
            "Keypress ignored because Team A is one of the inactive teams. (['Team A'])"
        )
        assert not tieBreaker.afterBuzzTimer.isActive()
        tieBreaker.stopListening()
    
    @patch('buzzerlogic.TieBreaker.logger')
    def test_handleKeyPress_freezes_early_buzzes(self, mockLogger, tieBreaker):
        keypressInfo1 = ('Team A', 'a', 1000)
        keypressInfo2 = ('Team A', 'a', 1200)
        keypressInfo3 = ('Team A', 'a', 1500)
        keypressInfo4 = ('Team A', 'a', 1600)
        tieBreaker.handleKeyPress(keypressInfo1)
        
        mockLogger.info.assert_called_once_with("Buzzer 'a' frozen for buzzing in too early")
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo1)

        # Verify subsequent buzzes from frozen buzzers are frozen until after the freeze timeout
        tieBreaker.startListening()
        tieBreaker.handleKeyPress(keypressInfo2)
        mockLogger.info.assert_called_with("Keypress ignored because buzzer 'a' has been frozen")
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo2)
        
        tieBreaker.handleKeyPress(keypressInfo3)
        mockLogger.info.assert_called_with("Keypress ignored because buzzer 'a' has been frozen")
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo3)

        # Keypress 4 is valid now that the freeze timeout has expired
        tieBreaker.handleKeyPress(keypressInfo4)
        assert tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress == keypressInfo4
        assert not tieBreaker.isFrozen(keypressInfo4)

        # Verify resetFrozen Buzzers un-freezes buzzer 'a'
        tieBreaker.resetFrozenBuzzers()
        assert not tieBreaker.isFrozen(keypressInfo1)
        assert not tieBreaker.isFrozen(keypressInfo2)
        assert not tieBreaker.isFrozen(keypressInfo3)
        assert not tieBreaker.isFrozen(keypressInfo4)
        tieBreaker.stopListening()

    @patch('buzzerlogic.TieBreaker.logger')
    def test_handleKeyPress_freeze_early_buzzes_disabled(self, mockLogger, tieBreaker):
        tieBreaker.freezeEarlyBuzzers = False
        keypressInfo = ('Team A', 'a', 1000)
        tieBreaker.handleKeyPress(keypressInfo)
                
        mockLogger.info.assert_called_with(f"Buzzer 'a' ignored because it was too early")
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert not tieBreaker.isFrozen(keypressInfo)
        tieBreaker.freezeEarlyBuzzers = True

    def test_handleKeyPress_frozen_players_dont_affect_other_players(self, tieBreaker):
        keypressInfo1 = ('Team A', 'a', 1000)
        keypressInfo2 = ('Team A', 'b', 1200)
        keypressInfo3 = ('Team B', 'c', 1500)
        tieBreaker.handleKeyPress(keypressInfo1)
        
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo1)

        # Verify other players aren't affected by the frozen buzzer.
        tieBreaker.startListening()
        tieBreaker.handleKeyPress(keypressInfo2)
        assert tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress == keypressInfo2
        assert not tieBreaker.isFrozen(keypressInfo2)
        
        tieBreaker.handleKeyPress(keypressInfo3)
        assert tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress == keypressInfo2
        assert not tieBreaker.isFrozen(keypressInfo3)

        tieBreaker.stopListening()

    def test_handleKeyPress_multiple_players_can_be_frozen(self, tieBreaker):
        keypressInfo1 = ('Team A', 'a', 1000)
        keypressInfo2 = ('Team B', 'c', 1200)
        keypressInfo3 = ('Team A', 'a', 1250)
        keypressInfo4 = ('Team B', 'c', 1300)
        keypressInfo5 = ('Team A', 'b', 1500)
        tieBreaker.handleKeyPress(keypressInfo1)
        
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo1)

        tieBreaker.handleKeyPress(keypressInfo2)
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo2)
        
        tieBreaker.startListening()

        # Verify players a and c are frozen
        tieBreaker.handleKeyPress(keypressInfo3)
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo3)

        tieBreaker.handleKeyPress(keypressInfo4)
        assert not tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress is None
        assert tieBreaker.isFrozen(keypressInfo4)

        tieBreaker.handleKeyPress(keypressInfo5)
        assert tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.keypress == keypressInfo5
        assert not tieBreaker.isFrozen(keypressInfo5)

        tieBreaker.stopListening()
    
    def test_handleKeyPress_starts_timer_on_first_keypress(self, tieBreaker):
        keypressInfo = ('Team A', 'a', 1000)
        
        tieBreaker.startListening()
        tieBreaker.handleKeyPress(keypressInfo)
        
        assert tieBreaker.afterBuzzTimer.isActive()
        assert tieBreaker.afterBuzzTimer.interval() == 500
        assert tieBreaker.keypress == keypressInfo
        assert tieBreaker.randomlyChosenTeam is None
        tieBreaker.stopListening()
    
    def test_handleKeyPress_calls_pick_winner_on_second_keypress(self, tieBreaker):
        firstKeypress = ('Team A', 'a', 1000)
        secondKeypress = ('Team B', 'd', 1001)
        
        tieBreaker.startListening()
        with patch.object(tieBreaker, 'pickAWinner', return_value = firstKeypress) as mockPick:
            tieBreaker.handleKeyPress(firstKeypress)
            tieBreaker.handleKeyPress(secondKeypress)
            
            mockPick.assert_called_once_with(secondKeypress, firstKeypress)
        tieBreaker.stopListening()


class TestPickAWinnerMethod:
    
    def test_picks_faster_buzz_outside_threshold(self, tieBreaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1005)
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress1
    
    def test_picks_faster_buzz_reverse_order(self, tieBreaker):
        keypress1 = ('Team A', 'a', 1005)
        keypress2 = ('Team B', 'd', 1000)
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress2
    
    @patch('buzzerlogic.TieBreaker.random.choice')
    def test_random_choice_for_same_team_tie(self, mockChoice, tieBreaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team A', 'b', 1001)
        mockChoice.return_value = keypress1
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        mockChoice.assert_called_once_with([keypress1, keypress2])
        assert result == keypress1
    
    @patch('buzzerlogic.TieBreaker.random.choice')
    @patch('buzzerlogic.TieBreaker.logger')
    def test_random_choice_for_different_teams_no_history(self, mockLogger, mockChoice, tieBreaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        mockChoice.return_value = keypress1
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        mockChoice.assert_called_once_with([keypress1, keypress2])
        mockLogger.info.assert_called_with("TIE! Team A chosen by coin toss.")
        assert result == keypress1
        assert 'Team A' in tieBreaker.chosenTeams
        assert tieBreaker.randomlyChosenTeam == 'Team A'
    
    @patch('buzzerlogic.TieBreaker.logger')
    def test_prefers_less_recently_chosen_team(self, mockLogger, tieBreaker):
        tieBreaker.chosenTeams = ['Team B', 'Team A']
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team C', 'g', 1001)
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress2
        mockLogger.info.assert_called_with("TIE! Team C chosen because Team A was randomly chosen more recently.")
        assert tieBreaker.chosenTeams[-1] == 'Team C'
    
    @patch('buzzerlogic.TieBreaker.logger')
    def test_sticks_with_previously_randomly_chosen_team(self, mockLogger, tieBreaker):
        tieBreaker.randomlyChosenTeam = 'Team A'
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        assert result == keypress1
        mockLogger.info.assert_called_with("TIE! Team A chosen because they were already randomly chosen in the current tiebreaker session.")
    
    def test_resets_chosen_teams_when_all_chosen(self, tieBreaker):
        tieBreaker.chosenTeams = ['Team A', 'Team B', 'Team C']
        tieBreaker.allTeams = ['Team A', 'Team B', 'Team C']
        
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1001)
        
        with patch('buzzerlogic.TieBreaker.random.choice', return_value=keypress1):
            tieBreaker.pickAWinner(keypress1, keypress2)
            
            assert len(tieBreaker.chosenTeams) == 1


class TestTimeoutBehavior:
    
    def test_onAfterBuzzTimeout_emits_keypress(self, tieBreaker):
        keypressInfo = ('Team A', 'a', 1000)
        tieBreaker.keypress = keypressInfo
        
        with patch.object(tieBreaker, 'playerChosen') as mockSignal:
            tieBreaker.onAfterBuzzTimeout()
            
            mockSignal.emit.assert_called_once_with(keypressInfo)


class TestEdgeCases:
    
    def test_exact_tie_threshold_boundary(self, tieBreaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1002)
        
        with patch('buzzerlogic.TieBreaker.random.choice', return_value=keypress1):
            result = tieBreaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress1
    
    def test_zero_time_difference(self, tieBreaker):
        keypress1 = ('Team A', 'a', 1000)
        keypress2 = ('Team B', 'd', 1000)
        
        with patch('buzzerlogic.TieBreaker.random.choice', return_value=keypress2):
            result = tieBreaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress2
    
    def test_negative_time_difference_within_threshold(self, tieBreaker):
        keypress1 = ('Team A', 'a', 1002)
        keypress2 = ('Team B', 'd', 1000)
        
        with patch('buzzerlogic.TieBreaker.random.choice', return_value=keypress1):
            result = tieBreaker.pickAWinner(keypress1, keypress2)
            
            assert result == keypress1


class TestSignalEmission:
    
    def test_signal_connection(self, tieBreaker):
        assert hasattr(tieBreaker, 'playerChosen')
        assert tieBreaker.playerChosen is not None


class TestMultipleHandleKeypresses:
    
    def test_multiple_handleKeyPress_calls_with_timer_active(self, tieBreaker):
        firstKeypress = ('Team A', 'a', 1000)
        secondKeypress = ('Team B', 'd', 1001)
        thirdKeypress = ('Team C', 'g', 1002)
        
        tieBreaker.startListening()
        tieBreaker.handleKeyPress(firstKeypress)
        assert tieBreaker.afterBuzzTimer.isActive()
        
        with patch.object(tieBreaker, 'pickAWinner', side_effect=[secondKeypress, thirdKeypress]) as mockPick:
            tieBreaker.handleKeyPress(secondKeypress)
            tieBreaker.handleKeyPress(thirdKeypress)
            
            assert mockPick.call_count == 2
            assert tieBreaker.keypress == thirdKeypress
        tieBreaker.stopListening()


@pytest.mark.parametrize("threshold, timeDiff, expectedTie", [
    (2, 1, True),
    (2, 2, True),
    (2, 3, False),
    (5, 4, True),
    (5, 6, False),
    (0, 0, True),
    (0, 1, False),
])
def test_tie_threshold_scenarios(teamBuzzerInfo, threshold, timeDiff, expectedTie):
    tieBreaker = TieBreaker(teamBuzzerInfo, tieThresholdMS=threshold)
    
    keypress1 = ('Team A', 'a', 1000)
    keypress2 = ('Team B', 'd', 1000 + timeDiff)

    tieBreaker.startListening()
    
    with patch('buzzerlogic.TieBreaker.random.choice', return_value=keypress1) as mockChoice:
        result = tieBreaker.pickAWinner(keypress1, keypress2)
        
        if expectedTie:
            mockChoice.assert_called_once()
        else:
            mockChoice.assert_not_called()
            assert result == keypress1
    tieBreaker.stopListening()