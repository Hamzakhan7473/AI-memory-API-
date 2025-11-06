"""
MemMachine Service for use case integration
Provides helper functions to interact with MemMachine API
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

MEMMACHINE_URL = "http://localhost:8080"


class MemMachineService:
    """Service for interacting with MemMachine API"""
    
    def __init__(self):
        self.base_url = MEMMACHINE_URL
        self.client = None
    
    async def _get_client(self):
        """Get or create httpx client"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client
    
    async def health_check(self) -> bool:
        """Check if MemMachine is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"MemMachine health check failed: {e}")
            return False
    
    async def create_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create or get a session in MemMachine
        
        Args:
            session_id: Unique session identifier
            metadata: Optional session metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # MemMachine sessions are created implicitly when first memory is added
            # Just verify health
            return await self.health_check()
        except Exception as e:
            logger.error(f"Error creating MemMachine session: {e}")
            return False
    
    async def add_memory(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a memory (episode) to MemMachine
        
        Args:
            session_id: Session identifier
            messages: List of message dicts with 'role' and 'content'
            metadata: Optional episode metadata
            
        Returns:
            MemMachine response or None if failed
        """
        try:
            client = await self._get_client()
            
            # Prepare episode data
            episode_data = {
                "session": session_id,
                "messages": messages,
                "metadata": metadata or {}
            }
            
            response = await client.post(
                f"{self.base_url}/v1/memories",
                json=episode_data,
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.warning(f"MemMachine add_memory returned {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Error adding memory to MemMachine: {e}")
            return None
    
    async def search_memories(
        self,
        session_id: str,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories in MemMachine
        
        Args:
            session_id: Session identifier
            query: Search query
            limit: Maximum number of results
            metadata_filter: Optional metadata filter
            
        Returns:
            List of matching memories
        """
        try:
            client = await self._get_client()
            
            # MemMachine search API expects session as object with session_id
            search_data = {
                "session": {"session_id": session_id} if isinstance(session_id, str) else session_id,
                "query": query,
                "limit": limit
            }
            
            if metadata_filter:
                search_data["metadata"] = metadata_filter
            
            response = await client.post(
                f"{self.base_url}/v1/memories/search",
                json=search_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # MemMachine returns results in this structure:
                # {
                #   "status": 0,
                #   "content": {
                #     "episodic_memory": [[], [episodes], [""]],
                #     "profile_memory": []
                #   }
                # }
                # Extract episodic memories from the nested arrays
                content = result.get("content", {})
                episodic_memories = content.get("episodic_memory", [])
                
                # Flatten the episodic_memories array (it's nested)
                episodes = []
                for memory_array in episodic_memories:
                    if isinstance(memory_array, list):
                        for episode in memory_array:
                            # Skip empty strings and non-dict items
                            if isinstance(episode, dict) and episode.get("uuid"):
                                episodes.append(episode)
                            elif isinstance(episode, str) and episode.strip():
                                # Handle string content
                                episodes.append({
                                    "uuid": f"ep_{len(episodes)}",
                                    "content": episode,
                                    "content_type": "string"
                                })
                
                return episodes
            else:
                logger.warning(f"MemMachine search returned {response.status_code}: {response.text}")
                return []
        except Exception as e:
            logger.warning(f"Error searching MemMachine memories: {e}")
            return []
    
    async def get_sessions(self) -> List[str]:
        """Get all active sessions"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/v1/sessions", timeout=10.0)
            
            if response.status_code == 200:
                result = response.json()
                sessions = result.get("sessions", [])
                
                # MemMachine returns sessions as objects with session_id field
                # Extract session_id strings from the response
                session_ids = []
                for session in sessions:
                    if isinstance(session, dict):
                        # If it's a dict, extract session_id
                        session_id = session.get("session_id") or session.get("id")
                        if session_id:
                            session_ids.append(str(session_id))
                    elif isinstance(session, str):
                        # If it's already a string, use it directly
                        session_ids.append(session)
                
                return session_ids
            return []
        except Exception as e:
            logger.warning(f"Error getting MemMachine sessions: {e}")
            return []
    
    async def search_all_memories(
        self,
        query: str,
        limit: int = 20,
        use_case_filter: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search across all MemMachine memories (all sessions)
        
        Args:
            query: Search query
            limit: Maximum number of results per session
            use_case_filter: Optional filter by use case type (chatbot, knowledge_base, etc.)
            metadata_filter: Optional metadata filter
            
        Returns:
            List of matching memories with session info
        """
        try:
            # Get all sessions
            all_sessions = await self.get_sessions()
            
            if not all_sessions:
                return []
            
            # Filter sessions by use case if specified
            if use_case_filter:
                filtered_sessions = [
                    s for s in all_sessions
                    if s.startswith(f"{use_case_filter}_")
                ]
            else:
                filtered_sessions = all_sessions
            
            # Search across all filtered sessions
            all_results = []
            client = await self._get_client()
            
            for session_id in filtered_sessions:
                try:
                    # MemMachine search API expects session as object with session_id
                    # But it can also accept just the session_id string
                    # Try both formats
                    search_data = {
                        "session": {"session_id": session_id} if isinstance(session_id, str) else session_id,
                        "query": query,
                        "limit": limit
                    }
                    
                    if metadata_filter:
                        search_data["metadata"] = metadata_filter
                    
                    response = await client.post(
                        f"{self.base_url}/v1/memories/search",
                        json=search_data,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # MemMachine returns results in this structure:
                        # {
                        #   "status": 0,
                        #   "content": {
                        #     "episodic_memory": [[], [episodes], [""]],
                        #     "profile_memory": []
                        #   }
                        # }
                        # Extract episodic memories from the nested arrays
                        content = result.get("content", {})
                        episodic_memories = content.get("episodic_memory", [])
                        
                        # Flatten the episodic_memories array (it's nested)
                        episodes = []
                        for memory_array in episodic_memories:
                            if isinstance(memory_array, list):
                                for episode in memory_array:
                                    # Skip empty strings and non-dict items
                                    if isinstance(episode, dict) and episode.get("uuid"):
                                        episodes.append(episode)
                                    elif isinstance(episode, str) and episode.strip():
                                        # Handle string content
                                        episodes.append({
                                            "uuid": f"ep_{len(episodes)}",
                                            "content": episode,
                                            "content_type": "string"
                                        })
                        
                        # Add session_id and use_case to each result
                        for episode in episodes:
                            # Extract session_id from episode if present, otherwise use search session_id
                            episode_session_id = episode.get("session_id") or session_id
                            episode["session_id"] = episode_session_id
                            
                            # Extract use case type from session_id
                            if "_" in episode_session_id:
                                use_case = episode_session_id.split("_")[0]
                                episode["use_case"] = use_case
                            else:
                                episode["use_case"] = "unknown"
                            
                            all_results.append(episode)
                except Exception as e:
                    logger.warning(f"Error searching session {session_id}: {e}")
                    continue
            
            # Sort by relevance (if available) and limit total results
            # MemMachine typically returns results sorted by relevance
            return all_results[:limit * 2]  # Return more results since we're searching multiple sessions
            
        except Exception as e:
            logger.error(f"Error searching all MemMachine memories: {e}")
            return []
    
    async def delete_memories(self, session_id: str) -> bool:
        """Delete all memories for a session"""
        try:
            client = await self._get_client()
            response = await client.delete(
                f"{self.base_url}/v1/memories",
                json={"session": session_id},
                timeout=10.0
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.warning(f"Error deleting MemMachine memories: {e}")
            return False


# Global service instance
memmachine_service = MemMachineService()

