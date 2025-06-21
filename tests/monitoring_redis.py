import asyncio
from redis import asyncio as aioredis
from datetime import datetime

async def monitor_redis():
    redis = aioredis.from_url("redis://localhost:6379")
    
    while True:
        try:
            # Количество ключей
            keys_count = await redis.dbsize()
            
            # Использование памяти
            memory_info = await redis.info("memory")
            
            # Количество подключений
            clients_info = await redis.info("clients")
            
            print(f"\n[{datetime.now().isoformat()}] Redis stats:")
            print(f"Keys: {keys_count}")
            print(f"Memory used: {int(memory_info['used_memory'])/1024/1024:.2f} MB")
            print(f"Connections: {clients_info['connected_clients']}")
            
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Monitoring error: {e}")
            break

asyncio.run(monitor_redis())