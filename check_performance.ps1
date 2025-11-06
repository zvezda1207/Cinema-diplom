# PowerShell скрипт для проверки производительности контейнеров

Write-Host "=== Проверка сетевой задержки между контейнерами ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Проверка подключения к БД из backend:" -ForegroundColor Yellow
docker-compose exec backend python -c @"
import asyncio
import time
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
"@

Write-Host ""
Write-Host "=== Проверка нагрузки на БД ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Активные подключения:" -ForegroundColor Yellow
docker-compose exec db psql -U admin -d cinema -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"

Write-Host ""
Write-Host "Медленные запросы (если есть):" -ForegroundColor Yellow
docker-compose exec db psql -U admin -d cinema -c @"
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '1 second'
  AND state = 'active'
ORDER BY duration DESC;
"@

Write-Host ""
Write-Host "Размер таблиц:" -ForegroundColor Yellow
docker-compose exec db psql -U admin -d cinema -c @"
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"@

Write-Host ""
Write-Host "=== Проверка индексов ===" -ForegroundColor Cyan
docker-compose exec db psql -U admin -d cinema -c @"
SELECT 
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('tickets', 'seats', 'available_seats')
ORDER BY tablename, indexname;
"@


