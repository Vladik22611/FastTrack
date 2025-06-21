import grpc
import logging
import asyncio
from .generated import tracking_pb2_grpc
from .tracking_service import Tracking


async def serve() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    server = grpc.aio.server()
    tracking_pb2_grpc.add_TrackingServiceServicer_to_server(Tracking(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)

    await server.start()
    logger.info(f"Server started on {listen_addr}")
    await server.wait_for_termination()


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception("Server crashed: %s", e)
        raise
