#!/usr/bin/env python3
"""
Клиент для тестирования административных функций
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class AdminClient:
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
            return {"x-token": str(self.token)}
        return {}
    
    def login_admin(self, email="admin@example.com", password="admin123"):
        """Вход как администратор"""
        print(f"\nВходим как администратор: {email}")
        data = {
            "email": email,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/api/v1/user/login", json=data)
        self.print_response(response, "Вход администратора")
        
        if response.status_code == 200:
            login_data = response.json()
            self.token = login_data.get("token")
            print(f"Токен получен: {self.token[:20] if self.token else 'None'}...")
            return True
        return False
    
    def create_hall(self, name="Админский зал", rows=12, seats_per_row=15):
        """Создание зала администратором"""
        print(f"\nСоздаем зал: {name}")
        data = {
            "name": name,
            "rows": rows,
            "seats_per_row": seats_per_row
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/hall", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание зала")
        return response.status_code == 200
    
    def create_film(self, title="Админский фильм", description="Фильм созданный администратором", duration=120, poster_url="https://example.com/admin.jpg"):
        """Создание фильма администратором"""
        print(f"\nСоздаем фильм: {title}")
        data = {
            "title": title,
            "description": description,
            "duration": duration,
            "poster_url": poster_url
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/film", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание фильма")
        return response.status_code == 200
    
    def create_seat(self, hall_id=1, row_number=1, seat_number=1, seat_type="standard"):
        """Создание места администратором"""
        print(f"\nСоздаем место: ряд {row_number}, номер {seat_number}")
        data = {
            "hall_id": hall_id,
            "row_number": row_number,
            "seat_number": seat_number,
            "seat_type": seat_type
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/seat", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание места")
        return response.status_code == 200
    
    def create_seance(self, film_id=1, hall_id=1, start_time=None, price_standard=500.0, price_vip=800.0):
        """Создание сеанса администратором"""
        if start_time is None:
            start_time = (datetime.now() + timedelta(hours=1)).isoformat()
        
        print(f"\nСоздаем сеанс для фильма {film_id} в зале {hall_id}")
        data = {
            "film_id": film_id,
            "hall_id": hall_id,
            "start_time": start_time,
            "price_standard": price_standard,
            "price_vip": price_vip
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/seance", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание сеанса")
        return response.status_code == 200
    
    def create_price(self, seance_id=1, seat_id=1, seat_type="standard", price=500):
        """Создание цены администратором"""
        print(f"\nСоздаем цену: {price} руб. для сеанса {seance_id}, место {seat_id}")
        data = {
            "seance_id": seance_id,
            "seat_id": seat_id,
            "seat_type": seat_type,
            "price": price
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/price", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание цены")
        return response.status_code == 200
    
    def get_bookings(self):
        """Получение броней администратором"""
        print(f"\nПолучаем все брони")
        response = self.session.get(
            f"{BASE_URL}/api/v1/tickets",
            headers=self.get_headers()
        )
        self.print_response(response, "Все брони")
        return response.status_code == 200
    
    def test_admin_features(self):
        """Тест административных функций"""
        print("Тестируем возможности администратора")
        print("="*50)
        
        # 1. Вход как администратор
        print("\nШаг 1: Вход как администратор")
        if not self.login_admin():
            print("Не удалось войти как администратор")
            return
        
        # 2. Создание зала
        print("\nШаг 2: Создание зала")
        self.create_hall("Админский зал", 10, 15)
        
        # 3. Создание фильма
        print("\nШаг 3: Создание фильма")
        self.create_film("Админский фильм", "Фильм созданный администратором", 120)
        
        # 4. Создание места
        print("\nШаг 4: Создание места")
        self.create_seat(1, 1, 1, "standard")
        
        # 5. Создание сеанса
        print("\nШаг 5: Создание сеанса")
        self.create_seance(1, 1, price_standard=500.0, price_vip=800.0)
        
        # 6. Создание цены
        print("\nШаг 6: Создание цены")
        self.create_price(1, 1, "standard", 500)
        
        # 7. Просмотр броней
        print("\nШаг 7: Просмотр броней")
        self.get_bookings()
        
        print("\nТестирование административных функций завершено!")

def main():
    """Главная функция"""
    print("Cinema Booking API - Административный клиент")
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
    client = AdminClient()
    client.test_admin_features()

if __name__ == "__main__":
    main()

