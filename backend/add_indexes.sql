-- SQL скрипт для добавления индексов для ускорения запросов
-- Выполнить в базе данных для улучшения производительности

-- Индексы для таблицы tickets (используются в запросах забронированных мест)
CREATE INDEX IF NOT EXISTS idx_tickets_seance_id ON tickets(seance_id);
CREATE INDEX IF NOT EXISTS idx_tickets_seat_id ON tickets(seat_id);
CREATE INDEX IF NOT EXISTS idx_tickets_booked ON tickets(booked);
CREATE INDEX IF NOT EXISTS idx_tickets_seance_seat_booked ON tickets(seance_id, seat_id, booked);

-- Индексы для таблицы seats (используются в запросах мест зала)
CREATE INDEX IF NOT EXISTS idx_seats_hall_id ON seats(hall_id);

-- Индексы для таблицы available_seats (используются в запросах доступных мест)
CREATE INDEX IF NOT EXISTS idx_available_seats_seance_id ON available_seats(seance_id);
CREATE INDEX IF NOT EXISTS idx_available_seats_seat_id ON available_seats(seat_id);

-- Композитный индекс для частого запроса: поиск забронированных мест по seance_id и booked
CREATE INDEX IF NOT EXISTS idx_tickets_seance_booked ON tickets(seance_id, booked);

