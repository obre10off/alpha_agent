from typing import List, Dict, Any
from llama_index.llms.openai import OpenAI

class ContentFilter:
    """Filter and analyze content for relevance."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the content filter."""
        self.config = config
        self.llm = OpenAI(model="gpt-4o-mini")
        
    async def analyze_relevance(self, content: Dict[str, Any]) -> float:
        """Analyze content relevance using LLM."""
        prompt = f"""
        Analyze the following content for its relevance to AI agents and autonomous systems.
        Consider factors like:
        - Innovation potential
        - Technical feasibility
        - Market opportunity
        - Current trends
        
        Content:
        Title: {content.get('title', '')}
        Text: {content.get('text', '')}
        
        Rate the relevance from 0.0 to 1.0, where:
        0.0 = Not relevant at all
        1.0 = Highly relevant and innovative
        
        Return only the numerical score.
        """
        
        response = await self.llm.acomplete(prompt)
        try:
            score = float(response.text.strip())
            return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1
        except ValueError:
            return 0.0
        
    async def filter_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter content based on relevance threshold."""
        filtered = []
        for content in content_list:
            relevance = await self.analyze_relevance(content)
            if relevance >= self.config["relevance_threshold"]:
                content["relevance_score"] = relevance
                filtered.append(content)
        return filtered[:self.config["max_posts_per_source"]] 