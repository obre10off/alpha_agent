from typing import List, Dict, Any
from .base import BaseCollector
from composio_llamaindex import ComposioToolSet, Action
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker

class GitHubCollector(BaseCollector):
    """Collector for GitHub repositories."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the GitHub collector."""
        super().__init__(config)
        self.llm = OpenAI(model="gpt-4o-mini")
        self.toolset = ComposioToolSet()
        self.tools = self.toolset.get_tools(actions=['GITHUB_SEARCH_REPOSITORIES'])
        
        # Set up agent
        prefix_messages = [
            ChatMessage(
                role="system",
                content=(
                    "You are a GitHub project finder specializing in AI agents and autonomous systems. "
                    "Look for repositories that demonstrate innovative approaches to AI agents, "
                    "autonomous systems, or agent frameworks. Focus on active projects with good documentation."
                )
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
        """Collect interesting GitHub repositories."""
        repositories = []
        search_queries = [
            "AI agent framework language:python stars:>100",
            "autonomous AI agent language:python stars:>100",
            "LLM agent framework language:python stars:>100",
            "AI assistant framework language:python stars:>100"
        ]
        
        for query in search_queries:
            try:
                prompt = f"Find GitHub repositories matching: {query}"
                response = await self.agent.achat(prompt)
                
                # Process the response
                if hasattr(response, 'response'):
                    results = response.response if isinstance(response.response, list) else [response.response]
                    
                    for repo in results:
                        # Add platform identifier and standardize fields
                        repo_data = {
                            "platform": "GitHub",
                            "title": repo.get("name", ""),
                            "text": repo.get("description", ""),
                            "url": repo.get("html_url", ""),
                            "stars": repo.get("stargazers_count", 0),
                            "language": repo.get("language", ""),
                            "created_at": repo.get("created_at", ""),
                            "updated_at": repo.get("updated_at", ""),
                            "topics": repo.get("topics", []),
                            "readme": await self._fetch_readme(repo.get("full_name", ""))
                        }
                        repositories.append(repo_data)
                        
            except Exception as e:
                print(f"Error searching GitHub with query '{query}': {str(e)}")
                continue
                
        return repositories
    
    async def _fetch_readme(self, repo_full_name: str) -> str:
        """Fetch repository README content."""
        try:
            prompt = f"Get the README content for repository: {repo_full_name}"
            response = await self.agent.achat(prompt)
            if hasattr(response, 'response'):
                return response.response.get("content", "")
        except Exception as e:
            print(f"Error fetching README for {repo_full_name}: {str(e)}")
        return ""
    
    async def filter_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter GitHub repositories based on relevance and quality."""
        filtered = []
        for repo in content:
            try:
                # Basic filtering criteria
                stars = int(repo.get("stars", 0))
                has_readme = bool(repo.get("readme", "").strip())
                has_description = bool(repo.get("text", "").strip())
                
                if (stars >= self.config.get("min_stars", 100) and 
                    has_readme and 
                    has_description):
                    filtered.append(repo)
            except (ValueError, TypeError):
                continue
        return filtered
    
    def validate_config(self) -> bool:
        """Validate GitHub collector configuration."""
        required_fields = ["min_stars"]
        return all(field in self.config for field in required_fields) 