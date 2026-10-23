"""
Procedural Retro Sound Effects Generator and Manager for RetroSNES.
Generates authentic 8-bit / 16-bit sound effects directly in memory.
No external sound files required.
"""

import math
import struct
import io
import wave

class SoundManager:
    def __init__(self, enabled=True, volume=0.8):
        self.enabled = enabled
        self.volume = max(0.0, min(1.0, volume))
        self.initialized = False
        self.sounds = {}
        
        self._init_mixer()
        if self.initialized:
            self._generate_sounds()

    def _init_mixer(self):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)
            self.initialized = True
        except Exception:
            self.initialized = False

    def _generate_wav_bytes(self, samples, sample_rate=44100) -> bytes:
        """Packages raw float samples (-1.0 to 1.0) into WAV file bytes in memory."""
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(sample_rate)
            raw_data = bytearray()
            for s in samples:
                val = max(-32767, min(32767, int(s * 32767)))
                raw_data.extend(struct.pack('<h', val))
            wf.writeframes(raw_data)
        return wav_io.getvalue()

    def _generate_sounds(self):
        try:
            import pygame
            sample_rate = 44100

            # 1. Nav Move Blip (Crisp retro blip: 650Hz -> 850Hz over 35ms)
            duration = 0.035
            n_samples = int(sample_rate * duration)
            samples = []
            for i in range(n_samples):
                t = i / sample_rate
                f = 650 + (200 * (i / n_samples))
                # Square wave with slight smoothing
                phase = (t * f) % 1.0
                val = 0.6 if phase < 0.5 else -0.6
                env = 1.0 - (i / n_samples)
                samples.append(val * env)
            wav_bytes = self._generate_wav_bytes(samples, sample_rate)
            self.sounds['nav'] = pygame.mixer.Sound(io.BytesIO(wav_bytes))

            # 2. Select / Confirm Chime (SNES 2-tone bell: 880Hz + 1760Hz, 150ms)
            duration = 0.15
            n_samples = int(sample_rate * duration)
            samples = []
            for i in range(n_samples):
                t = i / sample_rate
                s1 = math.sin(2 * math.pi * 880 * t)
                s2 = 0.5 * math.sin(2 * math.pi * 1760 * t)
                env = math.exp(-12.0 * t)
                samples.append((s1 + s2) * 0.5 * env)
            wav_bytes = self._generate_wav_bytes(samples, sample_rate)
            self.sounds['select'] = pygame.mixer.Sound(io.BytesIO(wav_bytes))

            # 3. Back / Cancel Blip (Downward tone 480Hz -> 240Hz, 50ms)
            duration = 0.05
            n_samples = int(sample_rate * duration)
            samples = []
            for i in range(n_samples):
                t = i / sample_rate
                f = 480 - (240 * (i / n_samples))
                phase = (t * f) % 1.0
                val = 0.5 if phase < 0.5 else -0.5
                env = 1.0 - (i / n_samples)
                samples.append(val * env)
            wav_bytes = self._generate_wav_bytes(samples, sample_rate)
            self.sounds['back'] = pygame.mixer.Sound(io.BytesIO(wav_bytes))

            # 4. Launch Fanfare (Ascending arpeggio: C5, E5, G5, C6)
            notes = [523.25, 659.25, 783.99, 1046.50]
            note_dur = 0.065
            samples = []
            for note_freq in notes:
                n_note = int(sample_rate * note_dur)
                for i in range(n_note):
                    t = i / sample_rate
                    # Blend triangle and sine
                    triangle = 2.0 * abs(2.0 * ((t * note_freq) % 1.0) - 1.0) - 1.0
                    sine = math.sin(2 * math.pi * note_freq * t)
                    val = 0.6 * triangle + 0.4 * sine
                    env = 1.0 - (i / n_note) * 0.4
                    samples.append(val * env * 0.6)
            wav_bytes = self._generate_wav_bytes(samples, sample_rate)
            self.sounds['launch'] = pygame.mixer.Sound(io.BytesIO(wav_bytes))

            self.set_volume(self.volume)
        except Exception as e:
            print(f"[SoundManager] Could not synthesize sounds: {e}")

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        if not self.initialized:
            return
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.volume)
            except Exception:
                pass

    def play(self, name: str):
        if not self.enabled or not self.initialized:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
