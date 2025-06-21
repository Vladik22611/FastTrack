import asyncio
import grpc
import uuid
from datetime import datetime
from server.generated import tracking_pb2, tracking_pb2_grpc
from config import SERVER_HOST, SERVER_PORT, UPDATE_INTERVAL


async def generate_updates(driver_id):
    """Генератор обновлений с обработкой остановки"""
    lat, lng = 59.934, 30.335
    try:
        while True:
            yield tracking_pb2.DriverLocationUpdate(
                driver_uuid=driver_id,
                latitude=lat,
                longitude=lng,
                status="STATUS_AVAILABLE",
            )
            lat += 0.001
            lng += 0.001
            await asyncio.sleep(UPDATE_INTERVAL)
    except asyncio.CancelledError:
        print("Update generator stopped")
        raise


async def run_driver(driver_id):
    async with grpc.aio.insecure_channel(
        f"{SERVER_HOST}:{SERVER_PORT}"
    ) as channel:
        stub = tracking_pb2_grpc.TrackingServiceStub(channel)

        try:
            call = stub.UpdateDriverLocation()

            async def send_task():
                async for update in generate_updates(driver_id):
                    await call.write(update)
                    print(f"Sent: {update.latitude}, {update.longitude}")

            # Запускаем отправку и получение параллельно
            sender = asyncio.create_task(send_task())
            async for ack in call:
                print(f"ACK at {datetime.now().isoformat()}: {ack}")

        except grpc.RpcError as e:
            print(f"Server error: {e.code()}: {e.details()}")
        finally:
            if not sender.done():
                sender.cancel()
            await call.done_writing()


if __name__ == "__main__":
    driver_id = f"driver_{uuid.uuid4()}"
    print(f"Starting driver {driver_id}")

    try:
        asyncio.run(run_driver(driver_id))
    except KeyboardInterrupt:
        print("\nClient stopped by user")
