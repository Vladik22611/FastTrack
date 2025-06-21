#  Система отслеживания водителей (gRPC + Redis)  

## Стек технологий  

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![gRPC](https://img.shields.io/badge/gRPC-%2343853D.svg?style=for-the-badge&logo=google&logoColor=white)](https://grpc.io/)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Asyncio](https://img.shields.io/badge/asyncio-%2343853D.svg?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/asyncio.html)
[![Protocol Buffers](https://img.shields.io/badge/protobuf-%234285F4.svg?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/protocol-buffers)

## Описание 
Проект представляет собой систему мониторинга водителей в реальном времени с использованием:
- gRPC для связи между компонентами
- Redis для хранения данных и геопространственных запросов
- Asyncio для асинхронной обработки

## Установка

```shell
# Склонировать репозиторий
git clone https://github.com/Vladik22611/FastTrack.git
```

> [!IMPORTANT]
> Для дальнейшей работы понадобится Redis.
> Чтобы его установить выполните в терминале следующую команду:
```shell
# Установка Redis
sudo apt install redis-server -y
```

```shell
# Добавление виртуального окражения и установка зависимостей
python -m venv venv
source venv/scripts/activate
pip install -r requirements.txt
```
## Запуск
```shell
# Запустите Redis(в отдельном терминале)
redis-server
```
```shell
# Запустите сервер(в новом терминале)
python -m server.main
```
```shell
# Запустите клиент водителя (в новом терминале):
python -m clients.driver_client
```
```shell
# Запустите клиент пассажира (в новом терминале):
python -m clients.passenger_client
```
## Взаимодействие компонентов
1. Водитель подключается к серверу и начинает отправлять свои координаты
2. Сервер сохраняет данные в Redis с геопространственным индексом
3. Пассажир запрашивает список доступных водителей в радиусе 5 км
4. Сервер возвращает ближайших водителей со статусом "AVAILABLE"
5. Пассажир выбирает водителя и начинает отслеживать его местоположение

## Настройки 
Основные параметры можно изменить в файле config.py 

## Автор:

Гречкин Владсислав  

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/g_vladislav22)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Vladik22611)

