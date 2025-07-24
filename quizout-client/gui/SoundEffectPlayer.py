from typing import Dict
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QObject

from resources import soundEffectPaths
from utils.Enums import SoundEffect

class SoundEffectPlayer:
    soundEffects: Dict[SoundEffect, QSoundEffect] = {}

    def __init__(self, parent:QObject):
        for effect in SoundEffect:
            self.soundEffects[effect] = self.initSoundEffect(effect, parent)

    def initSoundEffect(self, effect:SoundEffect, parent):
        qEffect = QSoundEffect(parent)
        qEffect.setSource(QUrl.fromLocalFile(soundEffectPaths[effect]))
        qEffect.setVolume(1.0)

        return qEffect

    def playSound(self, effect:SoundEffect):
        if effect in self.soundEffects:
            self.soundEffects[effect].play()
