#!/bin/bash
# Скрипт для проверки производительности контейнеров

echo "=== Проверка сетевой задержки между контейнерами ==="
echo ""
echo "1. Задержка от backend к db:"
docker-compose exec backend ping -c 3 db | grep "time=" || echo "Ping недоступен, используем другой метод"

echo ""
echo "2. Проверка подключения к БД из backend:"
docker-compose exec backend python -c "
import asyncio
import time
from app.config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
import asyncpg

async def test_db():
    start = time.time()
    try:
        conn = await asyncpg.connect(
            host='db',
            port=5432,
            user='admin',
            password='password',
            database='cinema'
        )
        await conn.fetchval('SELECT 1')
        await conn.close()
        elapsed = (time.time() - start) * 1000
        print(f'Подключение к БД: {elapsed:.2f}ms')
    except Exception as e:
        print(f'Ошибка: {e}')

asyncio.run(test_db())
"

echo ""
echo "=== Проверка нагрузки на БД ==="
echo ""
echo "Активные подключения:"
docker-compose exec db psql -U admin -d cinema -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"

echo ""
echo "Медленные запросы (если есть):"
docker-compose exec db psql -U admin -d cinema -c "
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '1 second'
  AND state = 'active'
ORDER BY duration DESC;
"

echo ""
echo "Размер таблиц:"
docker-compose exec db psql -U admin -d cinema -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"


