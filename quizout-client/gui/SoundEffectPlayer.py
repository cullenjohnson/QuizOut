from typing import Dict
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QObject

from resources import soundEffectPaths
from utils.Enums import SoundEffect

class SoundEffectPlayer:
    soundEffects: Dict[SoundEffect, QSoundEffect] = {}
    SOUND_EFFECT_VOLUMES: Dict[SoundEffect, float] = {
        SoundEffect.ActivateSound: 1.0,
        SoundEffect.BuzzSound: 0.75,
        SoundEffect.CorrectSound: 0.75,
        SoundEffect.IncorrectSound: 0.9,
        SoundEffect.TimeoutSound: 0.6,
    }

    def __init__(self, parent:QObject):
        for effect in SoundEffect:
            self.soundEffects[effect] = self.initSoundEffect(effect, parent)

    def initSoundEffect(self, effect:SoundEffect, parent):
        qEffect = QSoundEffect(parent)
        qEffect.setSource(QUrl.fromLocalFile(soundEffectPaths[effect]))
        qEffect.setVolume(self.SOUND_EFFECT_VOLUMES[effect])

        return qEffect

    def playSound(self, effect:SoundEffect):
        if effect in self.soundEffects:
            self.soundEffects[effect].play()
