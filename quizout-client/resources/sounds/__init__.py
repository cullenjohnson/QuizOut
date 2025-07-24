import os

from utils.Enums import SoundEffect

paths = {
    SoundEffect.ActivateSound : os.path.abspath("activate.611802__metalfortress__reminder2.wav"),
    SoundEffect.BuzzSound : os.path.abspath("buzz.342749__rhodesmas__notification-01.wav"),
    SoundEffect.CorrectSound : os.path.abspath("correct.611787__metalfortress__jingle_little_achievement2.wav"),
    SoundEffect.IncorrectSound : os.path.abspath("incorrect.611798__metalfortress__error.wav"),
    SoundEffect.TimeoutSound : os.path.abspath("timeout.745159__etheraudio__incorrect-buzzer-retro.wav")
}