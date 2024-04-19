import boto3
from datetime import date
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_community.chat_models import BedrockChat
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain.agents import Tool
import json

# ------------------------------------------------------------------------
# Constants

# Harcoded Employee Metadata 
EMPLOYEE_METADATA = { "agent_name": "Example Agent", "employee_class": "F", "employee_id": "112662604" }

# Bedrock model id
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Bedrock model inference parameters
MODEL_KWARGS =  { 
    "max_tokens": 2048,
    "temperature": 0.0,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": ["\n\nHuman"],
}

# ------------------------------------------------------------------------
# LangChain

@tool
def list_southwest_flights_url(date, origination_airport_code, destination_airport_code, ):
    """Returns the Southwest Flights URL for the input paramters.

    date: str --> The date of the flight in the format 2021-11-30.

    origination_airport_code: str --> The origin airport 3-letter code. SAN, LAX, SFO

    destination_airport_code: str --> The destination airport 3-letter code. DAL, PHX, LGA
    """
    import scrape
    url = scrape.get_southwest_flights_url(
       date,
        origination_airport_code,
        destination_airport_code,
        1,
        1
    )
    return url

@tool
def curr_date(text):
    """Returns todays date, use this for any \
    questions related to knowing todays date. \
    The input should always be an empty string, \
    and this function will always return todays \
    date - any date math should occur \
    outside this function."""
    return str(date.today())

def initialize_tools():
    date_tool = Tool(
        name="DateTool", 
        func=curr_date, 
        description="Useful for when you need to answer what the current date is"
    )

    southwest_list_flights_url_tool = Tool(
        name="SouthwestListFlightsURL Tool", 
        func=list_southwest_flights_url, 
        description="Useful for generating the URL that lists flights on Southwest"
    )

    return [
        date_tool, 
        southwest_list_flights_url_tool
    ]

def initialize_bedrock_runtime():
    """Initialize the Bedrock runtime."""
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2"
    )
    return bedrock_runtime

def initialize_model(bedrock_runtime, model_id, model_kwargs):
    model = BedrockChat(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )
    return model

def initialize_streamlit_memory():
    history = StreamlitChatMessageHistory()
    return history

def initialize_memory(streamlit_memory):
    memory = ConversationBufferMemory(
        chat_memory=streamlit_memory,
        return_messages=True,
        memory_key="chat_history",
        output_key="output"
    )
    return memory

def intialize_prompt():
    system = '''You are a Southwest Airlines customer support agent. You help customers find flights and book them.
    Your goal is to generate an answer to the employee's message in a friendly, customer support like tone.

    Do not use any tools if you can answer the employee's latest message without them.
    
    You have access to the following tools:

    {tools}

    Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

    Valid "action" values: "Final Answer" or {tool_names}

    Provide only ONE action per $JSON_BLOB, as shown:

    ```
    {{
    "action": $TOOL_NAME,
    "action_input": $INPUT
    }}
    ```

    Follow this format:

    Question: input question to answer
    Thought: consider previous and subsequent steps
    Action:
    ```
    $JSON_BLOB
    ```
    Observation: action result
    ... (repeat Thought/Action/Observation N times)
    Thought: I know what to respond
    Action:
    ```
    {{
    "action": "Final Answer",
    "action_input": "Final response to human"
    }}

    Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

    human = '''

    {input}

    {agent_scratchpad}

    (reminder to respond in a JSON blob no matter what)'''

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human),
        ]
    )

    return prompt

# Initialize the Model
bedrock_runtime = initialize_bedrock_runtime()
model = initialize_model(bedrock_runtime, MODEL_ID, MODEL_KWARGS)

# Initialize the Memory
streamlit_memory = initialize_streamlit_memory()
memory = initialize_memory(streamlit_memory)

# Initialize the Tools
tools = initialize_tools()

# Initialize the Agent
system_prompt = intialize_prompt()
agent = create_structured_chat_agent(
    model,
    tools,
    system_prompt
)
executor = agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )

# ------------------------------------------------------------------------
# Streamlit

import streamlit as st

# Page title
st.set_page_config(page_title="Southwest Generative AI Agent Demo", page_icon=":plane:")
st.title("Southwest Generative AI Agent Demo")
st.caption("This is a demo of a Generative AI Assistant that can use Tools to interact with Southwest Airlines.")

# Initialize the session state for steps 
if "steps" not in st.session_state.keys():
    st.session_state.steps = {}

# Display current chat messages
for message in streamlit_memory.messages:
    with st.chat_message(message.type):
        st.write(message.content)

# Chat Input - User Prompt 
if user_input := st.chat_input("Message"):
    with st.chat_message("human"):
        st.write(user_input)

    # As usual, new messages are added to StreamlitChatMessageHistory when the Chain is called.
    config = {"configurable": {"session_id": "any"}}

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        chat_history = memory.buffer_as_messages
        input_metadata = json.dumps(EMPLOYEE_METADATA)
        response = agent_executor.invoke(
            input={
                "input": f"{user_input} | {input_metadata}",
                "chat_history": chat_history,             
            },
            config=cfg
        )
        st.write(response["output"])
        st.session_state.steps[str(len(streamlit_memory.messages) - 1)] = response["intermediate_steps"]
