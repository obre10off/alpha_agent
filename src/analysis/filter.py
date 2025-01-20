from typing import List, Dict, Any
from datetime import datetime, timezone
from llama_index.llms.openai import OpenAI

class ContentFilter:
    """Filter and analyze content for relevance."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the content filter."""
        self.config = config
        self.llm = OpenAI(model="gpt-4-turbo-preview")  # Using a more capable model
        
    async def analyze_relevance(self, content: Dict[str, Any]) -> float:
        """Analyze content relevance using LLM with structured criteria."""
        # First apply basic filtering
        if not self._meets_basic_criteria(content):
            return 0.0
            
        prompt = """
        Analyze the following content's relevance to AI technology and development.
        
        Content to analyze:
        Title: {title}
        Description: {text}
        Date: {date}
        
        Evaluate based on these specific criteria:
        1. Technical Innovation (0-10):
           - Novel AI approaches or technologies
           - Technical implementation details
           - Research or development insights
        
        2. Practical Application (0-10):
           - Real-world use cases
           - Implementation examples
           - Business or industry impact
        
        3. Timeliness (0-10):
           - Current relevance
           - Future potential
           - Trend alignment
        
        4. Quality & Credibility (0-10):
           - Information depth
           - Source reliability
           - Technical accuracy
        
        Return only a JSON object with scores and final_score:
        {{
            "technical_score": X,
            "practical_score": X,
            "timeliness_score": X,
            "quality_score": X,
            "final_score": X.X  // Normalized to 0-1 scale
        }}
        """
        
        formatted_prompt = prompt.format(
            title=content.get('title', ''),
            text=self._get_cleaned_content(content),
            date=self._format_date(content.get('created_utc', None))
        )
        
        try:
            response = await self.llm.acomplete(formatted_prompt)
            scores = eval(response.text.strip())  # Parse JSON response
            return scores['final_score']
        except Exception as e:
            print(f"Error analyzing content: {e}")
            return 0.0
            
    def _meets_basic_criteria(self, content: Dict[str, Any]) -> bool:
        """Apply basic filtering criteria before LLM analysis."""
        # Skip if content is too old (e.g., older than 30 days)
        if content.get('created_utc'):
            age_days = (datetime.now(timezone.utc).timestamp() - content['created_utc']) / 86400
            if age_days > self.config.get('max_age_days', 30):
                return False
        
        # Skip if engagement is too low
        min_score = self.config.get('min_score', 5)
        if content.get('score', 0) < min_score:
            return False
            
        # Skip if content is too short
        min_length = self.config.get('min_content_length', 100)
        if len(self._get_cleaned_content(content)) < min_length:
            return False
            
        return True
        
    def _get_cleaned_content(self, content: Dict[str, Any]) -> str:
        """Extract and clean the main content."""
        # For Reddit
        if 'selftext' in content:
            text = content.get('selftext', '')
        # For HackerNews
        elif 'text' in content:
            text = content.get('text', '')
        else:
            text = content.get('description', '')
            
        # Clean and truncate if needed
        text = text.strip()
        max_length = 1000  # Prevent too long content
        return text[:max_length] if len(text) > max_length else text
        
    def _format_date(self, timestamp: float) -> str:
        """Format Unix timestamp to readable date."""
        if not timestamp:
            return "No date"
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d')
        
    async def filter_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter content based on relevance threshold and return structured results."""
        filtered = []
        
        for content in content_list:
            if not self._meets_basic_criteria(content):
                continue
                
            relevance = await self.analyze_relevance(content)
            if relevance >= self.config["relevance_threshold"]:
                filtered_content = {
                    "title": content.get('title', ''),
                    "url": content.get('url', ''),
                    "source": content.get('source', 'unknown'),
                    "date": self._format_date(content.get('created_utc')),
                    "relevance_score": relevance,
                    "summary": self._get_cleaned_content(content)[:200] + "..."  # Short preview
                }
                filtered.append(filtered_content)
                
        # Sort by relevance score and limit results
        filtered.sort(key=lambda x: x['relevance_score'], reverse=True)
        return filtered[:self.config["max_posts_per_source"]] 