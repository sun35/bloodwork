"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import openai
from openai import OpenAI

client = OpenAI(api_key="")

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

#df

st.set_page_config("Labwork AI", "🩸", layout="wide")
st.title("Labwork AI  :drop_of_blood:")
st.header("Your one-stop-shop for all things related to understanding blood work reports.")




uploaded_files = st.file_uploader('Choose your .pdf file', type="pdf",  accept_multiple_files=True)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    #st.write("filename:", uploaded_file.name)
    #st.write(bytes_data)
prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
    
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
  print(message_content.value)
  print("\n".join(citations))



if uploaded_files:
    #df = extract_data(uploaded_files)
    with st.spinner("Analyzing blood work..."):
      df = extract_data(uploaded_files)

