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
      "content": "Give me a comprehensive view of how my health has changed between these blood reports.",
    }
  ]
)

print(thread.tool_resources.file_search)


# run = client.beta.threads.runs.create_and_poll(
#     thread_id=thread.id, assistant_id=assistant.id
# )

# messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

# message_content = messages[0].content[0].text
# annotations = message_content.annotations
# citations = []
# for index, annotation in enumerate(annotations):
#     message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
#     if file_citation := getattr(annotation, "file_citation", None):
#         cited_file = client.files.retrieve(file_citation.file_id)
#         citations.append(f"[{index}] {cited_file.filename}")

# print(message_content.value)
# print("\n".join(citations))

# Then, we use the stream SDK helper
# with the EventHandler class to create the Run
# and stream the response.
 
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print("on message done")
        print(message_content.value)
        print("\n".join(citations))

print('running stream')
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()

print("actually done")
