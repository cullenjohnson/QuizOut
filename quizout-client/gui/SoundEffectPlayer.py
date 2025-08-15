from typing import Dict
import pygame
import logging
from PySide6.QtCore import QObject

from resources import soundEffectPaths
from utils.Enums import SoundEffect

logger = logging.getLogger(__name__)

class SoundEffectPlayer:
    soundEffects: Dict[SoundEffect, pygame.mixer.Sound] = {}
    SOUND_EFFECT_VOLUMES: Dict[SoundEffect, float] = {
        SoundEffect.ActivateSound: 1.0,
        SoundEffect.BuzzSound: 1.0,
        SoundEffect.CorrectSound: 1.0,
        SoundEffect.IncorrectSound: 1.0,
        SoundEffect.TimeoutSound: 1.0,
    }

    def __init__(self, parent: QObject):
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        for effect in SoundEffect:
            self.soundEffects[effect] = self.initSoundEffect(effect)

    def initSoundEffect(self, effect: SoundEffect):
        try:
            logger.info(f"Initializing sound effect {effect.name}...")
            sound = pygame.mixer.Sound(soundEffectPaths[effect])
            sound.set_volume(self.SOUND_EFFECT_VOLUMES[effect])
            logger.info(f"Sound effect {effect.name} initialized.")
            return sound
        except pygame.error as e:
            logger.error(f"Error loading sound effect {effect.name}: {e}")
            # Return a dummy sound object that won't crash when played
            return pygame.mixer.Sound(buffer=b'\x00' * 1024)  # Silent sound

    def playSound(self, effect: SoundEffect):
        if effect in self.soundEffects:
            try:
                logger.info(f"Playing sound {effect.name}")
                self.soundEffects[effect].play()
            except pygame.error as e:
                logger.error(f"Error playing sound effect {effect.name}: {e}")

    def __del__(self):
        # Clean up pygame mixer when the object is destroyed
        # Note: Only quit if no other sounds are playing
        try:
            pygame.mixer.quit()
        except:
            pass  # Ignore errors during cleanup
