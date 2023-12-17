import logging
import random
import threading
import time
from datetime import datetime
from queue import Empty, Queue
from threading import Event

from confluent_kafka import Message, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
)
from dataclasses_avroschema import AvroModel

from murkelhausen.config import config
from murkelhausen.garmin.functions import EnhancedAvroModel, HeartRate
from murkelhausen.util.logger import setup_logging

log = logging.getLogger(__name__)


def delivery_report(err, msg: Message):
    if err is not None:
        log.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    log.debug(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def get_schema_registry_client() -> SchemaRegistryClient:
    schema_registry_conf = {"url": config.app.confluent_schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    return schema_registry_client


def get_producer() -> Producer:
    producer_conf = {"bootstrap.servers": config.app.confluent_broker_url}
    producer = Producer(producer_conf)
    return producer


def producer_thread(queue: Queue[EnhancedAvroModel], stop_event: Event):
    schema_registry_client = get_schema_registry_client()
    producer = get_producer()
    headers = {"content-type": "avro"}

    while not stop_event.is_set():
        # Serve on_delivery callbacks from previous calls to produce()
        try:
            data = queue.get(block=True, timeout=10)  # TODO move timeout to config
        except Empty:
            sleep_seconds = 5  # TODO move sleep to config
            log.info(f"Queue is empty. Waiting {sleep_seconds} seconds...")
            time.sleep(sleep_seconds)
            continue
        producer.poll(0.0)  # TODO: needed?
        # TODO cache avro_serializer based on data class
        avro_serializer = AvroSerializer(
            schema_registry_client, data.avro_schema(), lambda obj, ctx: obj.to_dict()
        )
        # topic = f"test_avro_python_serializer_{data.__class__.__name__}"
        topic = data.get_topic_name

        try:
            producer.produce(
                topic=topic,
                # key=string_serializer(str(uuid4())),
                value=avro_serializer(
                    data, SerializationContext(topic, MessageField.VALUE)
                ),
                headers=headers,
                on_delivery=delivery_report,
            )
        except ValueError:
            logging.exception("Message serialization failed")

        log.info("Flushing records...")
        producer.flush()

    log.info("Got stop Event. Producer thread stopped.")


def send_stop_event(queue: Queue, stop_event: Event):
    data = HeartRate(tstamp=datetime.now(), heart_rate=random.randint(50, 200))
    queue.put(data)
    log.info("Waiting 5 seconds...")
    time.sleep(5)
    log.info("Sending stop event...")
    stop_event.set()
    log.info("Stop event sent.")


def test():
    queue: Queue[AvroModel] = Queue()
    stop_event = Event()
    thread = threading.Thread(
        target=send_stop_event, kwargs={"stop_event": stop_event, "queue": queue}
    )
    thread.start()
    producer_thread(queue, stop_event)


if __name__ == "__main__":
    setup_logging()
    test()
