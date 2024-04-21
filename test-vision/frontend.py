"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import openai
from openai import OpenAI
from patient_context import patient_zero, prompt_for_patient

client = OpenAI(api_key="")

thread = None
assistant = None

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

#df

st.set_page_config("Labwork AI", "🩸", layout="wide")
st.title("Labwork AI  :drop_of_blood:")
st.header("Your one-stop-shop for all things related to understanding blood work reports.")
if "cache" not in st.session_state:
  st.session_state.cache = {}

with st.form("my-form", clear_on_submit=True):
  #file = st.file_uploader("FILE UPLOADER")
  uploaded_files = st.file_uploader('Choose your .pdf file', type="pdf",  accept_multiple_files=True)
  submitted = st.form_submit_button("Analyze lab work")


def chat_bot(thread, assistant):
  if "messages" not in st.session_state:
    st.session_state.messages = []
  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])

  message_content = "nothing"

  # React to user input
  if prompt := st.chat_input("What is up?"):
      # Display user message in chat message container
      st.chat_message("user").markdown(prompt)
      # Add user message to chat history
      st.session_state.messages.append({"role": "user", "content": prompt})

      messages = list(client.beta.threads.messages.list(thread_id=thread.id))
      message_content = messages[0].content[0].text
      annotations = message_content.annotations
      citations = []
      for index, annotation in enumerate(annotations):
          message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
          if file_citation := getattr(annotation, "file_citation", None):
              cited_file = client.files.retrieve(file_citation.file_id)
              citations.append(f"[{index}] {cited_file.filename}")

      print(f"specific message: {message_content.value}")
      client.beta.threads.messages.create(
          thread_id = thread.id,
          role = "user",
          content = prompt
      )
      client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=""
      )

  response = f"Echo: {prompt} Answer: {message_content}"
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
    tools=[{"type": "file_search"}],
  )

  vector_store = client.beta.vector_stores.create(name="Blood Reports")
  file_paths = uploaded_files
  file_streams = [(path) for path in file_paths]

  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
  )

  assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
  )

  prompt_for_patient_str = prompt_for_patient(patient_zero)
  prompt_for_patient_str += "give me a comprehensive view of my health based on the latest blood work report. Don't yap."
  thread = client.beta.threads.create(
      messages=[
      {
        "role": "user",
        "content": prompt_for_patient_str,
      }
    ]
  )
  thread.tool_resources.file_search

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

  print(f"specific message: {message_content.value}")
  client.beta.threads.messages.create(
      thread_id = thread.id,
      role = "assistant",
      content = message_content.value
  )
  st.write(message_content.value)
  return [thread, assistant]
first_time = True
if uploaded_files and first_time and submitted:
    with st.spinner("Analyzing blood work..."):
      data = extract_data(uploaded_files)
      st.session_state.cache = { "data": data }
      uploaded_files = None
      first_time = False

if (st.session_state.cache and st.session_state.cache["data"]):
  data = st.session_state.cache["data"]
  thread = data[0]
  assistant = data[1]
  chat_bot(thread, assistant)

      


