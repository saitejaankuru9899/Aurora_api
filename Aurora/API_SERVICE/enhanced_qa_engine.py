import re
import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from data_service import data_service
from precise_answer_extractor import enhance_answer_extraction
from logger_service import api_logger

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class EnhancedQuestionAnalysis:
    """Enhanced analysis of a user question"""
    question_type: str
    target_entities: List[str]  # People, places, things mentioned
    keywords: List[str]
    intent: str
    confidence: float
    temporal_indicators: List[str]  # Time-related terms
    quantity_indicators: List[str]  # Number-related terms
    location_indicators: List[str]  # Place-related terms

class EnhancedQAEngine:
    """Enhanced question-answering engine with better NLP capabilities"""
    
    def __init__(self):
        # Dynamic question word analysis
        self.question_words = {
            'when': ['when', 'what time', 'schedule', 'date', 'time'],
            'how_many': ['how many', 'how much', 'count', 'number of', 'quantity'],
            'what': ['what', 'which', 'what are', 'what is'],
            'where': ['where', 'location', 'place', 'destination'],
            'who': ['who', 'which person', 'whose'],
            'why': ['why', 'reason', 'because'],
            'how': ['how', 'method', 'way']
        }
        
        # Common English words to exclude from name detection
        self.stop_words = {
            'when', 'what', 'where', 'who', 'why', 'how', 'is', 'are', 'was', 'were',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'about', 'from', 'up', 'out', 'down', 'off', 'over', 'under',
            'many', 'much', 'some', 'any', 'all', 'most', 'few', 'several', 'planning',
            'going', 'visiting', 'traveling', 'trip', 'cars', 'restaurants', 'time',
            'favorite', 'preferred', 'best', 'good', 'great', 'nice', 'today', 'tomorrow',
            'yesterday', 'this', 'that', 'these', 'those', 'here', 'there'
        }

    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Enhanced method to answer questions using dynamic analysis
        """
        start_time = time.time()
        
        try:
            # Step 1: Enhanced question analysis
            logger.info(f"Starting enhanced question analysis for: {question}")
            analysis = await self._enhanced_analyze_question(question)
            
            # Step 2: Smart data retrieval
            logger.info(f"Starting smart data retrieval for entities: {analysis.target_entities}")
            relevant_messages = await self._smart_get_relevant_data(analysis)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Log Q&A processing details
            api_logger.log_qa_processing(
                question=question,
                question_analysis=analysis.__dict__,
                messages_searched=len(relevant_messages),
                relevant_messages=relevant_messages,
                processing_time_ms=processing_time_ms
            )
            
            # Step 3: Dynamic answer extraction
            logger.info(f"Starting dynamic answer extraction")
            answer = await self._dynamic_extract_answer(question, analysis, relevant_messages)
            
            # Step 4: Format enhanced response
            result = {
                "answer": answer,
                "confidence": analysis.confidence,
                "messages_searched": len(relevant_messages),
                "question_type": analysis.question_type,
                "target_entities": analysis.target_entities,
                "debug_info": {
                    "keywords": analysis.keywords,
                    "intent": analysis.intent,
                    "temporal_indicators": analysis.temporal_indicators,
                    "quantity_indicators": analysis.quantity_indicators,
                    "location_indicators": analysis.location_indicators,
                    "processing_time_ms": processing_time_ms
                }
            }
            
            logger.info(f"Question answered successfully in {processing_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Log error
            api_logger.log_error(
                question=question,
                error_message=str(e),
                error_type=type(e).__name__,
                stack_trace=None  # Could add traceback if needed
            )
            
            logger.error(f"Error in answer_question: {e}")
            raise e

    async def _enhanced_analyze_question(self, question: str) -> EnhancedQuestionAnalysis:
        """Enhanced question analysis with better entity extraction"""
        
        question_lower = question.lower().strip()
        
        # Detect question type dynamically
        question_type = "general"
        confidence = 0.5
        
        for q_type, indicators in self.question_words.items():
            for indicator in indicators:
                if indicator in question_lower:
                    question_type = q_type
                    confidence = 0.8
                    logger.info(f"Detected question type: {question_type}")
                    break
            if question_type != "general":
                break
        
        # Extract entities (names, places, etc.) dynamically
        target_entities = self._extract_entities(question)
        logger.info(f"Extracted entities: {target_entities}")
        
        # Extract various types of indicators
        keywords = self._extract_smart_keywords(question_lower)
        temporal_indicators = self._extract_temporal_indicators(question_lower)
        quantity_indicators = self._extract_quantity_indicators(question_lower)
        location_indicators = self._extract_location_indicators(question_lower)
        
        # Determine intent
        intent = self._determine_dynamic_intent(question_type, keywords, target_entities)
        
        return EnhancedQuestionAnalysis(
            question_type=question_type,
            target_entities=target_entities,
            keywords=keywords,
            intent=intent,
            confidence=confidence,
            temporal_indicators=temporal_indicators,
            quantity_indicators=quantity_indicators,
            location_indicators=location_indicators
        )

    def _extract_entities(self, question: str) -> List[str]:
        """Extract potential entity names (people, places, organizations) from question"""
        
        entities = []
        words = question.split()
        
        # Find capitalized sequences that could be names
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalpha())
            
            # Check if it's capitalized and not a common word
            if (len(clean_word) > 2 and 
                clean_word[0].isupper() and 
                clean_word.lower() not in self.stop_words and
                not clean_word.isdigit()):
                
                # Check for multi-word entities
                entity_parts = [clean_word]
                
                # Look ahead for more capitalized words
                for j in range(i + 1, min(len(words), i + 3)):  # Look ahead up to 2 words
                    next_word = words[j]
                    next_clean = ''.join(c for c in next_word if c.isalpha())
                    
                    if (len(next_clean) > 1 and 
                        next_clean[0].isupper() and 
                        next_clean.lower() not in self.stop_words):
                        entity_parts.append(next_clean)
                    else:
                        break
                
                entity = ' '.join(entity_parts)
                if entity not in entities:
                    entities.append(entity)
        
        return entities

    def _extract_smart_keywords(self, question_lower: str) -> List[str]:
        """Extract meaningful keywords, excluding stop words"""
        
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', question_lower)
        
        keywords = []
        for word in words:
            if (len(word) > 2 and 
                word not in self.stop_words and 
                not word.isdigit()):
                keywords.append(word)
        
        return keywords[:15]  # Limit to top 15 keywords

    def _extract_temporal_indicators(self, question_lower: str) -> List[str]:
        """Extract time-related terms from the question"""
        
        temporal_words = [
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december',
            'today', 'tomorrow', 'yesterday', 'tonight', 'morning', 'afternoon', 'evening', 'night',
            'this', 'next', 'last', 'now', 'soon', 'later'
        ]
        
        words = question_lower.split()
        temporal_indicators = []
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in temporal_words:
                temporal_indicators.append(clean_word)
        
        return temporal_indicators

    def _extract_quantity_indicators(self, question_lower: str) -> List[str]:
        """Extract quantity-related terms"""
        
        quantity_words = [
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'eleven', 'twelve', 'few', 'several', 'many', 'multiple', 'couple', 'pair', 'dozen'
        ]
        
        words = question_lower.split()
        quantity_indicators = []
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word in quantity_words or clean_word.isdigit():
                quantity_indicators.append(clean_word)
        
        return quantity_indicators

    def _extract_location_indicators(self, question_lower: str) -> List[str]:
        """Extract location-related terms"""
        
        location_words = [
            'paris', 'london', 'milan', 'rome', 'barcelona', 'madrid', 'berlin', 'amsterdam',
            'dubai', 'tokyo', 'sydney', 'york', 'angeles', 'francisco',
            'restaurant', 'hotel', 'theater', 'theatre', 'opera', 'airport', 'station',
            'mall', 'park', 'museum', 'cafe', 'bar', 'city', 'country', 'state'
        ]
        
        words = question_lower.split()
        location_indicators = []
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in location_words:
                location_indicators.append(clean_word)
        
        return location_indicators

    def _determine_dynamic_intent(self, question_type: str, keywords: List[str], entities: List[str]) -> str:
        """Dynamically determine intent based on analysis"""
        
        intent_mapping = {
            "when": "temporal_information",
            "how_many": "quantity_information",
            "what": "descriptive_information",
            "where": "location_information",
            "who": "identity_information",
            "why": "explanatory_information",
            "how": "procedural_information"
        }
        
        base_intent = intent_mapping.get(question_type, "general_information")
        
        # Refine intent based on keywords
        if any(word in keywords for word in ['favorite', 'prefer', 'like', 'love']):
            return f"{base_intent}_preferences"
        elif any(word in keywords for word in ['book', 'reserve', 'schedule']):
            return f"{base_intent}_booking"
        
        return base_intent

    async def _smart_get_relevant_data(self, analysis: EnhancedQuestionAnalysis) -> List[Dict[str, Any]]:
        """Smart data retrieval using enhanced search capabilities"""
        
        try:
            all_relevant_messages = []
            
            # Search for each entity mentioned in the question
            for entity in analysis.target_entities:
                logger.info(f"Searching for entity: {entity}")
                entity_messages = await data_service.search_all_messages(entity, max_results=20)
                
                # Add entity info to each message for tracking
                for msg in entity_messages:
                    msg['matched_entity'] = entity
                    msg['entity_match_score'] = self._calculate_entity_match_score(msg, entity)
                
                all_relevant_messages.extend(entity_messages)
            
            # If no entities found, search by keywords
            if not all_relevant_messages and analysis.keywords:
                logger.info("No entity matches found, searching by keywords...")
                for keyword in analysis.keywords[:3]:  # Top 3 keywords
                    keyword_messages = await data_service.search_all_messages(keyword, max_results=15)
                    
                    for msg in keyword_messages:
                        msg['matched_keyword'] = keyword
                        msg['keyword_match_score'] = self._calculate_keyword_match_score(msg, keyword)
                    
                    all_relevant_messages.extend(keyword_messages)
            
            # Remove duplicates based on message ID
            unique_messages = {}
            for msg in all_relevant_messages:
                msg_id = msg.get('id')
                if msg_id not in unique_messages:
                    unique_messages[msg_id] = msg
                elif msg.get('entity_match_score', 0) > unique_messages[msg_id].get('entity_match_score', 0):
                    unique_messages[msg_id] = msg
            
            # Convert back to list and sort by relevance
            final_messages = list(unique_messages.values())
            final_messages.sort(key=lambda x: max(
                x.get('entity_match_score', 0), 
                x.get('keyword_match_score', 0)
            ), reverse=True)
            
            logger.info(f"Found {len(final_messages)} unique relevant messages")
            return final_messages[:25]  # Top 25 most relevant
            
        except Exception as e:
            logger.error(f"Error in smart data retrieval: {e}")
            return []

    def _calculate_entity_match_score(self, message: Dict[str, Any], entity: str) -> float:
        """Calculate how well a message matches an entity"""
        
        score = 0.0
        entity_lower = entity.lower()
        
        user_name = message.get('user_name', '').lower()
        message_content = message.get('message', '').lower()
        
        # Exact name match in user_name gets highest score
        if entity_lower == user_name:
            score += 2.0
        elif entity_lower in user_name:
            score += 1.5
        
        # Partial name matches
        entity_parts = entity_lower.split()
        for part in entity_parts:
            if part in user_name:
                score += 0.8
            if part in message_content:
                score += 0.3
        
        return score

    def _calculate_keyword_match_score(self, message: Dict[str, Any], keyword: str) -> float:
        """Calculate how well a message matches a keyword"""
        
        score = 0.0
        keyword_lower = keyword.lower()
        
        message_content = message.get('message', '').lower()
        
        # Count occurrences
        occurrences = message_content.count(keyword_lower)
        score += occurrences * 0.5
        
        # Bonus for exact word match vs. substring
        if f" {keyword_lower} " in f" {message_content} ":
            score += 0.3
        
        return score

    async def _dynamic_extract_answer(self, question: str, analysis: EnhancedQuestionAnalysis, messages: List[Dict[str, Any]]) -> str:
        """Dynamically extract answers using precise extraction techniques"""
        
        if not messages:
            entity_list = ", ".join(analysis.target_entities) if analysis.target_entities else "this topic"
            return f"I couldn't find any information about {entity_list} in the member messages database."
        
        # Use precise answer extraction
        try:
            logger.info(f"Attempting precise extraction for question type: {analysis.question_type}")
            if messages:
                logger.info(f"Top message content: {messages[0].get('message', '')[:100]}...")
            
            precise_answer = enhance_answer_extraction(analysis.question_type, messages, analysis)
            
            logger.info(f"Precise extraction result: {precise_answer[:100]}...")
            return precise_answer
            
        except Exception as e:
            logger.error(f"Error in precise extraction: {e}")
            # Fallback to contextual answer
            return self._generate_contextual_answer(messages, analysis)

    def _generate_contextual_answer(self, messages: List[Dict[str, Any]], analysis: EnhancedQuestionAnalysis) -> str:
        """Generate contextual answers for general questions"""
        
        best_msg = messages[0]
        entity = analysis.target_entities[0] if analysis.target_entities else "the relevant person"
        
        return f"Based on {best_msg['user_name']}'s message: \"{best_msg['message']}\""

# Create enhanced engine instance
enhanced_qa_engine = EnhancedQAEngine()