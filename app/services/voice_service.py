"""
Voice Service for Speech-to-Text and Text-to-Speech
"""
from typing import Optional, Dict, Any
import logging
import io
import base64
from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice input/output capabilities"""
    
    def __init__(self):
        self.stt_model = None
        self.tts_model = None
        self._init_models()
    
    def _init_models(self):
        """Initialize STT and TTS models"""
        try:
            # Try OpenAI Whisper for STT
            if settings.openai_api_key:
                self.stt_type = "openai_whisper"
                logger.info("Using OpenAI Whisper for STT")
            else:
                # Fallback to local Whisper
                try:
                    import whisper
                    self.stt_model = whisper.load_model("base")
                    self.stt_type = "local_whisper"
                    logger.info("Using local Whisper for STT")
                except ImportError:
                    self.stt_type = "none"
                    logger.warning("Whisper not installed. STT disabled.")
        except Exception as e:
            logger.error(f"Error initializing STT: {e}")
            self.stt_type = "none"
        
        # TTS can use OpenAI TTS or Google TTS
        try:
            if settings.openai_api_key:
                self.tts_type = "openai"
                logger.info("Using OpenAI TTS")
            else:
                # Try Google TTS
                try:
                    from gtts import gTTS
                    self.tts_type = "google"
                    logger.info("Using Google TTS")
                except ImportError:
                    self.tts_type = "none"
                    logger.warning("TTS libraries not installed")
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            self.tts_type = "none"
    
    def speech_to_text(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "webm"
    ) -> Dict[str, Any]:
        """
        Convert speech to text
        
        Args:
            audio_data: Audio file bytes
            language: Language code (optional, auto-detect if None)
            format: Audio format (webm, mp3, wav, etc.)
            
        Returns:
            Dictionary with transcribed text and metadata
        """
        if self.stt_type == "none":
            raise ValueError("Speech-to-text not available")
        
        try:
            if self.stt_type == "openai_whisper":
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                
                # Save audio to temporary file
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                try:
                    with open(tmp_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language=language
                        )
                    
                    return {
                        "text": transcript.text,
                        "language": transcript.language if hasattr(transcript, 'language') else None,
                        "confidence": 1.0  # OpenAI doesn't provide confidence
                    }
                finally:
                    os.unlink(tmp_path)
            
            elif self.stt_type == "local_whisper":
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                try:
                    result = self.stt_model.transcribe(tmp_path, language=language)
                    return {
                        "text": result["text"],
                        "language": result.get("language"),
                        "confidence": 1.0
                    }
                finally:
                    os.unlink(tmp_path)
            
        except Exception as e:
            logger.error(f"Error in speech-to-text: {e}")
            raise
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        format: str = "mp3"
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer for OpenAI)
            format: Output format (mp3, opus, aac, flac)
            
        Returns:
            Audio file bytes
        """
        if self.tts_type == "none":
            raise ValueError("Text-to-speech not available")
        
        try:
            if self.tts_type == "openai":
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                
                return response.content
            
            elif self.tts_type == "google":
                from gtts import gTTS
                import io
                
                tts = gTTS(text=text, lang='en')
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                return audio_buffer.read()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            raise
    
    def text_to_speech_base64(
        self,
        text: str,
        voice: str = "alloy",
        format: str = "mp3"
    ) -> str:
        """
        Convert text to speech and return as base64 encoded string
        
        Args:
            text: Text to convert
            voice: Voice to use
            format: Output format
            
        Returns:
            Base64 encoded audio string
        """
        audio_bytes = self.text_to_speech(text, voice, format)
        return base64.b64encode(audio_bytes).decode('utf-8')


# Global service instance
voice_service = VoiceService()

