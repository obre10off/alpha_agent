from typing import List, Dict, Any
from .base import BaseCollector
from composio_llamaindex import ComposioToolSet, Action
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker

class HackerNewsCollector(BaseCollector):
    """Collector for HackerNews content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the HackerNews collector."""
        super().__init__(config)
        self.llm = OpenAI(model="gpt-4o-mini")
        self.toolset = ComposioToolSet()
        self.tools = self.toolset.get_tools(actions=['HACKERNEWS_SEARCH_POSTS'])
        
        # Set up agent
        prefix_messages = [
            ChatMessage(
                role="system",
                content="You are a HackerNews content collector. Your task is to search for relevant posts."
            )
        ]
        
        self.agent = FunctionCallingAgentWorker(
            tools=self.tools,
            llm=self.llm,
            prefix_messages=prefix_messages,
            max_function_calls=10,
            allow_parallel_tool_calls=False,
            verbose=True
        ).as_agent()
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect posts from HackerNews."""
        posts = []
        for keyword in self.config["keywords"]:
            try:
                prompt = f"Search HackerNews for posts about '{keyword}'"
                response = await self.agent.achat(prompt)
                
                # Process the response
                if hasattr(response, 'response') and isinstance(response.response, dict):
                    results = [response.response]
                elif hasattr(response, 'response') and isinstance(response.response, list):
                    results = response.response
                else:
                    results = []
                
                for post in results:
                    # Add platform identifier and standardize fields
                    post["platform"] = "HackerNews"
                    post["text"] = post.get("text", "")
                    post["title"] = post.get("title", "")
                    post["url"] = post.get("url", "")
                    posts.append(post)
            except Exception as e:
                print(f"Error searching HackerNews for '{keyword}': {str(e)}")
                continue
        return posts
    
    async def filter_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter HackerNews posts based on points and relevance."""
        filtered = []
        for post in content:
            try:
                points = int(post.get("points", 0))
                if points >= self.config["min_points"]:
                    filtered.append(post)
            except (ValueError, TypeError):
                continue  # Skip posts with invalid points
        return filtered
    
    def validate_config(self) -> bool:
        """Validate HackerNews collector configuration."""
        required_fields = ["keywords", "min_points"]
        return all(field in self.config for field in required_fields) 