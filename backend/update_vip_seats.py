"""
Скрипт для обновления VIP мест в существующем зале
Обновляет только центральные места в рядах 4-7 как VIP
Использование: python update_vip_seats.py [hall_id]
"""

import sys
import requests
from admin_client import AdminClient

BASE_URL = "http://localhost:8000"


def update_vip_seats(hall_id: int, vip_rows: list[int] = None):
    """
    Обновляет VIP места в зале: только центральные места в VIP рядах
    
    Args:
        hall_id: ID зала
        vip_rows: Список номеров рядов, которые должны иметь VIP места (по умолчанию ряды 4-7)
    """
    if vip_rows is None:
        vip_rows = [4, 5, 6, 7]
    
    client = AdminClient()
    
    print(f"\n[INFO] Авторизация администратора...")
    if not client.login_admin():
        print(f"[ERROR] Не удалось авторизоваться как администратор")
        return False
    print(f"[OK] Авторизация успешна")
    
    # Получаем информацию о зале
    print(f"\n[INFO] Получаем информацию о зале {hall_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/hall/{hall_id}")
    if response.status_code != 200:
        print(f"[ERROR] Не удалось получить информацию о зале")
        return False
    
    hall_data = response.json()
    seats_per_row = hall_data.get('seats_per_row', 0)
    hall_name = hall_data.get('name', f'Зал {hall_id}')
    
    print(f"[OK] Зал: {hall_name}")
    print(f"   Мест в ряду: {seats_per_row}")
    print(f"   VIP ряды: {vip_rows}")
    
    # Вычисляем центральную треть мест
    if seats_per_row > 0:
        third = seats_per_row // 3
        center_start = third + 1
        center_end = seats_per_row - third
        print(f"   Центральные места (VIP): {center_start}-{center_end}")
    else:
        print(f"[ERROR] Некорректное количество мест в ряду")
        return False
    
    # Получаем все места зала
    print(f"\n[INFO] Получаем все места зала...")
    response = requests.get(f"{BASE_URL}/api/v1/seat?hall_id={hall_id}")
    if response.status_code != 200:
        print(f"[ERROR] Не удалось получить места зала")
        return False
    
    all_seats = response.json().get('seats', [])
    print(f"   Найдено мест: {len(all_seats)}")
    
    # Обновляем места
    print(f"\n[INFO] Обновляем VIP места...")
    updated = 0
    errors = 0
    
    for seat in all_seats:
        row_num = seat['row_number']
        seat_num = seat['seat_number']
        seat_id = seat['id']
        current_type = seat.get('seat_type', 'standard')
        
        # Определяем, должно ли место быть VIP
        is_vip_row = row_num in vip_rows
        should_be_vip = False
        
        if is_vip_row:
            should_be_vip = center_start <= seat_num <= center_end
        
        # Определяем правильный тип
        correct_type = 'vip' if should_be_vip else 'standard'
        
        # Обновляем только если тип изменился
        if current_type != correct_type:
            data = {
                "seat_type": correct_type
            }
            response = client.session.patch(
                f"{BASE_URL}/api/v1/seat/{seat_id}",
                json=data,
                headers=client.get_headers()
            )
            
            if response.status_code == 200:
                updated += 1
                if updated % 10 == 0:
                    print(f"   Обновлено мест: {updated}...")
            else:
                errors += 1
                if errors <= 5:
                    print(f"   [ERROR] Ошибка обновления места {seat_id}: {response.status_code}")
    
    print(f"\n[OK] Готово!")
    print(f"   Обновлено мест: {updated}")
    print(f"   Ошибок: {errors}")
    
    # Проверяем результат
    print(f"\n[INFO] Проверяем результат...")
    response = requests.get(f"{BASE_URL}/api/v1/seat?hall_id={hall_id}")
    if response.status_code == 200:
        all_seats = response.json().get('seats', [])
        vip_count = sum(1 for seat in all_seats if seat.get('seat_type') == 'vip')
        print(f"   Всего мест: {len(all_seats)}")
        print(f"   VIP мест: {vip_count}")
        print(f"   Ожидалось VIP: {len(vip_rows) * (center_end - center_start + 1)}")
    
    return True


if __name__ == "__main__":
    hall_id = 1
    if len(sys.argv) > 1:
        try:
            hall_id = int(sys.argv[1])
        except ValueError:
            print(f"[ERROR] '{sys.argv[1]}' не является числом")
            sys.exit(1)
    
    vip_rows = None
    if len(sys.argv) > 2:
        try:
            vip_str = sys.argv[2]
            if '-' in vip_str:
                start, end = map(int, vip_str.split('-'))
                vip_rows = list(range(start, end + 1))
            else:
                vip_rows = [int(x) for x in vip_str.split(',')]
        except ValueError:
            print(f"[WARNING] Не удалось распарсить VIP ряды, используем значения по умолчанию")
    
    print(f"[START] Обновление VIP мест для зала {hall_id}")
    if vip_rows:
        print(f"   VIP ряды: {vip_rows}")
    
    success = update_vip_seats(hall_id, vip_rows)
    
    if success:
        print(f"\n[OK] Скрипт выполнен успешно!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] Скрипт завершился с ошибками")
        sys.exit(1)

