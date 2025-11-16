import re
import logging
from typing import List, Dict, Any, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

class PreciseAnswerExtractor:
    """Extract precise answers from message content without hardcoded regex"""
    
    def __init__(self):
        # Number word mappings
        self.number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14',
            'fifteen': '15', 'sixteen': '16', 'seventeen': '17', 'eighteen': '18',
            'nineteen': '19', 'twenty': '20'
        }

    def extract_precise_answer(self, question_type: str, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract precise answer based on question type and analysis"""
        
        if not messages:
            return "No relevant information found."
        
        logger.info(f"Extracting precise answer for question type: {question_type}")
        
        # Try different extraction strategies based on question type
        if question_type == "how_many":
            return self._extract_quantity_intelligent(messages, analysis)
        elif question_type == "what" and hasattr(analysis, 'keywords') and any(word in analysis.keywords for word in ['restaurant', 'place', 'venue']):
            return self._extract_restaurant_intelligent(messages, analysis)
        elif question_type == "where":
            return self._extract_location_intelligent(messages, analysis)
        elif question_type == "when":
            return self._extract_time_intelligent(messages, analysis)
        elif question_type == "who":
            return self._extract_person_intelligent(messages, analysis)
        else:
            return self._extract_contextual(messages, analysis)

    def _extract_quantity_intelligent(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract quantity using intelligent text analysis without hardcoded patterns"""
        
        for msg in messages[:3]:  # Check top 3 messages
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            logger.info(f"Analyzing quantity in message: {content[:100]}...")
            
            words = content.split()
            
            # Look for numbers in context
            for i, word in enumerate(words):
                clean_word = ''.join(c for c in word.lower() if c.isalnum())
                
                # Check if word is a number (digit or word)
                if clean_word.isdigit() or clean_word in self.number_words:
                    number = clean_word if clean_word.isdigit() else self.number_words[clean_word]
                    
                    # Look at surrounding words for context
                    context_start = max(0, i - 3)
                    context_end = min(len(words), i + 4)
                    surrounding_context = words[context_start:context_end]
                    
                    # Look for quantity-related words near the number
                    quantity_words = ['people', 'person', 'guest', 'guests', 'ticket', 'tickets', 
                                    'table', 'tables', 'car', 'cars', 'room', 'rooms', 'item', 'items']
                    
                    for j, context_word in enumerate(surrounding_context):
                        clean_context = ''.join(c for c in context_word.lower() if c.isalpha())
                        if clean_context in quantity_words:
                            logger.info(f"Found quantity: {number} {clean_context}")
                            return f"{user_name} mentioned {number} {clean_context}. (From: \"{content[:100]}...\")"
        
        # Fallback
        return f"Based on {messages[0]['user_name']}'s message: \"{messages[0]['message'][:150]}...\""

    def _extract_restaurant_intelligent(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract restaurant names using intelligent analysis"""
        
        for msg in messages[:3]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            logger.info(f"Analyzing restaurant in message: {content[:100]}...")
            
            words = content.split()
            
            # Look for restaurant-related context words
            restaurant_context = ['reservation', 'dinner', 'lunch', 'table', 'book', 'restaurant', 'at']
            
            for i, word in enumerate(words):
                word_lower = word.lower()
                
                # If we find a restaurant context word
                if any(ctx in word_lower for ctx in restaurant_context):
                    # Look for capitalized words nearby (likely restaurant names)
                    search_start = max(0, i - 3)
                    search_end = min(len(words), i + 5)
                    
                    potential_names = []
                    j = search_start
                    
                    while j < search_end:
                        word_at_j = words[j]
                        clean_word = ''.join(c for c in word_at_j if c.isalpha())
                        
                        # Check if it's a capitalized word that could be part of a name
                        if (len(clean_word) > 1 and 
                            clean_word[0].isupper() and 
                            clean_word.lower() not in ['the', 'a', 'an', 'for', 'at', 'in', 'on']):
                            
                            # Check if next words are also capitalized (multi-word name)
                            name_parts = [clean_word]
                            k = j + 1
                            
                            while k < min(len(words), j + 4):  # Look ahead up to 3 words
                                next_word = words[k]
                                next_clean = ''.join(c for c in next_word if c.isalpha())
                                
                                if (len(next_clean) > 1 and 
                                    next_clean[0].isupper() and 
                                    next_clean.lower() not in ['the', 'for', 'tonight', 'today', 'tomorrow']):
                                    name_parts.append(next_clean)
                                    k += 1
                                else:
                                    break
                            
                            full_name = ' '.join(name_parts)
                            if len(full_name) > 2:
                                logger.info(f"Found potential restaurant: {full_name}")
                                return f"{user_name} mentioned \"{full_name}\". (From: \"{content[:100]}...\")"
                            
                            j = k
                        else:
                            j += 1
        
        return f"Based on {messages[0]['user_name']}'s message: \"{messages[0]['message'][:150]}...\""

    def _extract_location_intelligent(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract location using intelligent analysis"""
        
        for msg in messages[:3]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            logger.info(f"Analyzing location in message: {content[:100]}...")
            
            words = content.split()
            
            # Look for location indicator words
            location_indicators = ['to', 'in', 'at', 'from', 'near']
            
            for i, word in enumerate(words):
                word_lower = word.lower().rstrip('.,!?')
                
                # If we find a location indicator
                if word_lower in location_indicators and i + 1 < len(words):
                    next_word = words[i + 1]
                    clean_next = ''.join(c for c in next_word if c.isalpha())
                    
                    # Check if the next word is capitalized (likely a place name)
                    if (len(clean_next) > 2 and 
                        clean_next[0].isupper() and 
                        clean_next.lower() not in ['the', 'this', 'that', 'today', 'tomorrow', 'tonight']):
                        
                        logger.info(f"Found location: {clean_next}")
                        return f"{user_name} mentioned \"{clean_next}\". (From: \"{content[:100]}...\")"
        
        # Also look for well-known city names anywhere in the message
        known_cities = ['paris', 'london', 'milan', 'rome', 'barcelona', 'madrid', 'berlin', 
                       'amsterdam', 'dubai', 'tokyo', 'sydney', 'york', 'angeles', 'francisco']
        
        for msg in messages[:3]:
            content = msg.get('message', '').lower()
            user_name = msg.get('user_name', '')
            
            for city in known_cities:
                if city in content:
                    # Find the actual capitalized version in the original message
                    original_content = msg.get('message', '')
                    words = original_content.split()
                    
                    for word in words:
                        clean_word = ''.join(c for c in word if c.isalpha())
                        if clean_word.lower() == city:
                            logger.info(f"Found known city: {clean_word}")
                            return f"{user_name} mentioned \"{clean_word}\". (From: \"{original_content[:100]}...\")"
        
        return f"Based on {messages[0]['user_name']}'s message: \"{messages[0]['message'][:150]}...\""

    def _extract_time_intelligent(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract time using intelligent analysis without regex"""
        
        for msg in messages[:3]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            logger.info(f"Analyzing time in message: {content[:100]}...")
            
            words = content.lower().split()
            
            # Time-related words
            time_words = {
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                'relative': ['today', 'tomorrow', 'tonight', 'yesterday'],
                'modifiers': ['this', 'next', 'last']
            }
            
            # Look for time expressions
            for i, word in enumerate(words):
                clean_word = ''.join(c for c in word if c.isalpha())
                
                # Check for day names
                if clean_word in time_words['days']:
                    # Check if preceded by modifier
                    if i > 0 and words[i-1] in time_words['modifiers']:
                        time_phrase = f"{words[i-1]} {clean_word}"
                        logger.info(f"Found time phrase: {time_phrase}")
                        return f"{user_name} mentioned \"{time_phrase}\". (From: \"{content[:100]}...\")"
                    else:
                        logger.info(f"Found day: {clean_word}")
                        return f"{user_name} mentioned \"{clean_word}\". (From: \"{content[:100]}...\")"
                
                # Check for relative time words
                elif clean_word in time_words['relative']:
                    logger.info(f"Found relative time: {clean_word}")
                    return f"{user_name} mentioned \"{clean_word}\". (From: \"{content[:100]}...\")"
        
        return f"Based on {messages[0]['user_name']}'s message: \"{messages[0]['message'][:150]}...\""

    def _extract_person_intelligent(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract person information from messages"""
        
        if messages:
            relevant_senders = list(set(msg['user_name'] for msg in messages[:5]))
            
            if len(relevant_senders) == 1:
                return f"{relevant_senders[0]} (based on their message: \"{messages[0]['message'][:100]}...\")"
            else:
                sender_list = ", ".join(relevant_senders)
                return f"Multiple people mentioned: {sender_list}. Most relevant: {messages[0]['user_name']} (message: \"{messages[0]['message'][:100]}...\")"
        
        return "Could not identify specific person from the messages."

    def _extract_contextual(self, messages: List[Dict[str, Any]], analysis: Any) -> str:
        """Extract contextual information for general questions"""
        
        if not messages:
            return "No relevant information found."
        
        best_msg = messages[0]
        return f"Based on {best_msg['user_name']}'s message: \"{best_msg['message']}\""

# Integration function to enhance existing answer extraction
def enhance_answer_extraction(question_type: str, messages: List[Dict[str, Any]], analysis: Any) -> str:
    """Enhanced answer extraction using precise extraction techniques"""
    
    logger.info(f"enhance_answer_extraction called with:")
    logger.info(f"   - Question type: {question_type}")
    logger.info(f"   - Messages count: {len(messages)}")
    if messages:
        logger.info(f"   - First message: {messages[0].get('message', '')[:100]}...")
    
    extractor = PreciseAnswerExtractor()
    result = extractor.extract_precise_answer(question_type, messages, analysis)
    
    logger.info(f"enhance_answer_extraction returning: {result[:100]}...")
    return result