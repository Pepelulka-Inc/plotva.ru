import asyncio
import signal

from handlers import init_indexes, do

from consumer import Consumer


# init_indexes()


async def main():
    product_consumer = Consumer("products")
    seller_consumer = Consumer("sellers")
    comment_consumer = Consumer("comments")

    await product_consumer.start()
    await seller_consumer.start()
    await comment_consumer.start()

    print("here", flush=True)

    async def stop():
        await product_consumer.stop()
        await seller_consumer.stop()
        await comment_consumer.stop()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(stop()))

    await product_consumer.consume(do)
    await seller_consumer.consume(do)
    await comment_consumer.consume(do)

asyncio.run(main())