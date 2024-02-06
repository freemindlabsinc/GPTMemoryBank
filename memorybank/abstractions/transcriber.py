from loguru import logger
import numpy as np
from abc import ABC

class Transcriber(ABC):
    def __init__(self):
        # TODO pass appsettings and use config
        logger.debug("Creating speech recognition pipeline...")
        
        from transformers import pipeline
        self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

    def transcribe(self, audio) -> str:
        logger.debug("Transcribing audio...")
        
        sr, y = audio
        y = y.astype(np.float32)
        y /= np.max(np.abs(y))

        txt = self.transcriber({"sampling_rate": sr, "raw": y})["text"]
        return txt