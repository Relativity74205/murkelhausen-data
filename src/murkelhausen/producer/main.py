import logging
import random
from datetime import datetime
from uuid import uuid4

from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
    StringSerializer,
)
from dataclasses_avroschema import AvroModel

from confluent_kafka import Producer, Message
from confluent_kafka.schema_registry import SchemaRegistryClient

from murkelhausen.garmin.functions import HeartRate
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


def main(data: AvroModel):
    topic = "test_avro_python_serializer_3"
    schema_registry_conf = {"url": "http://192.168.1.69:8081"}  # TODO: add to config
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    # schema = Schema(schema_type="AVRO", schema_str=data.avro_schema())
    # schema_registry_client.register_schema(topic + "-value", schema=schema)
    avro_serializer = AvroSerializer(
        schema_registry_client, data.avro_schema(), lambda obj, ctx: obj.to_dict()
    )
    string_serializer = StringSerializer("utf_8")

    producer_conf = {"bootstrap.servers": "192.168.1.69:19092"}  # TODO: add to config

    producer = Producer(producer_conf)

    log.info("Producing user records to topic {}. ^C to exit.".format(topic))
    # while True:
    # Serve on_delivery callbacks from previous calls to produce()
    producer.poll(0.0)
    try:
        producer.produce(
            topic=topic,
            key=string_serializer(str(uuid4())),
            value=avro_serializer(
                data, SerializationContext(topic, MessageField.VALUE)
            ),
            on_delivery=delivery_report,
        )
    except ValueError:
        logging.exception("Message serialization failed")

    log.info("\nFlushing records...")
    producer.flush()


if __name__ == "__main__":
    setup_logging()
    main(HeartRate(tstamp=datetime.now(), heart_rate=random.randint(50, 200)))
