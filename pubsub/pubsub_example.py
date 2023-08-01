import os
from google.cloud import pubsub_v1

os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/pubsub/credentials.json"

project_id = "my-project"
topic_id = "my-topic"
subscription_id = "my-subscription"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

try:
    publisher.create_topic(request={"name": topic_path})
except Exception:
    pass

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

try:
    subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})
except Exception:
    pass

message_data = "Mensagem de exemplo"
message_bytes = message_data.encode("utf-8")
future = publisher.publish(topic_path, data=message_bytes)
print(f"Mensagem publicada: {future.result()}")

def callback(message):
    print(f"Mensagem recebida: {message.data}")
    message.ack()

subscriber.subscribe(subscription_path, callback=callback)

while True:
    pass
