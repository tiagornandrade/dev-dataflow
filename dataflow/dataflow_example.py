import os
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import pubsub_v1
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime

pubsub_emulator_host = "localhost:8085"
os.environ["PUBSUB_EMULATOR_HOST"] = pubsub_emulator_host

project_id = "my-project"
subscription_id = "my-subscription"

options = PipelineOptions(
    runner="DirectRunner",
    streaming=True
)


def print_results(word_count):
    print(word_count)


with beam.Pipeline(options=options) as p:
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    messages = (
        p
        | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(subscription=subscription_path)
        | "Decode message" >> beam.Map(lambda x: x.decode("utf-8"))
        | "Split words" >> beam.FlatMap(lambda line: line.split(" "))
        | "Assign timestamps" >> beam.Map(lambda word: beam.window.TimestampedValue(word, 0))
        | "Fixed window" >> beam.WindowInto(
            beam.window.FixedWindows(10),
            trigger=AfterWatermark(early=AfterProcessingTime(2), late=AfterProcessingTime(5)),
            accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING
        )
        | "Count words" >> beam.combiners.Count.PerElement()
    )

    _ = messages | beam.Map(print)
