import json

from logger import logger

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError as AsyncKafkaError

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError as SyncKafkaError

from typing import Callable, Awaitable, Any

class Consumer:
    def __init__(self, topic_name: str, kafka_endpoint: str = "kafka:9094"):
        self.topic_name = topic_name
        
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=kafka_endpoint)

            topic_list = [
                NewTopic(
                    name=topic_name, 
                    num_partitions=1,
                    replication_factor=1
                )
            ]
            admin_client.create_topics(
                new_topics=topic_list,
                validate_only=False
            )

            logger.info(f"{topic_name} topic was created!")

        except SyncKafkaError as e1:
            logger.error(f"Can't create {topic_name} topic", exc_info=True)
        finally:
            try:
                self._consumer = AIOKafkaConsumer(
                    topic_name,
                    bootstrap_servers=kafka_endpoint
                )
            except AsyncKafkaError as e2:
                logger.error(f"Can't connect to kafka")

    async def start(self) -> None:
        try:
            await self._consumer.start()
            logger.info(f"Consumer of {self.topic_name} topic started")
        except AsyncKafkaError as e:
            logger.error(f"Can't start consumer of {self.topic_name} topic", exc_info=True)
    
    async def stop(self) -> None:
        try:
            await self._consumer.stop()
            logger.info(f"Consumer of {self.topic_name} topic stopped")
        except AsyncKafkaError as e:
            logger.error(f"Can't stop consumer of {self.topic_name} topic", exc_info=True)

    async def consume(self, handler: Callable[[Any], Awaitable[None]]) -> None:
        try:
            async for msg in self._consumer:
                data = json.loads(msg.value)
                await handler(data)
        except AsyncKafkaError as e:
            logger.error(f"Can't read messages from {self.topic_name} topic", exc_info=True)