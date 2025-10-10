import numpy as np
import sounddevice as sd
import threading
class SoundStreamer:
    """
    Non-blocking audio streamer that plays up to 6 sine oscillators at once.
    - update_freqs(f1..f6) to change pitches live (any missing args keep previous).
    - set_gains(g1..g6) to adjust per-voice gains (0..1).
    - set_volume(amp) to scale the final mix (0..1).
    """
    def __init__(self, fs=48000, amp=0.25, device=None):
        self.fs = int(fs)
        self.amp = float(np.clip(amp, 0.0, 1.0))
        self.voices = 9

        # Shared state
        self._lock = threading.Lock()
        self._freqs = np.full(self.voices, 440.0, dtype=np.float64)   # Hz
        self._phase = np.zeros(self.voices, dtype=np.float64)         # radians
        self._gains = np.ones(self.voices, dtype=np.float64)          # per-voice [0..1]

        # Start one persistent output stream (mono) with a callback
        self._stream = sd.OutputStream(
            channels=1,
            samplerate=self.fs,
            dtype='float32',
            callback=self._callback,
            blocksize=0,           # let backend choose (low-latency)
            device=device          # None = default; or pass an output device index/name
        )
        self._stream.start()

    # ---------- Public API ----------
    def update_freqs(self, *freqs):
        """Update 1..6 frequencies (Hz). Omitted voices keep their previous freq."""
        if not freqs:
            return
        with self._lock:
            for i, f in enumerate(freqs[:self.voices]):
                self._freqs[i] = float(np.clip(f, 20.0, 20000.0))

    def set_gains(self, *gains):
        """Set per-voice gains (0..1). Omitted voices keep their previous gain."""
        if not gains:
            return
        with self._lock:
            for i, g in enumerate(gains[:self.voices]):
                self._gains[i] = float(np.clip(g, 0.0, 1.0))

    def set_volume(self, amp):
        """Set master volume (0..1)."""
        with self._lock:
            self.amp = float(np.clip(amp, 0.0, 1.0))

    def stop(self):
        self._stream.stop()
        self._stream.close()

    # ---------- Audio callback ----------
    def _callback(self, outdata, frames, time_info, status):
        if status:
            # print(status)  # optional debug
            pass

        # Snapshot state atomically
        with self._lock:
            freqs = self._freqs.copy()
            gains = self._gains.copy()
            amp   = self.amp
            phase = self._phase.copy()

        # Build samples
        n = np.arange(frames, dtype=np.float64)  # [0..frames-1]
        inc = (2.0 * np.pi * freqs) / self.fs    # per-voice phase increment

        # phases shape: (voices, frames)
        phases = phase[:, None] + inc[:, None] * n[None, :]
        sines = np.sin(phases) * gains[:, None]  # weight each voice

        # Mix down to mono with safe normalization to avoid clipping
        mix = sines.sum(axis=0)
        norm = np.sum(gains) if np.sum(gains) > 1e-12 else 1.0
        mix = (amp * mix / max(1.0, norm)).astype(np.float32)

        # Write and advance phase (keep continuity)
        outdata[:] = mix.reshape(-1, 1)
        phase = (phase + inc * frames) % (2.0 * np.pi)

        # Store new phases
        with self._lock:
            self._phase = phase
