import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from data_service import data_service

@dataclass
class QuestionAnalysis:
    """Structured analysis of a user question"""
    question_type: str  # "when", "how_many", "what", "who", "where", "general"
    target_person: Optional[str]  # Person mentioned in question
    keywords: List[str]  # Important keywords extracted
    intent: str  # What the user is looking for
    confidence: float  # How confident we are in the analysis

class QuestionAnsweringEngine:
    """Advanced question-answering engine for Aurora member data"""
    
    def __init__(self):
        self.question_patterns = {
            "when": [
                r"when\s+(?:is|was|will|does|did)\s+(\w+).*?(planning|going|visiting|traveling|trip)",
                r"when\s+.*?(\w+).*?(plan|scheduled|booked|reserved)",
                r"what\s+time.*?(\w+)",
                r"(\w+).*?when"
            ],
            "how_many": [
                r"how\s+many\s+(\w+).*?(?:does|has|owns?)\s+(\w+)",
                r"(\w+).*?how\s+many\s+(\w+)",
                r"count.*?(\w+).*?(\w+)"
            ],
            "what": [
                r"what\s+(?:are|is)\s+(\w+)(?:'?s)?\s+(favorite|preferred|liked)\s+(\w+)",
                r"(\w+)(?:'?s)?\s+(favorite|preferred|best)\s+(\w+)",
                r"what.*?(\w+).*?(like|enjoy|prefer)"
            ],
            "where": [
                r"where\s+(?:is|was|will|does|did)\s+(\w+)",
                r"(\w+).*?where",
                r"location.*?(\w+)"
            ]
        }
        
        # Common objects/concepts people ask about
        self.entity_types = {
            "transportation": ["car", "cars", "vehicle", "jet", "plane", "flight", "uber", "taxi"],
            "dining": ["restaurant", "restaurants", "dinner", "lunch", "reservation", "table"],
            "travel": ["trip", "travel", "vacation", "visit", "flight", "hotel", "booking"],
            "entertainment": ["opera", "concert", "theater", "show", "tickets", "event"],
            "shopping": ["buy", "purchase", "order", "booking", "reserve"],
            "time": ["when", "time", "date", "schedule", "calendar", "today", "tomorrow", "friday", "saturday"]
        }

    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to answer a question based on member data
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with answer and metadata
        """
        
        # Step 1: Analyze the question
        analysis = self._analyze_question(question)
        
        # Step 2: Get relevant data
        relevant_messages = await self._get_relevant_messages(analysis)
        
        # Step 3: Extract answer from messages
        answer = self._extract_answer(question, analysis, relevant_messages)
        
        # Step 4: Format response
        return {
            "answer": answer,
            "confidence": analysis.confidence,
            "messages_searched": len(relevant_messages),
            "question_type": analysis.question_type,
            "target_person": analysis.target_person,
            "debug_info": {
                "keywords": analysis.keywords,
                "intent": analysis.intent,
                "relevant_messages_count": len(relevant_messages)
            }
        }

    def _analyze_question(self, question: str) -> QuestionAnalysis:
        """Analyze the structure and intent of the question"""
        
        question_lower = question.lower().strip()
        
        # Extract question type
        question_type = "general"
        confidence = 0.5
        keywords = []
        target_person = None
        intent = "information_request"
        
        # Identify question type using patterns
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, question_lower, re.IGNORECASE)
                if match:
                    question_type = q_type
                    confidence = 0.8
                    
                    # Extract potential person name from match groups
                    for group in match.groups():
                        if group and len(group) > 2 and group.isalpha():
                            # Check if it's likely a person's name (capitalized, not a common word)
                            if not self._is_common_word(group):
                                target_person = group.title()
                    break
            if question_type != "general":
                break
        
        # Extract keywords
        keywords = self._extract_keywords(question_lower)
        
        # Refine person detection
        if not target_person:
            target_person = self._extract_person_name(question)
        
        # Determine intent based on question type and keywords
        intent = self._determine_intent(question_type, keywords)
        
        return QuestionAnalysis(
            question_type=question_type,
            target_person=target_person,
            keywords=keywords,
            intent=intent,
            confidence=confidence
        )

    def _extract_person_name(self, question: str) -> Optional[str]:
        """Extract person names from the question using various heuristics"""
        
        # Look for capitalized words that could be names
        words = question.split()
        potential_names = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Check if it's capitalized and not a common word
            if (clean_word and clean_word[0].isupper() and 
                len(clean_word) > 2 and 
                not self._is_common_word(clean_word.lower())):
                potential_names.append(clean_word)
        
        # Handle compound names (like "Vikram Desai")
        if len(potential_names) >= 2:
            # Check if consecutive names
            question_words = question.split()
            for i in range(len(question_words) - 1):
                word1 = re.sub(r'[^\w]', '', question_words[i])
                word2 = re.sub(r'[^\w]', '', question_words[i + 1])
                
                if (word1 in potential_names and word2 in potential_names and
                    word1[0].isupper() and word2[0].isupper()):
                    return f"{word1} {word2}"
        
        # Return single name if found
        return potential_names[0] if potential_names else None

    def _is_common_word(self, word: str) -> bool:
        """Check if a word is a common English word (not a name)"""
        common_words = {
            "when", "what", "where", "who", "how", "why", "is", "are", "was", "were",
            "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "many", "much", "some", "any", "all", "most", "few", "several",
            "favorite", "preferred", "best", "good", "great", "nice", "planning",
            "going", "visiting", "traveling", "trip", "cars", "restaurants", "time"
        }
        return word.lower() in common_words

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract important keywords from the question"""
        
        # Remove common stop words
        stop_words = {
            "the", "is", "are", "was", "were", "a", "an", "and", "or", "but",
            "in", "on", "at", "to", "for", "of", "with", "by", "about"
        }
        
        # Extract meaningful words
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Limit to top 10 keywords

    def _determine_intent(self, question_type: str, keywords: List[str]) -> str:
        """Determine the user's intent based on question analysis"""
        
        intent_mapping = {
            "when": "time_information",
            "how_many": "quantity_information", 
            "what": "preference_information",
            "where": "location_information"
        }
        
        return intent_mapping.get(question_type, "general_information")

    async def _get_relevant_messages(self, analysis: QuestionAnalysis) -> List[Dict[str, Any]]:
        """Get messages relevant to the question"""
        
        try:
            # Get all available messages
            all_messages = await data_service.fetch_member_data()
            
            relevant_messages = []
            
            for message in all_messages:
                relevance_score = self._calculate_message_relevance(message, analysis)
                if relevance_score > 0.3:  # Threshold for relevance
                    message_with_score = message.copy()
                    message_with_score['relevance_score'] = relevance_score
                    relevant_messages.append(message_with_score)
            
            # Sort by relevance score
            relevant_messages.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            # Return top 20 most relevant messages
            return relevant_messages[:20]
            
        except Exception as e:
            print(f"Error getting relevant messages: {e}")
            return []

    def _calculate_message_relevance(self, message: Dict[str, Any], analysis: QuestionAnalysis) -> float:
        """Calculate how relevant a message is to the question"""
        
        relevance_score = 0.0
        
        user_name = message.get('user_name', '').lower()
        message_content = message.get('message', '').lower()
        
        # Check if target person matches
        if analysis.target_person:
            target_lower = analysis.target_person.lower()
            if target_lower in user_name:
                relevance_score += 1.0
            # Handle partial name matches (e.g., "Vikram" matches "Vikram Desai")
            name_parts = target_lower.split()
            for part in name_parts:
                if part in user_name:
                    relevance_score += 0.5
        
        # Check keyword matches in message content
        keyword_matches = 0
        for keyword in analysis.keywords:
            if keyword in message_content:
                keyword_matches += 1
                relevance_score += 0.3
        
        # Boost score for entity type matches
        for entity_type, entities in self.entity_types.items():
            for entity in entities:
                if entity in message_content:
                    relevance_score += 0.2
        
        return min(relevance_score, 3.0)  # Cap at 3.0

    def _extract_answer(self, question: str, analysis: QuestionAnalysis, messages: List[Dict[str, Any]]) -> str:
        """Extract the answer from relevant messages"""
        
        if not messages:
            return f"I couldn't find any information about {analysis.target_person or 'this topic'} in the member messages."
        
        # Different extraction strategies based on question type
        if analysis.question_type == "when":
            return self._extract_time_answer(messages, analysis)
        elif analysis.question_type == "how_many":
            return self._extract_quantity_answer(messages, analysis)
        elif analysis.question_type == "what":
            return self._extract_preference_answer(messages, analysis)
        elif analysis.question_type == "where":
            return self._extract_location_answer(messages, analysis)
        else:
            return self._extract_general_answer(messages, analysis)

    def _extract_time_answer(self, messages: List[Dict[str, Any]], analysis: QuestionAnalysis) -> str:
        """Extract time-related information from messages"""
        
        # Look for time patterns in messages
        time_patterns = [
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'(\d{1,2}[:/]\d{1,2})',
            r'(\d{1,2}\s*(?:am|pm))',
            r'(this\s+\w+|next\s+\w+|tomorrow|today)',
            r'(\d{1,2}(?:st|nd|rd|th)?)',
        ]
        
        time_mentions = []
        for msg in messages[:5]:  # Check top 5 most relevant
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            for pattern in time_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    time_mentions.append({
                        'time': match,
                        'user': user_name,
                        'context': content,
                        'relevance': msg.get('relevance_score', 0)
                    })
        
        if time_mentions:
            # Return the most relevant time mention
            best_mention = max(time_mentions, key=lambda x: x['relevance'])
            return f"Based on the messages, {best_mention['user']} mentioned: {best_mention['time']}. Context: \"{best_mention['context'][:100]}...\""
        
        return f"I found messages from {analysis.target_person or 'relevant users'} but couldn't find specific timing information."

    def _extract_quantity_answer(self, messages: List[Dict[str, Any]], analysis: QuestionAnalysis) -> str:
        """Extract quantity information from messages"""
        
        # Look for numbers in messages
        number_patterns = [
            r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b',
            r'\b(\d+)\s*(?:cars?|vehicles?|tickets?|reservations?|people?)\b'
        ]
        
        quantities = []
        for msg in messages[:5]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            for pattern in number_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    quantities.append({
                        'quantity': match,
                        'user': user_name,
                        'context': content,
                        'relevance': msg.get('relevance_score', 0)
                    })
        
        if quantities:
            best_quantity = max(quantities, key=lambda x: x['relevance'])
            return f"Based on {best_quantity['user']}'s messages: {best_quantity['quantity']}. Context: \"{best_quantity['context'][:100]}...\""
        
        return f"I found messages from {analysis.target_person or 'relevant users'} but couldn't find specific quantity information."

    def _extract_preference_answer(self, messages: List[Dict[str, Any]], analysis: QuestionAnalysis) -> str:
        """Extract preference/favorite information from messages"""
        
        preferences = []
        for msg in messages[:5]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            # Look for restaurants, places, activities mentioned
            if any(word in content.lower() for word in ['restaurant', 'dinner', 'lunch', 'favorite', 'love', 'like']):
                preferences.append({
                    'user': user_name,
                    'content': content,
                    'relevance': msg.get('relevance_score', 0)
                })
        
        if preferences:
            best_pref = max(preferences, key=lambda x: x['relevance'])
            return f"Based on {best_pref['user']}'s messages: \"{best_pref['content']}\""
        
        return f"I found messages from {analysis.target_person or 'relevant users'} but couldn't find specific preference information."

    def _extract_location_answer(self, messages: List[Dict[str, Any]], analysis: QuestionAnalysis) -> str:
        """Extract location information from messages"""
        
        # Look for location patterns
        location_patterns = [
            r'\b(paris|london|milan|new york|tokyo|rome|barcelona|madrid|berlin|amsterdam)\b',
            r'\b(restaurant|hotel|theater|opera|airport|station)\b',
            r'\bto\s+(\w+)\b',
            r'\bin\s+(\w+)\b'
        ]
        
        locations = []
        for msg in messages[:5]:
            content = msg.get('message', '')
            user_name = msg.get('user_name', '')
            
            for pattern in location_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    locations.append({
                        'location': match,
                        'user': user_name,
                        'context': content,
                        'relevance': msg.get('relevance_score', 0)
                    })
        
        if locations:
            best_location = max(locations, key=lambda x: x['relevance'])
            return f"Based on {best_location['user']}'s messages, the location mentioned is: {best_location['location']}. Context: \"{best_location['context'][:100]}...\""
        
        return f"I found messages from {analysis.target_person or 'relevant users'} but couldn't find specific location information."

    def _extract_general_answer(self, messages: List[Dict[str, Any]], analysis: QuestionAnalysis) -> str:
        """Extract general information from messages"""
        
        # Return the most relevant message content
        if messages:
            best_msg = messages[0]  # Already sorted by relevance
            return f"Based on {best_msg['user_name']}'s messages: \"{best_msg['message']}\""
        
        return "I couldn't find relevant information in the member messages."

# Create global engine instance
qa_engine = QuestionAnsweringEngine()

# Test function
async def test_qa_engine():
    """Test the question-answering engine with sample questions"""
    
    test_questions = [
        "When is Sophia planning her trip to Paris?",
        "How many tickets does Armand need for the opera?", 
        "What is Fatima's favorite restaurant?",
        "Where is Sophia going this Friday?",
        "Tell me about private jet bookings"
    ]
    
    print("🧠 Testing Question-Answering Engine")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n❓ Question {i}: {question}")
        print("-" * 40)
        
        try:
            result = await qa_engine.answer_question(question)
            
            print(f"💡 Answer: {result['answer']}")
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"🔍 Messages Searched: {result['messages_searched']}")
            print(f"🎯 Question Type: {result['question_type']}")
            print(f"👤 Target Person: {result['target_person'] or 'None detected'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_qa_engine())