import grpc
from redis import asyncio as aioredis
import asyncio
from typing import AsyncIterable, AsyncIterator
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from server.generated import tracking_pb2, tracking_pb2_grpc
from config import (
    REDIS_URL,
    REDIS_MAX_CONNECTIONS,
    REDIS_DRIVER_TTL,
    UPDATE_INTERVAL,
)


class Tracking(tracking_pb2_grpc.TrackingServiceServicer):
    status_mapping = {
        0: tracking_pb2.Status.STATUS_UNKNOWN,
        1: tracking_pb2.Status.STATUS_AVAILABLE,
        2: tracking_pb2.Status.STATUS_ON_TRIP,
        3: tracking_pb2.Status.STATUS_OFFLINE,
    }

    def __init__(self, redis_url=REDIS_URL):
        self.redis = aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=REDIS_MAX_CONNECTIONS,
        )

    async def UpdateDriverLocation(
        self,
        request_iterator: AsyncIterator[tracking_pb2.DriverLocationUpdate],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[tracking_pb2.Ack]:
        try:
            async for r in request_iterator:
                driver_id = r.driver_uuid
                if not (-90 <= r.latitude <= 90) or not (-180 <= r.longitude <= 180):
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid coordinates")
                    continue
                await self.redis.hset(
                    f"driver:{r.driver_uuid}",
                    mapping={"lat": r.latitude, "lng": r.longitude, "status": r.status},
                )

                # Добавляем в геоиндекс
                await self.redis.geoadd(
                    "drivers:geo", (r.longitude, r.latitude, r.driver_uuid)
                )

                await self.redis.expire(f"driver:{r.driver_uuid}",
                                        REDIS_DRIVER_TTL)
                await self.redis.expire("drivers:geo", REDIS_DRIVER_TTL)

                yield tracking_pb2.Ack()
        finally:
            if driver_id:
                await self.redis.hset(
                    f"driver:{driver_id}", "status", "0"  # STATUS_UNKNOWN
                )
                print(f"Driver {driver_id} disconnected, status set to UNKNOWN")

    async def GetAvailableDrivers(
        self,
        request: tracking_pb2.AreaFilter,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterable[tracking_pb2.DriverInfo]:
        drivers = await self.redis.georadius(
            "drivers:geo",
            request.center_lng,
            request.center_lat,
            request.radius_km,
            "km",
            withdist=True,
            count=100,
            sort="ASC",
        )
        for driver_uuid, distance in drivers:
            driver_data = await self.redis.hgetall(f"driver:{driver_uuid}")
            redis_status = int(driver_data.get("status", "0"))
            status = self.status_mapping.get(
                int(redis_status),
                tracking_pb2.Status.STATUS_UNKNOWN
            )

            if status != self.status_mapping[1]:
                continue

            yield tracking_pb2.DriverInfo(
                driver_uuid=driver_uuid, distance=distance, status=status
            )

    async def StreamDriverLocation(
        self,
        request: tracking_pb2.GeoRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterable[tracking_pb2.DriverLocation]:
        while True:
            try:
                driver = await self.redis.hgetall(
                    f"driver:{request.driver_uuid}")
                if not driver:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Driver not found")
                    break
                if driver["status"] == "0":
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Driver is no longer available")
                    break

                now = Timestamp()
                now.FromDatetime(datetime.utcnow())

                redis_status = int(driver.get("status", "0"))
                status = self.status_mapping.get(
                    int(redis_status), tracking_pb2.Status.STATUS_UNKNOWN
                )

                yield tracking_pb2.DriverLocation(
                    driver_uuid=request.driver_uuid,
                    latitude=float(driver.get("lat", 0)),
                    longitude=float(driver.get("lng", 0)),
                    status=status,
                    updated_at=now,
                )

                await asyncio.sleep(UPDATE_INTERVAL)

            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Error: {str(e)}")
                break
