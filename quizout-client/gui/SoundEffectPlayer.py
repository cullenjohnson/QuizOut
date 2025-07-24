from typing import Dict
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

from resources import soundEffectPaths
from utils.Enums import SoundEffect

class SoundEffectPlayer:
    soundEffects: Dict[SoundEffect, QSoundEffect] = {}

    def __init__(self):
        activateEffect = QSoundEffect()
        activateEffect.setSource(QUrl.fromLocalFile(soundEffectPaths[SoundEffect.ActivateSound]))
        # activateEffect.setVolume(1.0)

        self.soundEffects[SoundEffect.ActivateSound] = activateEffect

    def playSound(self, effect:SoundEffect):
        if effect in self.soundEffects:
            self.soundEffects[effect].play()
