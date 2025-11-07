import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain.tools.render import render_text_description
from langchain.callbacks import StreamlitCallbackHandler
from langchain import hub
from dotenv import load_dotenv
import os

# load_dotenv()

# Arxiv and Wikipedia Tools
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=250)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)

api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

search = DuckDuckGoSearchRun(name="Search")

# Streamlit UI
st.title("🔍 Agentic SmartSearch Engine")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq AI API Key:", type="password")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm your AI search agent! How can I help you today?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Ask anything (e.g. 'Find latest paper on quantum AI')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True)
    tools = [search, arxiv, wiki]

    # Create a modern ReAct Agent
    prompt_template = hub.pull("hwchase17/react")  # pulls default reasoning + acting prompt
    agent = create_react_agent(llm, tools, prompt_template)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = agent_executor.invoke({"input": prompt}, config={"callbacks": [st_cb]})
        answer = response["output"]
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        st.write(answer)
