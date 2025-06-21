import asyncio
import grpc
from server.generated import tracking_pb2, tracking_pb2_grpc

async def simulate_driver(driver_id):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = tracking_pb2_grpc.TrackingServiceStub(channel)
        call = stub.UpdateDriverLocation()
        
        lat, lng = 59.934, 30.335
        try:
            while True:
                update = tracking_pb2.DriverLocationUpdate(
                    driver_uuid=driver_id,
                    latitude=lat,
                    longitude=lng,
                    status="STATUS_AVAILABLE",
                )
                await call.write(update)
                lat += 0.001
                lng += 0.001
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await call.done_writing()

async def run_load_test(num_drivers):
    tasks = []
    for i in range(num_drivers):
        driver_id = f"load_test_driver_{i}"
        task = asyncio.create_task(simulate_driver(driver_id))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(run_load_test(100))  # 100 симулированных водителей