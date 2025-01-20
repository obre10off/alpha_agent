import dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker
from composio_llamaindex import Action, ComposioToolSet
from typing import List, Dict
dotenv.load_dotenv()

class RepoSearchAndNotify:
    def __init__(self, api_key: str, recipient_email: str):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.composio_toolset = ComposioToolSet(api_key=api_key)
        self.recipient_email = recipient_email

    def _create_email_content(self, repos_data: str) -> Dict[str, str]:
        """Format repository data into a nice email"""
        subject = "Latest AI Repository Updates"
        
        email_body = """
Hello!

Here are the latest interesting AI repositories I found for you:

{repos_data}

Best regards,
Your AI Agent
        """.format(repos_data=repos_data)
        
        return {
            "subject": subject,
            "body": email_body
        }

    def execute(self):
        # 1. Search for repositories
        search_tools = self.composio_toolset.get_tools(actions=['GITHUB_SEARCH_REPOSITORIES'])
        
        search_agent = FunctionCallingAgentWorker(
            tools=search_tools,
            llm=self.llm,
            prefix_messages=[
                ChatMessage(
                    role="system",
                    content="You are a technical researcher focused on finding relevant AI repositories."
                ),
            ],
            verbose=True
        ).as_agent()

        # Perform the search
        search_response = search_agent.chat(
            "Search for repositories related to various AI ideas/topics/implementations. "
            "AI agents, autonomous systems, and AI-related projects are the main focus. "
            "Return 3 repositories that are most relevant to the topic. "
            "The repositories should not be older than 5 months. "
            "They should include code, do not give me any repos that have only .md files and no code implementation"
        )

        # 2. Send email with results
        email_tools = self.composio_toolset.get_tools(actions=['GMAIL_SEND_EMAIL'])
        
        email_agent = FunctionCallingAgentWorker(
            tools=email_tools,
            llm=self.llm,
            prefix_messages=[
                ChatMessage(
                    role="system",
                    content="You are an email assistant. Send emails with the provided content."
                ),
            ],
            verbose=True
        ).as_agent()

        # Format and send email
        email_content = self._create_email_content(search_response.response)
        
        email_prompt = (
            f"Send an email to {self.recipient_email} "
            f"with the subject: '{email_content['subject']}' "
            f"and the following body: '{email_content['body']}'"
        )
        
        email_response = email_agent.chat(email_prompt)
        
        return {
            "search_response": search_response,
            "email_response": email_response
        }

if __name__ == "__main__":
    # Initialize and run
    agent = RepoSearchAndNotify(
        api_key="85zq31ck6okzfoqknx89rk",
        recipient_email="mariosy18@gmail.com"
    )
    
    result = agent.execute()
    print("Process completed!")
    print("Search Response:", result["search_response"])
    print("Email Response:", result["email_response"]) 