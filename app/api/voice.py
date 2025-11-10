"""
API endpoints for Voice capabilities (Speech-to-Text and Text-to-Speech)
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from app.services.voice_service import voice_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TTSRequest(BaseModel):
    """Text-to-Speech request model"""
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="alloy", description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)")
    format: str = Field(default="mp3", description="Output format (mp3, opus, aac, flac)")


@router.post("/stt", response_model=dict)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, etc.)"),
    language: str = None
):
    """
    Convert speech to text from uploaded audio file
    
    Supports:
    - WebM, MP3, WAV, M4A formats
    - Auto language detection or specify language code
    """
    try:
        audio_data = await audio.read()
        
        result = voice_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            format=audio.filename.split('.')[-1] if audio.filename else "webm"
        )
        
        return {
            "text": result["text"],
            "language": result.get("language"),
            "confidence": result.get("confidence", 1.0)
        }
    except Exception as e:
        logger.error(f"Error in speech-to-text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts", response_model=dict)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    
    Returns base64-encoded audio data
    """
    try:
        audio_base64 = voice_service.text_to_speech_base64(
            text=request.text,
            voice=request.voice,
            format=request.format
        )
        
        return {
            "audio": audio_base64,
            "format": request.format,
            "voice": request.voice,
            "text_length": len(request.text)
        }
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-memory", response_model=dict)
async def create_memory_from_voice(
    audio: UploadFile = File(...),
    language: str = None
):
    """
    Create a memory from voice input
    
    Flow:
    1. Convert speech to text
    2. Create memory from transcribed text
    3. Return memory with transcription
    """
    try:
        from app.services.memory_service import memory_service
        
        # Transcribe audio
        audio_data = await audio.read()
        transcription = voice_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            format=audio.filename.split('.')[-1] if audio.filename else "webm"
        )
        
        # Create memory from transcription
        memory = memory_service.create_memory(
            content=transcription["text"],
            metadata={
                "source": "voice",
                "language": transcription.get("language"),
                "audio_filename": audio.filename
            },
            source_type="voice",
            source_id=f"voice_{audio.filename}" if audio.filename else None
        )
        
        return {
            "memory": {
                "id": memory.id,
                "content": memory.content,
                "created_at": memory.created_at.isoformat()
            },
            "transcription": {
                "text": transcription["text"],
                "language": transcription.get("language"),
                "confidence": transcription.get("confidence", 1.0)
            }
        }
    except Exception as e:
        logger.error(f"Error creating memory from voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-rag", response_model=dict)
async def voice_rag_query(
    audio: UploadFile = File(...),
    language: str = None,
    retrieval_limit: int = 10,
    rerank: bool = True,
    model: str = "gpt-4"
):
    """
    Complete voice-to-voice RAG pipeline
    
    Flow:
    1. Convert speech to text
    2. Perform RAG query
    3. Convert answer to speech
    4. Return text answer + audio response
    """
    try:
        from app.services.rag_service import rag_service
        
        # Transcribe audio
        audio_data = await audio.read()
        transcription = voice_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            format=audio.filename.split('.')[-1] if audio.filename else "webm"
        )
        
        query_text = transcription["text"]
        
        # Perform RAG query
        rag_result = rag_service.rag_query(
            query=query_text,
            retrieval_limit=retrieval_limit,
            rerank=rerank,
            model=model
        )
        
        # Convert answer to speech
        audio_answer = voice_service.text_to_speech_base64(
            text=rag_result["answer"],
            voice="alloy",
            format="mp3"
        )
        
        return {
            "query": {
                "text": query_text,
                "language": transcription.get("language")
            },
            "answer": {
                "text": rag_result["answer"],
                "audio": audio_answer,
                "format": "mp3"
            },
            "citations": rag_result["citations"],
            "metadata": {
                "tokens_used": rag_result.get("tokens_used"),
                "total_time_ms": rag_result.get("total_time_ms")
            }
        }
    except Exception as e:
        logger.error(f"Error in voice RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

