#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных: фильмы, залы, сеансы
Использование: python create_test_data.py
"""
import sys
import os
import requests
from datetime import datetime, timedelta
from admin_client import AdminClient

# Определяем BASE_URL: внутри Docker используем имя сервиса, снаружи - localhost
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
# Если запускаемся внутри Docker контейнера, используем внутренний адрес
if os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER'):
    BASE_URL = 'http://backend:80'  # Внутренний адрес backend контейнера


def create_test_data():
    """Создание тестовых данных"""
    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ ДЛЯ CINEMA BOOKING")
    print("=" * 60)
    
    client = AdminClient()
    
    # Авторизуемся как администратор
    print("\n[1/5] Авторизация администратора...")
    if not client.login_admin():
        print("[ERROR] Не удалось авторизоваться как администратор")
        print("   Проверьте, что админ существует и backend запущен")
        return False
    print("[OK] Авторизация успешна")
    
    # Проверяем существующие данные
    print("\n[2/5] Проверка существующих данных...")
    halls_response = requests.get(f"{BASE_URL}/api/v1/hall")
    films_response = requests.get(f"{BASE_URL}/api/v1/film")
    
    halls = halls_response.json().get('halls', []) if halls_response.status_code == 200 else []
    films = films_response.json().get('films', []) if films_response.status_code == 200 else []
    
    print(f"[INFO] Найдено залов: {len(halls)}")
    print(f"[INFO] Найдено фильмов: {len(films)}")
    
    # Создаем зал, если нет
    if not halls:
        print("\n[3/5] Создание тестового зала...")
        hall_data = {
            "name": "Зал 1",
            "rows": 10,
            "seats_per_row": 15,
            "is_active": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/hall",
            json=hall_data,
            headers={"x-token": client.token}
        )
        if response.status_code == 200:
            hall = response.json()
            halls.append(hall)
            print(f"[OK] Создан зал: {hall['name']} (ID: {hall['id']})")
            print(f"[INFO] Не забудьте сгенерировать места: python generate_seats.py {hall['id']}")
        else:
            print(f"[ERROR] Ошибка создания зала: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
    else:
        print(f"[OK] Используем существующий зал: {halls[0]['name']} (ID: {halls[0]['id']})")
    
    hall_id = halls[0]['id']
    
    # Создаем фильмы, если нет
    test_films = [
        {
            "title": "Интерстеллар",
            "description": "Фантастический фильм о путешествии через червоточину в поисках нового дома для человечества.",
            "duration": 169,
            "poster_url": "https://example.com/interstellar.jpg"
        },
        {
            "title": "Начало",
            "description": "Фильм о проникновении в сны для кражи идей.",
            "duration": 148,
            "poster_url": "https://example.com/inception.jpg"
        },
        {
            "title": "Матрица",
            "description": "Классический научно-фантастический фильм о реальности и иллюзии.",
            "duration": 136,
            "poster_url": "https://example.com/matrix.jpg"
        }
    ]
    
    print("\n[4/5] Создание тестовых фильмов...")
    created_films = []
    for film_data in test_films:
        # Проверяем, существует ли фильм
        existing = [f for f in films if f.get('title') == film_data['title']]
        if existing:
            print(f"[SKIP] Фильм '{film_data['title']}' уже существует")
            created_films.append(existing[0])
            continue
        
        response = requests.post(
            f"{BASE_URL}/api/v1/film",
            json=film_data,
            headers={"x-token": client.token}
        )
        if response.status_code == 200:
            film = response.json()
            created_films.append(film)
            film_title = film.get('title', film_data['title'])
            film_id = film.get('id', '?')
            print(f"[OK] Создан фильм: {film_title} (ID: {film_id})")
        else:
            print(f"[WARNING] Ошибка создания фильма '{film_data['title']}': {response.status_code}")
            if response.status_code != 409:  # 409 - уже существует
                print(f"   Ответ: {response.text[:200]}")
    
    if not created_films:
        # Используем существующие фильмы
        created_films = films[:3] if len(films) >= 3 else films
    
    if not created_films:
        print("[ERROR] Нет фильмов для создания сеансов")
        return False
    
    # Создаем сеансы на сегодня и завтра
    print("\n[5/5] Создание тестовых сеансов...")
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Времена сеансов
    seance_times = [
        (10, 0),   # 10:00
        (13, 30),  # 13:30
        (17, 0),   # 17:00
        (20, 30),  # 20:30
    ]
    
    created_seances = []
    for date in [today, tomorrow]:
        date_str = date.strftime("%Y-%m-%d")
        print(f"\n  Создание сеансов на {date_str}...")
        
        for film in created_films:
            film_id = film.get('id') if isinstance(film, dict) else film.id if hasattr(film, 'id') else None
            film_title = film.get('title', 'Фильм') if isinstance(film, dict) else getattr(film, 'title', 'Фильм')
            
            if not film_id:
                print(f"    [SKIP] Пропускаем фильм без ID: {film_title}")
                continue
            
            for hour, minute in seance_times:
                seance_time = date.replace(hour=hour, minute=minute)
                
                # Проверяем, не в прошлом ли время
                if seance_time < now:
                    continue
                
                seance_data = {
                    "film_id": film_id,
                    "hall_id": hall_id,
                    "start_time": seance_time.isoformat(),
                    "price_standard": 500.0,
                    "price_vip": 800.0
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/seance",
                    json=seance_data,
                    headers={"x-token": client.token}
                )
                
                if response.status_code == 200:
                    seance = response.json()
                    created_seances.append(seance)
                    time_str = seance_time.strftime("%H:%M")
                    seance_id = seance.get('id', '?')
                    print(f"    [OK] {time_str} - {film_title} (ID: {seance_id})")
                else:
                    time_str = seance_time.strftime("%H:%M")
                    print(f"    [WARNING] Ошибка создания сеанса {time_str} - {film_title}: {response.status_code}")
                    if response.status_code != 409:  # 409 - уже существует
                        print(f"       Ответ: {response.text[:100]}")
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ СОЗДАНИЯ ТЕСТОВЫХ ДАННЫХ")
    print("=" * 60)
    print(f"Залов: {len(halls)}")
    print(f"Фильмов: {len(created_films)}")
    print(f"Сеансов создано: {len(created_seances)}")
    print("\n[OK] Тестовые данные готовы!")
    print(f"\n[INFO] Для генерации мест в зале выполните:")
    print(f"   docker-compose exec backend python generate_seats.py {hall_id}")
    print("\n[INFO] Теперь можно тестировать бронирование на главной странице!")
    
    return True


if __name__ == "__main__":
    try:
        success = create_test_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

