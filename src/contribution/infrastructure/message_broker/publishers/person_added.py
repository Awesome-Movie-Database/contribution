from aio_pika import Exchange, Message

from contribution.infrastructure.message_broker.real_events import (
    RealPersonAddedEvent,
)


class PublishPersonAddedEvent:
    def __init__(
        self,
        exchange: Exchange,
        routing_key: str,
    ):
        self._exchange = exchange
        self._routing_key = routing_key

    async def __call__(self, event: RealPersonAddedEvent) -> None:
        await self._exchange.publish(
            message=Message(event.to_json().encode()),
            routing_key=self._routing_key,
        )
