#!/usr/bin/env python3
"""
Простой клиент для тестирования Cinema Booking API
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
            print(f"🔍 {title}")
        print(f"📊 Статус: {response.status_code}")
        try:
            print(f"📝 Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"📝 Ответ: {response.text}")
        print(f"{'='*50}")
        
    def get_headers(self):
        """Получить заголовки с токеном"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def register_user(self, name="Тестовый пользователь", phone="+1234567890", email="test@example.com", password="password123"):
        """Регистрация пользователя"""
        print(f"\n👤 Регистрируем пользователя: {email}")
        data = {
            "name": name,
            "phone": phone,
            "email": email,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/api/v1/user", json=data)
        self.print_response(response, "Регистрация пользователя")
        return response.status_code == 200
    
    def login(self, email="test@example.com", password="password123"):
        """Вход в систему"""
        print(f"\n🔐 Входим в систему: {email}")
        data = {
            "email": email,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/api/v1/user/login", json=data)
        self.print_response(response, "Вход в систему")
        
        if response.status_code == 200:
            login_data = response.json()
            self.token = login_data.get("access_token")
            print(f"✅ Токен получен: {self.token[:20] if self.token else 'None'}...")
            return True
        return False
    
    def create_hall(self, name="Зал 1", capacity=100):
        """Создание зала"""
        print(f"\n🏛️ Создаем зал: {name}")
        data = {
            "name": name,
            "capacity": capacity
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/hall", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание зала")
        return response.status_code == 200
    
    def create_film(self, title="Тестовый фильм", description="Описание фильма", duration=120):
        """Создание фильма"""
        print(f"\n🎬 Создаем фильм: {title}")
        data = {
            "title": title,
            "description": description,
            "duration": duration
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/film", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание фильма")
        return response.status_code == 200
    
    def create_seance(self, film_id=1, hall_id=1, start_time=None):
        """Создание сеанса"""
        if start_time is None:
            start_time = (datetime.now() + timedelta(hours=1)).isoformat()
        
        print(f"\n🎭 Создаем сеанс для фильма {film_id} в зале {hall_id}")
        data = {
            "film_id": film_id,
            "hall_id": hall_id,
            "start_time": start_time
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/seance", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание сеанса")
        return response.status_code == 200
    
    def create_seat(self, hall_id=1, row=1, number=1):
        """Создание места"""
        print(f"\n🪑 Создаем место: ряд {row}, номер {number}")
        data = {
            "hall_id": hall_id,
            "row": row,
            "number": number
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/seat", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание места")
        return response.status_code == 200
    
    def create_price(self, seance_id=1, seat_id=1, price=500):
        """Создание цены"""
        print(f"\n💰 Создаем цену: {price} руб. для сеанса {seance_id}, место {seat_id}")
        data = {
            "seance_id": seance_id,
            "seat_id": seat_id,
            "price": price
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/price", 
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Создание цены")
        return response.status_code == 200
    
    def get_films(self):
        """Получение списка фильмов"""
        print(f"\n🎬 Получаем список фильмов")
        response = self.session.get(f"{BASE_URL}/api/v1/film")
        self.print_response(response, "Список фильмов")
        return response.status_code == 200
    
    def get_halls(self):
        """Получение списка залов"""
        print(f"\n🏛️ Получаем список залов")
        response = self.session.get(
            f"{BASE_URL}/api/v1/hall",
            headers=self.get_headers()
        )
        self.print_response(response, "Список залов")
        return response.status_code == 200
    
    def get_seances(self):
        """Получение списка сеансов"""
        print(f"\n🎭 Получаем список сеансов")
        response = self.session.get(
            f"{BASE_URL}/api/v1/seance",
            headers=self.get_headers()
        )
        self.print_response(response, "Список сеансов")
        return response.status_code == 200
    
    def book_ticket(self, seance_id=1, seat_id=1, user_name="Пользователь", user_phone="+1234567890", user_email="user@example.com"):
        """Бронирование билета"""
        print(f"\n🎫 Бронируем билет для сеанса {seance_id}, место {seat_id}")
        data = {
            "seance_id": seance_id,
            "seat_id": seat_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "user_email": user_email
        }
        response = self.session.post(
            f"{BASE_URL}/api/v1/ticket/booking",
            json=data,
            headers=self.get_headers()
        )
        self.print_response(response, "Бронирование билета")
        return response.status_code == 200
    
    def get_tickets(self):
        """Получение билетов пользователя"""
        print(f"\n🎫 Получаем билеты пользователя")
        response = self.session.get(
            f"{BASE_URL}/api/v1/ticket",
            headers=self.get_headers()
        )
        self.print_response(response, "Билеты пользователя")
        return response.status_code == 200
    
    def run_demo(self):
        """Запуск демонстрации"""
        print("🎬 Демонстрация Cinema Booking API")
        print("="*50)
        
        # 1. Регистрация и вход
        print("\n📋 Шаг 1: Регистрация и вход")
        self.register_user()
        self.login()
        
        if not self.token:
            print("❌ Не удалось получить токен. Останавливаем демонстрацию.")
            return
        
        # 2. Создание зала
        print("\n📋 Шаг 2: Создание зала")
        self.create_hall("Большой зал", 150)
        
        # 3. Создание фильма
        print("\n📋 Шаг 3: Создание фильма")
        self.create_film("Интерстеллар", "Фантастический фильм о космосе", 169)
        
        # 4. Создание места
        print("\n📋 Шаг 4: Создание места")
        self.create_seat(1, 1, 1)  # Зал 1, ряд 1, место 1
        
        # 5. Создание сеанса
        print("\n📋 Шаг 5: Создание сеанса")
        self.create_seance(1, 1)  # Фильм 1, Зал 1
        
        # 6. Создание цены
        print("\n📋 Шаг 6: Создание цены")
        self.create_price(1, 1, 500)  # Сеанс 1, Место 1, 500 руб
        
        # 7. Просмотр данных
        print("\n📋 Шаг 7: Просмотр созданных данных")
        self.get_films()
        self.get_halls()
        self.get_seances()
        
        # 8. Бронирование билета
        print("\n📋 Шаг 8: Бронирование билета")
        self.book_ticket(1, 1, "Иван Иванов", "+7-123-456-7890", "ivan@example.com")
        
        # 9. Просмотр билетов
        print("\n📋 Шаг 9: Просмотр билетов")
        self.get_tickets()
        
        print("\n🎉 Демонстрация завершена!")

def main():
    """Главная функция"""
    print("🎬 Cinema Booking API - Простой клиент")
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
    
    # Запускаем демонстрацию
    client = CinemaClient()
    client.run_demo()

if __name__ == "__main__":
    main()

