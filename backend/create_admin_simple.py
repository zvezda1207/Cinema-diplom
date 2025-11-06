#!/usr/bin/env python3
"""
Скрипт для создания администратора
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_admin():
    """Создание администратора"""
    print("Создаем администратора...")
    data = {
        "name": "Администратор",
        "phone": "+1234567890",
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/user", json=data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200:
        print("Администратор создан!")
        return True
    elif response.status_code == 409:
        print("Администратор уже существует")
        return True
    else:
        print("Ошибка создания администратора")
        return False

def login_admin():
    """Вход администратора"""
    print("\nВходим как администратор...")
    data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/user/login", json=data)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Токен администратора: {token[:20]}...")
        return token
    else:
        print("Ошибка входа администратора")
        return None

def main():
    print("Создание администратора для Cinema Booking API")
    print("="*50)
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Сервер недоступен!")
            return
    except Exception as e:
        print(f"Сервер недоступен: {e}")
        return
    
    print("Сервер доступен!")
    
    # Создаем администратора
    if create_admin():
        # Входим как администратор
        token = login_admin()
        if token:
            print(f"\nАдминистратор готов к работе!")
            print(f"Токен: {token}")
        else:
            print("\nНе удалось войти как администратор")
    else:
        print("\nНе удалось создать администратора")

if __name__ == "__main__":
    main()

