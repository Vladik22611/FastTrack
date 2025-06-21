import asyncio
import grpc
from server.generated import tracking_pb2, tracking_pb2_grpc
from config import SERVER_HOST, SERVER_PORT

status_mapping = {
    0: "UNKNOWN",
    1: "AVAILABLE",
    2: "ON_TRIP",
    3: "OFFLINE",
}


async def track_driver():
    async with grpc.aio.insecure_channel(
        f"{SERVER_HOST}:{SERVER_PORT}"
    ) as channel:
        stub = tracking_pb2_grpc.TrackingServiceStub(channel)

        try:
            print("Finding available drivers...")
            available_drivers = []
            async for driver in stub.GetAvailableDrivers(
                tracking_pb2.AreaFilter(
                    center_lat=59.934,
                    center_lng=30.335,
                    radius_km=5,
                )
            ):
                available_drivers.append(driver)
                print(f"Driver {driver.driver_uuid} is {status_mapping.get(int(driver.status),
                                        "UNKNOWN")}")

            if not available_drivers:
                print("No drivers available")
                return

            print("\nAvailable drivers:")
            for i, driver in enumerate(available_drivers, 1):
                print(
                    f"{i}. {driver.driver_uuid} ({status_mapping.get(int(driver.status),
                                        "UNKNOWN")}, {driver.distance:.2f} km)"
                )

            while True:
                try:
                    choice = int(input("Select driver number: "))
                    if 1 <= choice <= len(available_drivers):
                        driver_id = available_drivers[choice - 1].driver_uuid
                        break
                    print("Invalid number, try again")
                except ValueError:
                    print("Please enter a number")

            print(f"\nTracking driver {driver_id}...")
            async for location in stub.StreamDriverLocation(
                tracking_pb2.GeoRequest(driver_uuid=driver_id)
            ):
                print(f"Driver at: {location.latitude}, {location.longitude}")

        except grpc.RpcError as e:
            print(f"RPC failed: {e.code()}: {e.details()}")


if __name__ == "__main__":
    asyncio.run(track_driver())
