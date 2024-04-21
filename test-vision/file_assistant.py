from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

client = OpenAI(api_key="")

assistant = client.beta.assistants.create(
  name="Bloodwork Analysis",
  instructions="You are well-versed in bloodwork and can tell what metrics say what about a person's health. Use your knowledge to explain bloodwork results to patients in layman's terms, as if they are 16 years old.",
  model="gpt-4-turbo",
  tools=[{"type": "file_search"}],
)

vector_store = client.beta.vector_stores.create(name="Blood Reports")
file_paths = ["blood1.pdf", "blood2.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

thread = client.beta.threads.create(
    messages=[
    {
      "role": "user",
        "content": "Give me a comprehensive view of how my health has changed between these blood reports. Don't yap.",
    }
  ]
)

thread.tool_resources.file_search

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)
messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

while True:
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
    if (loop == 1):
      new_message = client.beta.threads.messages.create(
          thread_id = thread.id,
          role = "assistant",
          content = message_content.value
      )
      new_message_2 = client.beta.threads.messages.create(
          thread_id = thread.id,
          role = "user",
          content = "Is my WBC high? Just say yes or no."
      )
    elif (loop == 2):
      new_message = client.beta.threads.messages.create(
          thread_id = thread.id,
          role = "assistant",
          content = message_content.value
      )
      new_message_2 = client.beta.threads.messages.create(
          thread_id = thread.id,
          role = "user",
          content = "Do I need to make lifestyle changes for this? Don't yap."
      )
    
    run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions=""
    )