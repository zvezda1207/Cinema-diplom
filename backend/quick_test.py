#!/usr/bin/env python3
"""
Быстрый тест для проверки основных функций API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """Тест базовых эндпоинтов"""
    print("Тестируем базовые эндпоинты...")
    
    # Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"[OK] Health: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Health: {e}")
    
    # Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"[OK] Root: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Root: {e}")

def test_public_endpoints():
    """Тест публичных эндпоинтов"""
    print("\n🎬 Тестируем публичные эндпоинты...")
    
    # Публичные фильмы
    try:
        response = requests.get(f"{BASE_URL}/api/v1/films")
        print(f"✅ Публичные фильмы: {response.status_code}")
        if response.status_code == 200:
            films = response.json()
            print(f"   Найдено фильмов: {len(films.get('films', []))}")
    except Exception as e:
        print(f"❌ Публичные фильмы: {e}")

def test_user_registration():
    """Тест регистрации пользователя"""
    print("\n👤 Тестируем регистрацию пользователя...")
    
    user_data = {
        "name": "Тестовый пользователь",
        "phone": "+1234567890",
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/user", json=user_data)
        print(f"✅ Регистрация: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"   Пользователь создан с ID: {user.get('id')}")
        else:
            print(f"   Ошибка: {response.json()}")
    except Exception as e:
        print(f"❌ Регистрация: {e}")

def test_login():
    """Тест входа в систему"""
    print("\n🔐 Тестируем вход в систему...")
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/login", json=login_data)
        print(f"✅ Вход: {response.status_code}")
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            print(f"   Токен получен: {token[:20] if token else 'None'}...")
            return token
        else:
            print(f"   Ошибка: {response.json()}")
    except Exception as e:
        print(f"❌ Вход: {e}")
    
    return None

def test_authenticated_endpoints(token):
    """Тест аутентифицированных эндпоинтов"""
    if not token:
        print("\n❌ Нет токена для тестирования аутентифицированных эндпоинтов")
        return
    
    print(f"\n🔒 Тестируем аутентифицированные эндпоинты...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создание зала
    try:
        hall_data = {
            "name": "Тестовый зал",
            "capacity": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/hall", json=hall_data, headers=headers)
        print(f"✅ Создание зала: {response.status_code}")
        if response.status_code == 200:
            hall = response.json()
            print(f"   Зал создан с ID: {hall.get('id')}")
    except Exception as e:
        print(f"❌ Создание зала: {e}")
    
    # Создание фильма
    try:
        film_data = {
            "title": "Тестовый фильм",
            "description": "Описание тестового фильма",
            "duration": 120
        }
        response = requests.post(f"{BASE_URL}/api/v1/film", json=film_data, headers=headers)
        print(f"✅ Создание фильма: {response.status_code}")
        if response.status_code == 200:
            film = response.json()
            print(f"   Фильм создан с ID: {film.get('id')}")
    except Exception as e:
        print(f"❌ Создание фильма: {e}")

def main():
    """Главная функция быстрого теста"""
    print("Быстрый тест Cinema Booking API")
    print("="*50)
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Сервер недоступен!")
            return
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        print("💡 Запустите сервер: docker-compose up -d")
        return
    
    print("✅ Сервер доступен!")
    
    # Запускаем тесты
    test_basic_endpoints()
    test_public_endpoints()
    test_user_registration()
    token = test_login()
    test_authenticated_endpoints(token)
    
    print("\n🎉 Быстрый тест завершен!")

if __name__ == "__main__":
    main()
