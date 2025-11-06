#!/usr/bin/env python3
"""
Клиент для тестирования гостевых функций
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class GuestClient:
    def __init__(self):
        self.session = requests.Session()
        
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
    
    def get_films(self):
        """Просмотр списка фильмов (публичный)"""
        print(f"\nПолучаем список фильмов")
        response = self.session.get(f"{BASE_URL}/api/v1/public/films")
        self.print_response(response, "Список фильмов")
        return response.status_code == 200
    
    def get_seances(self):
        """Просмотр расписания сеансов"""
        print(f"\nПолучаем расписание сеансов")
        response = self.session.get(f"{BASE_URL}/api/v1/public/seances")
        self.print_response(response, "Расписание сеансов")
        return response.status_code == 200
    
    def get_available_seats(self, seance_id=1):
        """Выбор места в кинозале"""
        print(f"\nПолучаем доступные места для сеанса {seance_id}")
        response = self.session.get(f"{BASE_URL}/api/v1/public/seance/{seance_id}/available-seats")
        self.print_response(response, "Доступные места")
        return response.status_code == 200
    
    def book_ticket(self, seance_id=1, seat_id=1, user_name="Гость", user_phone="+1234567890", user_email="guest@example.com", qr_code_data="BOOKING_123456"):
        """Бронирование билета гостем"""
        print(f"\nБронируем билет для сеанса {seance_id}, место {seat_id}")
        data = {
            "seance_id": seance_id,
            "seat_id": seat_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "user_email": user_email,
            "qr_code_data": qr_code_data
        }
        response = self.session.post(f"{BASE_URL}/api/v1/ticket/booking", json=data)
        self.print_response(response, "Бронирование билета")
        return response.status_code == 200
    
    def test_guest_features(self):
        """Тест гостевых функций"""
        print("Тестируем возможности гостя")
        print("="*50)
        
        # 1. Просмотр списка фильмов
        print("\nШаг 1: Просмотр списка фильмов")
        self.get_films()
        
        # 2. Просмотр расписания
        print("\nШаг 2: Просмотр расписания")
        self.get_seances()
        
        # 3. Выбор места в кинозале
        print("\nШаг 3: Выбор места в кинозале")
        self.get_available_seats(1)
        
        # 4. Бронирование билета
        print("\nШаг 4: Бронирование билета")
        self.book_ticket(1, 1, "Иван Гость", "+7-123-456-7890", "ivan@example.com")
        
        print("\nТестирование гостевых функций завершено!")

def main():
    """Главная функция"""
    print("Cinema Booking API - Гостевой клиент")
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
    
    # Запускаем тестирование
    client = GuestClient()
    client.test_guest_features()

if __name__ == "__main__":
    main()
