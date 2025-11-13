#!/usr/bin/env python3
"""
Скрипт для создания администратора напрямую в БД
Использование: python create_admin.py
"""
import asyncio
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Session, User
from app.auth import hash_password
from sqlalchemy import select


async def create_admin():
    """Создание администратора в БД"""
    print("=" * 50)
    print("Создание администратора для Cinema Booking API")
    print("=" * 50)
    
    async with Session() as session:
        # Проверяем, существует ли уже администратор
        query = select(User).where(User.email == "admin@example.com")
        result = await session.execute(query)
        existing_admin = result.scalars().first()
        
        if existing_admin:
            print(f"\n[INFO] Администратор уже существует!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Имя: {existing_admin.name}")
            print(f"   Роль: {existing_admin.role}")
            print(f"\n[OK] Используйте эти данные для входа:")
            print(f"   Email: admin@example.com")
            print(f"   Пароль: admin123")
            return True
        
        # Создаем нового администратора
        print("\n[INFO] Создаем нового администратора...")
        admin = User(
            name="Администратор",
            phone="+1234567890",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        
        session.add(admin)
        try:
            await session.commit()
            await session.refresh(admin)
            print(f"[OK] Администратор успешно создан!")
            print(f"\n[OK] Данные для входа:")
            print(f"   Email: admin@example.com")
            print(f"   Пароль: admin123")
            print(f"\n[INFO] ID администратора: {admin.id}")
            return True
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Ошибка создания администратора: {e}")
            return False


async def main():
    try:
        await create_admin()
    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

