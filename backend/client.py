#!/usr/bin/env python3
"""
Клиент для тестирования Cinema Booking API
"""
import requests
import json
from datetime import datetime, timedelta
import time

# Базовый URL API
BASE_URL = "http://localhost:8000"

class CinemaBookingClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def print_response(self, response, title=""):
        """Красивый вывод ответа"""
        print(f"\n{'='*50}")
        if title:
            print(f"🔍 {title}")
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print(f"{'='*50}")
        
    def test_health(self):
        """Тест health check"""
        print("\n🏥 Тестируем Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_response(response, "Health Check")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def test_root(self):
        """Тест корневого эндпоинта"""
        print("\n🏠 Тестируем корневой эндпоинт...")
        try:
            response = self.session.get(f"{self.base_url}/")
            self.print_response(response, "Root Endpoint")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def register_user(self, name="Test User", phone="+1234567890", email="test@example.com", password="password123"):
        """Регистрация пользователя"""
        print(f"\n👤 Регистрируем пользователя: {email}")
        try:
            data = {
                "name": name,
                "phone": phone,
                "email": email,
                "password": password
            }
            response = self.session.post(f"{self.base_url}/api/v1/user", json=data)
            self.print_response(response, "Регистрация пользователя")
            
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get("id")
                print(f"✅ Пользователь создан с ID: {self.user_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def login(self, email="test@example.com", password="password123"):
        """Вход в систему"""
        print(f"\n🔐 Входим в систему: {email}")
        try:
            data = {
                "email": email,
                "password": password
            }
            response = self.session.post(f"{self.base_url}/api/v1/login", json=data)
            self.print_response(response, "Вход в систему")
            
            if response.status_code == 200:
                login_data = response.json()
                self.token = login_data.get("access_token")
                print(f"✅ Токен получен: {self.token[:20]}...")
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_headers(self):
        """Получить заголовки с токеном"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def create_hall(self, name="Зал 1", capacity=100):
        """Создание зала"""
        print(f"\n🏛️ Создаем зал: {name}")
        try:
            data = {
                "name": name,
                "capacity": capacity
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/hall", 
                json=data,
                headers=self.get_headers()
            )
            self.print_response(response, "Создание зала")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def create_film(self, title="Тестовый фильм", description="Описание фильма", duration=120):
        """Создание фильма"""
        print(f"\n🎬 Создаем фильм: {title}")
        try:
            data = {
                "title": title,
                "description": description,
                "duration": duration
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/film", 
                json=data,
                headers=self.get_headers()
            )
            self.print_response(response, "Создание фильма")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def create_seance(self, film_id=1, hall_id=1, start_time=None):
        """Создание сеанса"""
        if start_time is None:
            start_time = (datetime.now() + timedelta(hours=1)).isoformat()
        
        print(f"\n🎭 Создаем сеанс для фильма {film_id} в зале {hall_id}")
        try:
            data = {
                "film_id": film_id,
                "hall_id": hall_id,
                "start_time": start_time
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/seance", 
                json=data,
                headers=self.get_headers()
            )
            self.print_response(response, "Создание сеанса")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def create_seat(self, hall_id=1, row=1, number=1):
        """Создание места"""
        print(f"\n🪑 Создаем место: ряд {row}, номер {number}")
        try:
            data = {
                "hall_id": hall_id,
                "row": row,
                "number": number
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/seat", 
                json=data,
                headers=self.get_headers()
            )
            self.print_response(response, "Создание места")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def create_price(self, seance_id=1, seat_id=1, price=500):
        """Создание цены"""
        print(f"\n💰 Создаем цену: {price} руб. для сеанса {seance_id}, место {seat_id}")
        try:
            data = {
                "seance_id": seance_id,
                "seat_id": seat_id,
                "price": price
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/price", 
                json=data,
                headers=self.get_headers()
            )
            self.print_response(response, "Создание цены")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_public_films(self):
        """Получение публичного списка фильмов"""
        print(f"\n🎬 Получаем публичный список фильмов")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/films")
            self.print_response(response, "Публичный список фильмов")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_public_seances(self, film_id=1):
        """Получение публичного списка сеансов"""
        print(f"\n🎭 Получаем сеансы для фильма {film_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/film/{film_id}/seances")
            self.print_response(response, "Публичные сеансы")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_hall_seats(self, hall_id=1):
        """Получение мест в зале"""
        print(f"\n🪑 Получаем места в зале {hall_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/hall/{hall_id}/seats")
            self.print_response(response, "Места в зале")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_available_seats(self, seance_id=1):
        """Получение доступных мест для сеанса"""
        print(f"\n✅ Получаем доступные места для сеанса {seance_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/seance/{seance_id}/available-seats")
            self.print_response(response, "Доступные места")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def book_ticket_guest(self, seance_id=1, seat_id=1, guest_name="Гость", guest_phone="+1234567890"):
        """Бронирование билета гостем"""
        print(f"\n🎫 Бронируем билет для гостя: {guest_name}")
        try:
            data = {
                "seance_id": seance_id,
                "seat_id": seat_id,
                "guest_name": guest_name,
                "guest_phone": guest_phone
            }
            response = self.session.post(f"{self.base_url}/api/v1/book-ticket", json=data)
            self.print_response(response, "Бронирование билета гостем")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def get_tickets(self):
        """Получение билетов пользователя"""
        print(f"\n🎫 Получаем билеты пользователя")
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/tickets",
                headers=self.get_headers()
            )
            self.print_response(response, "Билеты пользователя")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def run_full_test(self):
        """Запуск полного теста"""
        print("🚀 Запускаем полное тестирование Cinema Booking API")
        print("="*60)
        
        # 1. Базовые тесты
        print("\n📋 Этап 1: Базовые тесты")
        self.test_health()
        self.test_root()
        
        # 2. Регистрация и вход
        print("\n📋 Этап 2: Регистрация и аутентификация")
        self.register_user()
        self.login()
        
        # 3. Создание данных
        print("\n📋 Этап 3: Создание базовых данных")
        self.create_hall()
        self.create_film()
        self.create_seance()
        self.create_seat()
        self.create_price()
        
        # 4. Публичные эндпоинты
        print("\n📋 Этап 4: Тестирование публичных эндпоинтов")
        self.get_public_films()
        self.get_public_seances()
        self.get_hall_seats()
        self.get_available_seats()
        
        # 5. Бронирование
        print("\n📋 Этап 5: Тестирование бронирования")
        self.book_ticket_guest()
        self.get_tickets()
        
        print("\n🎉 Тестирование завершено!")

def main():
    """Главная функция"""
    print("🎬 Cinema Booking API Client")
    print("="*40)
    
    client = CinemaBookingClient()
    
    # Проверяем, что сервер запущен
    print("🔍 Проверяем доступность сервера...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен!")
        else:
            print("❌ Сервер недоступен!")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("💡 Убедитесь, что сервер запущен: docker-compose up -d")
        return
    
    # Запускаем тесты
    client.run_full_test()

if __name__ == "__main__":
    main()

