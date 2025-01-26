from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from llama_index.llms.openai import OpenAI
import logging

class ContentFilter:
    """Filter and score content for relevance."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        self.keywords = [
            "ai agent", "autonomous ai", "llm agent", "ai assistant",
            "autonomous agent", "ai system", "agent architecture",
            "multi-agent", "agent framework"
        ]
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.llm = OpenAI(model="gpt-4o-mini")
        
    async def filter_content(self, posts: List[Dict[str, Any]], source: str = "") -> List[Dict[str, Any]]:
        """Filter posts based on relevance and freshness."""
        if not posts:
            return []
            
        filtered = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.get("max_age_days", 30))
        
        for post in posts:
            self.logger.debug(f"Processing post: {post.get('title', 'No title')}")
            
            # Basic criteria check
            if not self._meets_basic_criteria(post, cutoff_date):
                self.logger.debug("Failed basic criteria")
                continue
                
            # Calculate relevance
            relevance_score = self._calculate_relevance(post)
            self.logger.debug(f"Relevance score: {relevance_score}")
            
            # If post meets threshold, add it
            if relevance_score >= self.config.get("min_relevance_score", 0.3):  # Lowered threshold
                post["relevance_score"] = relevance_score
                filtered.append(post)
                self.logger.debug("Post added to filtered list")
            
        self.logger.debug(f"Total posts filtered: {len(filtered)}")
        return filtered[:self.config.get("max_posts_per_source", 3)]
        
    def _meets_basic_criteria(self, post: Dict[str, Any], cutoff_date: datetime) -> bool:
        """Check if post meets basic filtering criteria."""
        try:
            # Check creation date
            created_utc = post.get("created_utc")
            if created_utc:
                created_at = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                self.logger.debug(f"Post date: {created_at}, Cutoff date: {cutoff_date}")
                if created_at < cutoff_date:
                    self.logger.debug("Post too old")
                    return False
            
            # Check score/points
            score = post.get("score", post.get("points", 0))
            self.logger.debug(f"Post score: {score}")
            if score < self.config.get("min_points", 10):  # Lowered threshold
                self.logger.debug("Score too low")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in basic criteria check: {e}")
            return False
            
    def _calculate_relevance(self, post: Dict[str, Any]) -> float:
        """Calculate relevance score for a post."""
        score = 0.0
        content = f"{post.get('title', '')} {post.get('text', '')}".lower()
        
        # Keyword matching
        keyword_matches = 0
        for keyword in self.keywords:
            if keyword in content:
                keyword_matches += 1
                self.logger.debug(f"Matched keyword: {keyword}")
        
        # Calculate scores
        keyword_score = min(keyword_matches * 0.2, 0.6)
        title_score = 0.3 if any(kw in post.get('title', '').lower() for kw in self.keywords) else 0
        
        # Combine scores
        score = keyword_score + title_score
        
        self.logger.debug(f"Final relevance score: {score}")
        return min(score, 1.0)
        
    async def analyze_relevance(self, content: Dict[str, Any]) -> float:
        """Analyze content relevance using LLM with structured criteria."""
        # First apply basic filtering
        if not self._meets_basic_criteria(content, datetime.now(timezone.utc)):
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