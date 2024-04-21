"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import openai
from openai import OpenAI

client = OpenAI(api_key="sk-proj-wh7twY7WQ4XfnBTI7WYpT3BlbkFJgyYp2ePIVN3wI3xUJknU")

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

#df

st.set_page_config("Labwork AI", "🩸", layout="wide")
st.title("Labwork AI  :drop_of_blood:")
st.header("Your one-stop-shop for all things related to understanding blood work reports.")

with st.form("my-form", clear_on_submit=True):
  #file = st.file_uploader("FILE UPLOADER")
  uploaded_files = st.file_uploader('Choose your .pdf file', type="pdf",  accept_multiple_files=True)
  st.form_submit_button("Analyze lab work")

def chat_bot():
  if "messages" not in st.session_state:
    st.session_state.messages = []
  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])

  # React to user input
  if prompt := st.chat_input("What is up?"):
      # Display user message in chat message container
      st.chat_message("user").markdown(prompt)
      # Add user message to chat history
      st.session_state.messages.append({"role": "user", "content": prompt})

      response = f"Echo: {prompt}"
      # Display assistant response in chat message container
      with st.chat_message("assistant"):
          st.markdown(response)
      # Add assistant response to chat history
      st.session_state.messages.append({"role": "assistant", "content": response})

def extract_data(uploaded_files):
  assistant = client.beta.assistants.create(
  name="Bloodwork Analysis",
  instructions="You are well-versed in bloodwork and can tell what metrics say what about a person's health. Use your knowledge to explain bloodwork results to patients in layman's terms, as if they are 16 years old.",
  model="gpt-4-turbo",
  tools=[{"type": "file_search"}],)

  vector_store = client.beta.vector_stores.create(name="Blood Reports")
  file_paths = uploaded_files
  file_streams = [path for path in file_paths]

  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
  )

  print(file_batch.status)
  print(file_batch.file_counts)

  assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
  )

  thread = client.beta.threads.create(
      messages=[
      {
        "role": "user",
        "content": "Give me a comprehensive view of how my health has changed between these blood reports. don't yap",
      }
    ]
  )

  print(thread.tool_resources.file_search)


  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations
  citations = []
  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)
          citations.append(f"[{index}] {cited_file.filename}")
  st.write(message_content.value)
  return
first_time = True
if uploaded_files and first_time:
    with st.spinner("Analyzing blood work..."):
      df = extract_data(uploaded_files)
      uploaded_files = None
      first_time = False

chat_bot()

      


