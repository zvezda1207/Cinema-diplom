#!/usr/bin/env python3
"""
Финальный клиент для тестирования Cinema Booking API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class CinemaClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def print_response(self, response, title=""):
        """Красивый вывод ответа"""
        print(f"\n{'='*50}")
        if title:
            print(f"[{title}]")
        print(f"Статус: {response.status_code}")
        try:
            print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Ответ: {response.text}")
        print(f"{'='*50}")
        
    def get_headers(self):
        """Получить заголовки с токеном"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def login(self, email="test@example.com", password="password123"):
        """Вход в систему"""
        print(f"\nВходим в систему: {email}")
        data = {
            "email": email,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/api/v1/user/login", json=data)
        self.print_response(response, "Вход в систему")
        
        if response.status_code == 200:
            login_data = response.json()
            self.token = login_data.get("token")
            print(f"Токен получен: {self.token[:20] if self.token else 'None'}...")
            return True
        return False
    
    def get_films(self):
        """Получение списка фильмов"""
        print(f"\nПолучаем список фильмов")
        response = self.session.get(f"{BASE_URL}/api/v1/film")
        self.print_response(response, "Список фильмов")
        return response.status_code == 200
    
    def get_halls(self):
        """Получение списка залов"""
        print(f"\nПолучаем список залов")
        response = self.session.get(
            f"{BASE_URL}/api/v1/hall",
            headers=self.get_headers()
        )
        self.print_response(response, "Список залов")
        return response.status_code == 200
    
    def get_seances(self):
        """Получение списка сеансов"""
        print(f"\nПолучаем список сеансов")
        response = self.session.get(
            f"{BASE_URL}/api/v1/seance",
            headers=self.get_headers()
        )
        self.print_response(response, "Список сеансов")
        return response.status_code == 200
    
    def get_tickets(self):
        """Получение билетов пользователя"""
        print(f"\nПолучаем билеты пользователя")
        response = self.session.get(
            f"{BASE_URL}/api/v1/ticket",
            headers=self.get_headers()
        )
        self.print_response(response, "Билеты пользователя")
        return response.status_code == 200
    
    def test_basic_functions(self):
        """Тест базовых функций"""
        print("Тестируем базовые функции API")
        print("="*50)
        
        # 1. Вход в систему
        print("\nШаг 1: Вход в систему")
        if not self.login():
            print("Не удалось войти в систему")
            return
        
        # 2. Получение данных
        print("\nШаг 2: Получение данных")
        self.get_films()
        self.get_halls()
        self.get_seances()
        self.get_tickets()
        
        print("\nТестирование завершено!")

def main():
    """Главная функция"""
    print("Cinema Booking API - Финальный клиент")
    print("="*50)
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Сервер недоступен!")
            return
    except Exception as e:
        print(f"Сервер недоступен: {e}")
        print("Запустите сервер: docker-compose up -d")
        return
    
    print("Сервер доступен!")
    
    # Запускаем тестирование
    client = CinemaClient()
    client.test_basic_functions()

if __name__ == "__main__":
    main()

