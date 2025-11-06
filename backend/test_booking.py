"""
Скрипт для тестирования бронирования билетов
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(response, title=""):
    """Красивый вывод ответа"""
    print(f"\n{'='*60}")
    if title:
        print(f"[{title}]")
    print(f"Статус: {response.status_code}")
    try:
        data = response.json()
        print(f"Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Ответ: {response.text}")
        return None
    finally:
        print(f"{'='*60}")

def test_booking_flow():
    """Тестирование полного flow бронирования"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ БРОНИРОВАНИЯ БИЛЕТОВ")
    print("="*60)
    
    # Шаг 1: Получаем список сеансов
    print("\n[Шаг 1] Получаем список сеансов...")
    response = requests.get(f"{BASE_URL}/api/v1/seance")
    if response.status_code != 200:
        print(f"[ERROR] Ошибка получения сеансов: {response.status_code}")
        return False
    seances = response.json().get('seances', [])
    if not seances:
        print("[ERROR] Нет доступных сеансов для тестирования")
        return False
    
    seance = seances[0]
    seance_id = seance['id']
    print(f"[OK] Выбран сеанс ID={seance_id}, зал ID={seance.get('hall_id')}")
    
    # Шаг 2: Получаем доступные места
    print(f"\n[Шаг 2] Получаем доступные места для сеанса {seance_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/seance/{seance_id}/available-seats")
    if response.status_code != 200:
        print_response(response, "Ошибка получения доступных мест")
        return False
    
    available_data = response.json()
    available_seats = available_data.get('available_seats', [])
    total_seats = available_data.get('total_seats', 0)
    booked_seats = available_data.get('booked_seats', 0)
    
    print(f"[OK] Всего мест: {total_seats}")
    print(f"[OK] Забронировано: {booked_seats}")
    print(f"[OK] Доступно: {len(available_seats)}")
    
    if not available_seats:
        print("[ERROR] Нет доступных мест для тестирования")
        return False
    
    # Шаг 3: Бронируем первое доступное место
    test_seat = available_seats[0]
    seat_id = test_seat['id']
    print(f"\n[Шаг 3] Бронируем место ID={seat_id} (Ряд {test_seat.get('row_number')}, Место {test_seat.get('seat_number')})...")
    
    booking_data = {
        "seance_id": seance_id,
        "seat_id": seat_id,
        "user_name": "Тестовый Гость",
        "user_phone": "+79991234567",
        "user_email": f"test_{datetime.now().timestamp()}@example.com",
        "qr_code_data": f"test:booking:{datetime.now().isoformat()}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/ticket/booking",
        json=booking_data
    )
    
    if response.status_code != 200:
        print_response(response, "Ошибка бронирования")
        return False
    
    booking_result = response.json()
    print_response(response, "[OK] Бронирование успешно")
    
    booking_code = booking_result.get('booking_code')
    ticket_id = booking_result.get('id')
    print(f"[OK] Код бронирования: {booking_code}")
    print(f"[OK] ID билета: {ticket_id}")
    
    # Шаг 4: Проверяем, что место стало недоступным
    print(f"\n[Шаг 4] Проверяем, что место {seat_id} стало недоступным...")
    response = requests.get(f"{BASE_URL}/api/v1/seance/{seance_id}/available-seats")
    if response.status_code != 200:
        print("❌ Ошибка при проверке доступных мест")
        return False
    
    updated_data = response.json()
    updated_available = updated_data.get('available_seats', [])
    updated_booked = updated_data.get('booked_seats', 0)
    
    seat_still_available = any(seat['id'] == seat_id for seat in updated_available)
    
    if seat_still_available:
        print(f"[ERROR] Место {seat_id} все еще доступно!")
        return False
    
    print(f"[OK] Место {seat_id} больше не доступно")
    print(f"[OK] Теперь забронировано: {updated_booked} мест (было {booked_seats})")
    
    # Шаг 5: Пытаемся забронировать то же место еще раз
    print(f"\n[Шаг 5] Пытаемся забронировать место {seat_id} повторно...")
    response = requests.post(
        f"{BASE_URL}/api/v1/ticket/booking",
        json=booking_data
    )
    
    if response.status_code == 200:
        print("[ERROR] Удалось забронировать уже занятое место!")
        return False
    
    print(f"[OK] Правильно: получили ошибку {response.status_code}")
    error_data = response.json() if response.status_code != 200 else None
    if error_data:
        print(f"   Сообщение: {error_data.get('detail', 'N/A')}")
    
    # Шаг 6: Бронируем несколько мест подряд
    print(f"\n[Шаг 6] Бронируем несколько мест подряд...")
    seats_to_book = available_seats[1:4] if len(available_seats) >= 4 else available_seats[1:]
    
    if not seats_to_book:
        print("[WARNING] Недостаточно мест для теста множественного бронирования")
    else:
        print(f"   Бронируем {len(seats_to_book)} мест...")
        success_count = 0
        for seat in seats_to_book:
            booking_data_multi = {
                "seance_id": seance_id,
                "seat_id": seat['id'],
                "user_name": "Тестовый Гость",
                "user_phone": "+79991234567",
                "user_email": f"test_multi_{datetime.now().timestamp()}_{seat['id']}@example.com",
                "qr_code_data": f"test:booking:multi:{datetime.now().isoformat()}"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/ticket/booking",
                json=booking_data_multi
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"   [OK] Место {seat['id']} забронировано")
            else:
                print(f"   [ERROR] Ошибка бронирования места {seat['id']}: {response.status_code}")
        
        print(f"\n[OK] Успешно забронировано: {success_count} из {len(seats_to_book)} мест")
    
    print("\n" + "="*60)
    print("[OK] ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        # Проверяем доступность сервера
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("[ERROR] Сервер недоступен!")
            exit(1)
        print("[OK] Сервер доступен")
        
        # Запускаем тесты
        success = test_booking_flow()
        exit(0 if success else 1)
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Не удалось подключиться к серверу!")
        print("   Убедитесь, что backend запущен: docker-compose up -d backend")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        exit(1)

