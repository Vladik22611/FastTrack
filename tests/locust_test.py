from locust import User, task, between, events
import grpc
import time
import tracking_pb2, tracking_pb2_grpc

class GrpcUser(User):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Инициализация пользователя")
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = tracking_pb2_grpc.TrackingServiceStub(self.channel)

    @task
    def test_connection(self):
        start_time = time.time()
        print("Выполнение test_connection")
        try:
            # Простейший запрос для проверки
            request = tracking_pb2.GeoRequest(driver_uuid="load_test_driver")
            response = list(self.stub.StreamDriverLocation(request))[0]  # Получаем первый элемент
            print(f"Получен ответ: {response}")
                
            events.request.fire(
                request_type="grpc",
                name="ConnectionTest",
                response_time=(time.time()-start_time)*1000,
                response_length=0
            )
        except Exception as e:
            print(f"Ошибка: {e}")
            events.request.fire(
                request_type="grpc",
                name="ConnectionTest",
                response_time=(time.time()-start_time)*1000,
                response_length=0,
                exception=e
            )

if __name__ == "__main__":
    # Тест без Locust
    user = GrpcUser(environment=None)
    user.test_connection()