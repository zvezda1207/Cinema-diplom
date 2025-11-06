"""
Скрипт для добавления индексов в базу данных для ускорения запросов
Использование: python add_indexes.py
"""
import asyncio
from sqlalchemy import text
from app.dependancy import get_session

async def add_indexes():
    """Добавляет индексы в базу данных"""
    async for session in get_session():
        try:
            print("[INFO] Добавляем индексы в базу данных...")
            
            # Индексы для таблицы tickets
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_tickets_seance_id ON tickets(seance_id)",
                "CREATE INDEX IF NOT EXISTS idx_tickets_seat_id ON tickets(seat_id)",
                "CREATE INDEX IF NOT EXISTS idx_tickets_booked ON tickets(booked)",
                "CREATE INDEX IF NOT EXISTS idx_tickets_seance_seat_booked ON tickets(seance_id, seat_id, booked)",
                "CREATE INDEX IF NOT EXISTS idx_tickets_seance_booked ON tickets(seance_id, booked)",
                
                # Индексы для таблицы seats
                "CREATE INDEX IF NOT EXISTS idx_seats_hall_id ON seats(hall_id)",
                
                # Индексы для таблицы available_seats
                "CREATE INDEX IF NOT EXISTS idx_available_seats_seance_id ON available_seats(seance_id)",
                "CREATE INDEX IF NOT EXISTS idx_available_seats_seat_id ON available_seats(seat_id)",
            ]
            
            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                    await session.commit()
                    print(f"[OK] Индекс создан: {index_sql.split('ON')[1].strip()}")
                except Exception as e:
                    print(f"[WARNING] Ошибка создания индекса: {e}")
                    await session.rollback()
            
            print("\n[OK] Все индексы добавлены!")
            break
        except Exception as e:
            print(f"[ERROR] Ошибка: {e}")
            await session.rollback()
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(add_indexes())


