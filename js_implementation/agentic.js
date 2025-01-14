import { OpenAI } from "openai";
import { OpenAIToolSet } from "composio-core";
const openai_client = new OpenAI({apiKey: process.env.OPENAI_API_KEY});
const composio_toolset = new OpenAIToolSet({
    apiKey: "85zq31ck6okzfoqknx89rk"
});

const tools = await composio_toolset.getTools({
    actions: ["HACKERNEWS_SEARCH_POSTS"]
});


const instruction = "Search through hackernews and find me 3 posts where people discuss ideas about building AI agents/ agentic systems";

// Creating a chat completion request to the OpenAI model
const response = await openai_client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: instruction }],
    tools: tools,
    tool_choice: "auto",
});

const tool_response = await composio_toolset.handleToolCall(response);

console.log(tool_response);

