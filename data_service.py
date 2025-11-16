import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Setup logging for data service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataService:
    """Enhanced service to fetch and manage member data from Aurora API"""
    
    def __init__(self):
        self.api_url = "https://november7-730026606190.europe-west1.run.app/messages"
        self.data_cache = None
        self.last_fetch = None
        self.cache_duration = 300  # 5 minutes cache
        self._complete_data_cached = False
    
    async def fetch_member_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch member data from Aurora API (first 100 messages for quick access)
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            List of member messages (up to 100)
        """
        
        # Check if we need to refresh cache
        if not force_refresh and self._is_cache_valid() and not self._complete_data_cached:
            logger.info("Using cached partial data")
            return self.data_cache or []
        
        logger.info("Fetching partial dataset from Aurora API...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                
                data = response.json()
                
                # Handle the API response format: {"total": N, "items": [...]}
                if isinstance(data, dict) and "items" in data:
                    messages = data["items"]
                    total = data.get("total", len(messages))
                    logger.info(f"API returned {total} total messages, fetched {len(messages)} items")
                elif isinstance(data, list):
                    messages = data
                    logger.info(f"API returned {len(messages)} messages directly")
                else:
                    logger.warning(f"Unexpected API response format: {type(data)}")
                    messages = []
                
                # Cache the processed data
                if not self._complete_data_cached:  # Only cache if we don't have complete data
                    self.data_cache = messages
                    self.last_fetch = datetime.now()
                
                logger.info(f"Successfully fetched {len(messages)} messages")
                return messages
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to fetch data: HTTP {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Request timed out")
            raise Exception("API request timed out")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Failed to fetch data: {str(e)}")
    
    async def fetch_all_member_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch ALL member data from Aurora API (handles pagination)
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Complete list of all member messages
        """
        
        # Check if we have a complete dataset cached
        if not force_refresh and self._is_cache_valid() and self._complete_data_cached:
            logger.info("Using complete cached dataset")
            return self.data_cache or []
        
        logger.info("Fetching complete dataset from Aurora API...")
        all_messages = []
        page_size = 100
        offset = 0
        max_retries = 3
        
        try:
            async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                while True:
                    # Try different pagination approaches with retries
                    url = f"{self.api_url}?limit={page_size}&offset={offset}"
                    
                    for retry in range(max_retries):
                        try:
                            response = await client.get(url)
                            response.raise_for_status()
                            break
                        except httpx.HTTPStatusError as e:
                            if e.response.status_code in [401, 402, 403, 429]:
                                logger.warning(f"API limit reached or auth error: {e.response.status_code}. Retrieved {len(all_messages)} messages so far.")
                                if all_messages:  # Return what we have
                                    break
                                else:
                                    raise Exception(f"API access denied: HTTP {e.response.status_code}")
                            elif retry < max_retries - 1:
                                logger.warning(f"Retry {retry + 1} for offset {offset}")
                                continue
                            else:
                                raise
                    else:
                        # If we broke out of retry loop due to auth errors
                        break
                    
                    data = response.json()
                    
                    # Handle the API response format: {"total": N, "items": [...]}
                    if isinstance(data, dict) and "items" in data:
                        messages = data["items"]
                        total = data.get("total", len(messages))
                        
                        logger.info(f"Fetched page {offset//page_size + 1}: {len(messages)} messages (Total available: {total})")
                        
                        if not messages:  # No more data
                            break
                            
                        all_messages.extend(messages)
                        
                        # If we got less than page_size, we've reached the end
                        if len(messages) < page_size:
                            break
                            
                        offset += page_size
                        
                        # Safety check to prevent infinite loops
                        if len(all_messages) >= total or offset > total:
                            break
                            
                    else:
                        logger.error(f"Unexpected API response format: {type(data)}")
                        break
                
                # Cache the complete dataset
                self.data_cache = all_messages
                self.last_fetch = datetime.now()
                self._complete_data_cached = True
                
                logger.info(f"Successfully fetched complete dataset: {len(all_messages)} messages")
                return all_messages
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Fall back to partial data if available
            if all_messages:
                logger.info(f"Returning partial dataset: {len(all_messages)} messages")
                return all_messages
            raise Exception(f"Failed to fetch data: HTTP {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if all_messages:
                logger.info(f"Returning partial dataset: {len(all_messages)} messages")
                return all_messages
            raise Exception(f"Failed to fetch data: {str(e)}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self.data_cache is None or self.last_fetch is None:
            return False
        
        elapsed = (datetime.now() - self.last_fetch).total_seconds()
        return elapsed < self.cache_duration
    
    async def search_all_messages(self, search_term: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search through ALL available messages for a term
        
        Args:
            search_term: Term to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching messages
        """
        try:
            all_messages = await self.fetch_all_member_data()
            
            matching_messages = []
            search_term_lower = search_term.lower()
            
            for message in all_messages:
                user_name = message.get('user_name', '').lower()
                message_content = message.get('message', '').lower()
                
                # Check if search term appears in user name or message content
                if (search_term_lower in user_name or 
                    search_term_lower in message_content):
                    matching_messages.append(message)
                    
                    if len(matching_messages) >= max_results:
                        break
            
            logger.info(f"Found {len(matching_messages)} messages matching '{search_term}'")
            return matching_messages
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    async def analyze_data_structure(self) -> Dict[str, Any]:
        """
        Analyze the data structure for better understanding
        """
        try:
            data = await self.fetch_member_data()
            
            if not data:
                return {"error": "No data available"}
            
            unique_senders = set(msg.get('user_name', 'unknown') for msg in data)
            timestamps = [msg.get('timestamp') for msg in data if msg.get('timestamp')]
            
            analysis = {
                "total_messages": len(data),
                "sample_message": data[0] if data else None,
                "message_fields": list(data[0].keys()) if data else [],
                "unique_senders": len(unique_senders),
                "sender_list": list(unique_senders),
                "date_range": {
                    "earliest": min(timestamps) if timestamps else None,
                    "latest": max(timestamps) if timestamps else None,
                    "total_dates": len(timestamps)
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data structure: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

# Create a global instance
data_service = DataService()