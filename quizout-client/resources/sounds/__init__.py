import os

from utils.Enums import SoundEffect

BASE_DIR = os.path.dirname(__file__)

paths = {
    SoundEffect.ActivateSound : os.path.abspath(os.path.join(BASE_DIR, "activate.611802__metalfortress__reminder2.wav")),
    SoundEffect.BuzzSound : os.path.abspath(os.path.join(BASE_DIR, "buzz.342749__rhodesmas__notification-01.wav")),
    SoundEffect.CorrectSound : os.path.abspath(os.path.join(BASE_DIR, "correct.611787__metalfortress__jingle_little_achievement2.wav")),
    SoundEffect.IncorrectSound : os.path.abspath(os.path.join(BASE_DIR, "incorrect.611798__metalfortress__error.wav")),
    SoundEffect.TimeoutSound : os.path.abspath(os.path.join(BASE_DIR, "timeout.745159__etheraudio__incorrect-buzzer-retro.wav"))
}