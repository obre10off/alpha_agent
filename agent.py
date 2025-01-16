import dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.agent import FunctionCallingAgentWorker
from composio_llamaindex import Action, ComposioToolSet

dotenv.load_dotenv()

llm = OpenAI(model="gpt-4o-mini")

composio_toolset = ComposioToolSet(api_key="85zq31ck6okzfoqknx89rk")
tools = composio_toolset.get_tools(actions=['HACKERNEWS_SEARCH_POSTS'])

prefix_messages = [
    ChatMessage(
        role="system",
        content=(
            "You are now a integration agent, and what  ever you are requested, you will try to execute utilizing your tools."
        ),
    )
]

agent = FunctionCallingAgentWorker(
    tools=tools,
    llm=llm,
    prefix_messages=prefix_messages,
    max_function_calls=10,
    allow_parallel_tool_calls=False,
    verbose=True,
).as_agent()

response = agent.chat("Search through hackernews and find me 3 posts where people discuss ideas about building AI agents or agentic AI. Go back in time if you cannot find posts from today.")
print("Response:", response)

dotenv.load_dotenv()

llm = OpenAI(model="gpt-4o-mini")

composio_toolset = ComposioToolSet(api_key="85zq31ck6okzfoqknx89rk")
tools = composio_toolset.get_tools(actions=['HACKERNEWS_GET_TODAYS_POSTS'])

prefix_messages = [
    ChatMessage(
        role="system",
        content=(
            "You are now a integration agent, and what  ever you are requested, you will try to execute utilizing your tools."
        ),
    )
]

agent = FunctionCallingAgentWorker(
    tools=tools,
    llm=llm,
    prefix_messages=prefix_messages,
    max_function_calls=10,
    allow_parallel_tool_calls=False,
    verbose=True,
).as_agent()
response = agent.chat("your task description here")
print("Response:", response)