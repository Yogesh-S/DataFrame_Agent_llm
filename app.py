import streamlit as st
# from langchain_community.llms import Ollama
import pandas as pd
from langchain_experimental.agents import create_csv_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
#####
df = pd.read_pickle('stored_dataframe.pkl')
# llm = Ollama(model="phi4-mini:latest")
####
## set up Streamlit 
st.title("ChatBot using DataFrame Loader")

st.sidebar.title("Settings")
api_key=st.sidebar.text_input("Enter your Groq API Key:",type="password")

if api_key:

    llm=ChatGroq(groq_api_key=api_key,model_name="gemma2-9b-it",streaming=True)
    page = st.selectbox('Select the dashboard page',
                        ['<  Select  >']+list(df["Page Name"].unique()))

    if page != '<  Select  >':
        visuals = st.selectbox('Select the visual',
                    ['<  Select  >']+list(df[df["Page Name"]==page]["Visual Name"].unique()))

        if visuals != '<  Select  >':

            df2 = df[(df.loc[:, "Page Name"] == page) &  (df.loc[:, "Visual Name"] == visuals)]

            # st.write(df2)

            if "messages" not in st.session_state:
                st.session_state["messages"]=[
                    {"role":"assisstant",
                     "content":"Hi, I'm a Power BI chatbot. How can I help you?"}
                ]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg['content'])

            if prompt:=st.chat_input(placeholder="Enter text here"):
                st.session_state.messages.append({"role":"user","content":prompt})
                st.chat_message("user").write(prompt)

                agent_executor = create_pandas_dataframe_agent(
                llm,
                df2["Summarized Data"].iloc[0],
                verbose=True,
                allow_dangerous_code=True,
                agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                handle_parsing_errors=True,
                tools=[PythonAstREPLTool()]
                )

                with st.chat_message("assistant"):
                    with st.spinner(text = "In progress..."):
                    # st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
                        response=agent_executor.invoke(prompt)
                        st.session_state.messages.append({'role':'assistant',"content":response["output"]})
                        st.write(response["output"])

                # user_question = st.text_input("Ask your question?")

                # if user_question is not None and user_question != "":
                # with st.spinner(text = "In progress..."):
                #     response = agent_executor.invoke(prompt)
                #     response["output"]

                # with st.chat_message("assistant"):
                #     # st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
                #     response=search_agent.run(st.session_state.messages,callbacks=[st_cb])
                #     st.session_state.messages.append({'role':'assistant',"content":response})
                #     st.write(response)
