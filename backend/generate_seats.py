"""
Скрипт для генерации всех мест в зале
Использование: python generate_seats.py [hall_id]
"""

import sys
import requests
from admin_client import AdminClient

BASE_URL = "http://localhost:8000"


def generate_seats_for_hall(hall_id: int, vip_rows: list[int] = None):
    """
    Генерирует все места для зала на основе его rows и seats_per_row
    
    Args:
        hall_id: ID зала
        vip_rows: Список номеров рядов, которые должны быть VIP (по умолчанию ряды 4-7)
    """
    if vip_rows is None:
        # По умолчанию VIP места в центральных рядах (4-7)
        vip_rows = [4, 5, 6, 7]
    
    client = AdminClient()
    
    # Авторизуемся как администратор
    print(f"\n[INFO] Авторизация администратора...")
    if not client.login_admin():
        print(f"[ERROR] Не удалось авторизоваться как администратор")
        print(f"   Проверьте, что админ существует и backend запущен")
        return False
    print(f"[OK] Авторизация успешна")
    
    # Получаем информацию о зале
    print(f"\n[INFO] Получаем информацию о зале {hall_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/hall/{hall_id}")
    if response.status_code != 200:
        print(f"[ERROR] Не удалось получить информацию о зале")
        print(f"   Ответ: {response.text}")
        return False
    
    hall_data = response.json()
    rows = hall_data.get('rows', 0)
    seats_per_row = hall_data.get('seats_per_row', 0)
    hall_name = hall_data.get('name', f'Зал {hall_id}')
    
    print(f"[OK] Зал: {hall_name}")
    print(f"   Рядов: {rows}")
    print(f"   Мест в ряду: {seats_per_row}")
    print(f"   Всего мест: {rows * seats_per_row}")
    print(f"   VIP ряды: {vip_rows}")
    
    # Проверяем, есть ли уже места в зале
    print(f"\n[INFO] Проверяем существующие места...")
    response = requests.get(f"{BASE_URL}/api/v1/seat?hall_id={hall_id}")
    if response.status_code == 200:
        existing_seats = response.json().get('seats', [])
        print(f"   Найдено существующих мест: {len(existing_seats)}")
        
        if len(existing_seats) > 0:
            print(f"\n[INFO] В зале уже есть {len(existing_seats)} мест")
            print(f"   Будем создавать только отсутствующие места (существующие будут пропущены)")
    
    # Генерируем места
    print(f"\n[INFO] Создаем места...")
    created = 0
    skipped = 0
    errors = 0
    
    # Создаем Set существующих мест для быстрой проверки
    existing_seats_set = set()
    for seat in existing_seats:
        key = (seat['row_number'], seat['seat_number'])
        existing_seats_set.add(key)
    
    for row_num in range(1, rows + 1):
        is_vip_row = row_num in vip_rows
        
        # Вычисляем центральную треть мест для VIP рядов
        center_start = 0
        center_end = 0
        if is_vip_row and seats_per_row > 0:
            third = seats_per_row // 3
            center_start = third + 1
            center_end = seats_per_row - third
        
        for seat_num in range(1, seats_per_row + 1):
            # Пропускаем, если место уже существует
            if (row_num, seat_num) in existing_seats_set:
                skipped += 1
                continue
            
            # VIP места: только центральные места в VIP рядах
            if is_vip_row and center_start > 0 and center_end > 0:
                seat_type = 'vip' if (center_start <= seat_num <= center_end) else 'standard'
            else:
                seat_type = 'standard'
            
            # Пытаемся создать место (без вывода деталей)
            data = {
                "hall_id": hall_id,
                "row_number": row_num,
                "seat_number": seat_num,
                "seat_type": seat_type
            }
            response = client.session.post(
                f"{BASE_URL}/api/v1/seat",
                json=data,
                headers=client.get_headers()
            )
            
            if response.status_code == 200:
                created += 1
                if created % 20 == 0:
                    print(f"   Создано мест: {created}...")
            else:
                # Ошибка при создании
                errors += 1
                if errors <= 5:
                    print(f"   [ERROR] Ошибка создания места: ряд {row_num}, место {seat_num} - {response.status_code}")
    
    print(f"\n[OK] Готово!")
    print(f"   Создано новых мест: {created}")
    print(f"   Пропущено: {skipped}")
    print(f"   Ошибок: {errors}")
    
    # Проверяем результат
    print(f"\n[INFO] Проверяем результат...")
    response = requests.get(f"{BASE_URL}/api/v1/seat?hall_id={hall_id}")
    if response.status_code == 200:
        all_seats = response.json().get('seats', [])
        print(f"   Всего мест в зале: {len(all_seats)}")
        print(f"   Ожидалось: {rows * seats_per_row}")
        
        if len(all_seats) == rows * seats_per_row:
            print(f"   [OK] Все места созданы успешно!")
        else:
            print(f"   [WARNING] Количество мест не совпадает")
    
    return True


if __name__ == "__main__":
    # Получаем hall_id из аргументов командной строки или используем 1 по умолчанию
    hall_id = 1
    if len(sys.argv) > 1:
        try:
            hall_id = int(sys.argv[1])
        except ValueError:
            print(f"[ERROR] '{sys.argv[1]}' не является числом")
            sys.exit(1)
    
    # Можно указать VIP ряды через аргументы
    vip_rows = None
    if len(sys.argv) > 2:
        try:
            # Формат: "5,6,7,8" или "5-8"
            vip_str = sys.argv[2]
            if '-' in vip_str:
                # Диапазон: "5-8"
                start, end = map(int, vip_str.split('-'))
                vip_rows = list(range(start, end + 1))
            else:
                # Список: "5,6,7,8"
                vip_rows = [int(x) for x in vip_str.split(',')]
        except ValueError:
            print(f"[WARNING] Не удалось распарсить VIP ряды: '{sys.argv[2]}', используем значения по умолчанию")
    
    print(f"[START] Генерация мест для зала {hall_id}")
    if vip_rows:
        print(f"   VIP ряды: {vip_rows}")
    
    success = generate_seats_for_hall(hall_id, vip_rows)
    
    if success:
        print(f"\n[OK] Скрипт выполнен успешно!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] Скрипт завершился с ошибками")
        sys.exit(1)

