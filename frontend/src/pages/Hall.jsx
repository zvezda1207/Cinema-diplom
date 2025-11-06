import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import './Hall.css'

function Hall() {
    const { seanceId } = useParams()
    const navigate = useNavigate()
    const [seance, setSeance] = useState(null)
    const [hall, setHall] = useState(null) // Информация о зале (rows, seats_per_row)
    const [allSeats, setAllSeats] = useState([]) // Все места зала из базы
    const [availableSeatIds, setAvailableSeatIds] = useState([]) // ID доступных мест (массив для хранения в state)
    const [bookedSeatIds, setBookedSeatIds] = useState([]) // Локально отмеченные как забронированные
    const [selectedSeats, setSelectedSeats] = useState([])
    const [isBooking, setIsBooking] = useState(false)
    const [loading, setLoading] = useState(true)
    const [bookingMessage, setBookingMessage] = useState(null) // Сообщение о результате бронирования
    const isLoadingDataRef = useRef(false) // Защита от множественных вызовов

    const loadSeanceData = useCallback(async () => {
        // Защита от множественных одновременных вызовов
        if (isLoadingDataRef.current) {
            console.log('[Hall] loadSeanceData уже выполняется, пропускаем')
            return
        }

        isLoadingDataRef.current = true
        setLoading(true)
        try {
            // Уменьшаем логирование для производительности
            // console.log('[Hall] Начинаем загрузку данных для seanceId:', seanceId)

            // Загружаем данные сеанса
            const seanceData = await api.getSeance(seanceId)
            // console.log('[Hall] Данные сеанса загружены:', seanceData)
            setSeance(seanceData)

            if (!seanceData || !seanceData.hall_id) {
                console.error('[Hall] Ошибка: сеанс не содержит hall_id')
                return
            }

            // Загружаем информацию о зале, места зала и доступные места параллельно
            // console.log('[Hall] Загружаем данные зала, места и доступные места...')
            const [hallData, allSeatsData, availableSeatsData] = await Promise.all([
                api.getHall(seanceData.hall_id),
                api.getSeats({ hall_id: seanceData.hall_id }),
                api.getAvailableSeats(seanceId)
            ])

            // console.log('[Hall] Данные зала:', hallData)
            // console.log('[Hall] Все места зала (raw):', allSeatsData)
            // console.log('[Hall] Доступные места (raw):', availableSeatsData)

            if (!hallData) {
                console.error('[Hall] Ошибка: не удалось загрузить данные зала')
                return
            }

            setHall(hallData)

            // Сохраняем все места зала
            const seats = allSeatsData?.seats || []
            // console.log('[Hall] Обработанные места:', seats)
            console.log('[Hall] Количество мест:', seats.length)

            if (seats.length === 0) {
                console.warn('[Hall] ВНИМАНИЕ: В зале нет мест! Нужно создать места через скрипт generate_seats.py')
            }

            setAllSeats(seats)

            // Сохраняем массив ID доступных мест для быстрой проверки
            const availableSeats = availableSeatsData?.available_seats || []
            // console.log('[Hall] Доступные места (обработанные):', availableSeats)
            const availableIds = availableSeats.map(seat => seat.id)
            console.log('[Hall] Доступных мест:', availableIds.length)
            setAvailableSeatIds(availableIds)

            // Определяем забронированные места: все места зала, которые НЕ в списке доступных
            // ВАЖНО: если availableIds пустой, это может означать, что API не вернул данные,
            // в этом случае НЕ считаем все места забронированными
            const allSeatIds = seats.map(seat => seat.id)
            let bookedIds = []
            if (availableIds.length > 0) {
                // Если есть список доступных, определяем забронированные как разницу
                bookedIds = allSeatIds.filter(id => !availableIds.includes(id))
            } else {
                // Если список доступных пустой, используем данные из API (booked_seats count)
                // Но для начала оставляем пустым - места будут считаться доступными
                console.warn('[Hall] API вернул пустой список доступных мест. Используем fallback логику.')
                bookedIds = []
            }
            console.log('[Hall] Забронированных мест:', bookedIds.length)
            setBookedSeatIds(bookedIds)
        } catch (error) {
            console.error('[Hall] Ошибка загрузки данных сеанса:', error)
            console.error('[Hall] Детали ошибки:', {
                message: error.message,
                status: error.status,
                stack: error.stack
            })
        } finally {
            setLoading(false)
            isLoadingDataRef.current = false
        }
    }, [seanceId])

    useEffect(() => {
        // console.log('[Hall] useEffect вызван, seanceId:', seanceId)
        loadSeanceData()

        // Очистка при размонтировании
        return () => {
            // console.log('[Hall] Компонент размонтируется')
            isLoadingDataRef.current = false
        }
    }, [loadSeanceData]) // loadSeanceData уже зависит от seanceId через useCallback

    const handleSeatClick = (seatId) => {
        setSelectedSeats(prev => {
            if (prev.includes(seatId)) {
                const newSeats = prev.filter(id => id !== seatId)
                console.log('Убрано место:', seatId, 'Осталось:', newSeats.length)
                return newSeats
            } else {
                const newSeats = [...prev, seatId]
                console.log('Добавлено место:', seatId, 'Всего выбрано:', newSeats.length)
                return newSeats
            }
        })
    }

    const handleBooking = useCallback(async (e) => {
        // КРИТИЧНО: Предотвращаем перезагрузку страницы и любые другие действия
        if (e) {
            e.preventDefault()
            e.stopPropagation()
            e.stopImmediatePropagation?.()
        }

        // Дополнительная проверка: если уже идет бронирование, не делаем ничего
        if (isBooking) {
            console.log('[Hall] Бронирование уже в процессе, игнорируем клик')
            return
        }

        if (selectedSeats.length === 0) {
            setBookingMessage('⚠️ Выберите хотя бы одно место')
            setTimeout(() => {
                setBookingMessage(null)
            }, 3000)
            return
        }

        try {
            setIsBooking(true)
            // Убираем дубликаты на всякий случай
            const uniqueSeats = Array.from(new Set(selectedSeats))
            console.log('Бронирование мест:', selectedSeats, 'Уникальных:', uniqueSeats.length)

            // Снимаем выделение сразу и помечаем локально как занятые, чтобы избежать "залипания" цвета
            const seatsToBook = uniqueSeats
            setSelectedSeats([])
            setBookedSeatIds(prev => Array.from(new Set([...prev, ...seatsToBook])))

            // Бронируем места параллельно для ускорения процесса
            console.log(`[Hall] Начинаем бронирование ${seatsToBook.length} мест параллельно...`)
            const bookingTimestamp = Date.now()

            const bookingPromises = seatsToBook.map(async (seatId, index) => {
                try {
                    const bookingData = {
                        seance_id: Number(seanceId),
                        seat_id: seatId,
                        user_name: 'Гость',
                        user_phone: '+70000000000',
                        user_email: `guest_${bookingTimestamp}_${seatId}_${index}@example.com`, // Уникальный email для каждого места
                        qr_code_data: `guest:${bookingTimestamp}:seance:${seanceId}:seat:${seatId}`,
                    }
                    console.log(`[Hall] Бронируем место ${seatId}...`)
                    await api.bookTicket(bookingData)
                    console.log(`[Hall] Место ${seatId} успешно забронировано`)
                    return { success: true, seatId }
                } catch (error) {
                    console.error(`[Hall] Ошибка бронирования места ${seatId}:`, error.message)
                    return { success: false, seatId, error: error.message }
                }
            })

            // Ждем завершения всех бронирований
            const results = await Promise.all(bookingPromises)

            const bookedCount = results.filter(r => r.success).length
            const failedCount = results.filter(r => !r.success).length
            const successfullyBookedIds = results.filter(r => r.success).map(r => r.seatId)
            const failedSeatIds = results.filter(r => !r.success).map(r => r.seatId)

            if (failedSeatIds.length > 0) {
                console.warn(`[Hall] Не удалось забронировать места: ${failedSeatIds.join(', ')}`)
            }

            console.log(`[Hall] Бронирование завершено: успешно ${bookedCount}, ошибок ${failedCount}`)

            // Обновляем только список забронированных мест без полной перезагрузки данных
            // Это намного быстрее, чем загружать все данные заново
            if (successfullyBookedIds.length > 0) {
                setBookedSeatIds(prev => Array.from(new Set([...prev, ...successfullyBookedIds])))
                setAvailableSeatIds(prev => prev.filter(id => !successfullyBookedIds.includes(id)))
            }

            // Показываем результат через состояние (быстрее и не блокирует страницу)
            const message = failedCount === 0
                ? `✅ Успешно забронировано мест: ${bookedCount}`
                : `⚠️ Забронировано: ${bookedCount}, не удалось: ${failedCount}`

            setBookingMessage(message)
            console.log(`[Hall] ${message}`)

            // Автоматически скрываем сообщение через 5 секунд
            setTimeout(() => {
                setBookingMessage(null)
            }, 5000)
        } catch (error) {
            console.error('[Hall] Критическая ошибка бронирования:', error)
            const msg = typeof error?.message === 'string' ? error.message : 'Ошибка при бронировании'
            setBookingMessage(`❌ Ошибка: ${msg}`)
            setTimeout(() => {
                setBookingMessage(null)
            }, 5000)
        } finally {
            setIsBooking(false)
            // На всякий случай снимаем выделение
            setSelectedSeats([])
        }
    }, [selectedSeats, seanceId, isBooking])

    if (loading) {
        return (
            <div className="buying">
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    Загрузка...
                </div>
            </div>
        )
    }

    if (!seance) {
        return (
            <div className="buying">
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <p>Сеанс не найден</p>
                    <button onClick={() => navigate('/')}>Вернуться на главную</button>
                </div>
            </div>
        )
    }

    return (
        <div className="buying">
            <div className="buying__info">
                <div className="buying__info-description">
                    <h2 className="buying__info-title">{seance.film?.title || seance.film_id || 'Фильм'}</h2>
                    <p className="buying__info-start">
                        Начало сеанса: {new Date(seance.start_time).toLocaleString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </p>
                    <p className="buying__info-hall">
                        {seance.hall?.name || `Зал ${seance.hall_id}`}
                    </p>
                </div>
            </div>

            <div className="buying-scheme">
                <div className="buying-scheme__wrapper">
                    {!hall ? (
                        <div style={{ textAlign: 'center', padding: '2rem', color: '#fff' }}>
                            <p>Загрузка схемы зала...</p>
                        </div>
                    ) : allSeats.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem', color: '#fff' }}>
                            <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>В зале нет мест</p>
                            <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                                Необходимо создать места через скрипт generate_seats.py
                            </p>
                            <p style={{ fontSize: '0.8rem', opacity: 0.6, marginTop: '0.5rem' }}>
                                Зал: {hall.rows} рядов × {hall.seats_per_row} мест = {hall.rows * hall.seats_per_row} мест
                            </p>
                        </div>
                    ) : (() => {
                        console.log('Рендерим схему зала. Зал:', hall.rows, 'рядов,', hall.seats_per_row, 'мест в ряду')
                        console.log('Реальных мест в БД:', allSeats.length)
                        console.log('Доступные ID:', availableSeatIds, 'Количество:', availableSeatIds.length)
                        console.log('Забронированные ID:', bookedSeatIds, 'Количество:', bookedSeatIds.length)

                        // Создаем карту реальных мест для быстрого поиска
                        const seatsMap = new Map()
                        allSeats.forEach(seat => {
                            const key = `${seat.row_number}-${seat.seat_number}`
                            seatsMap.set(key, seat)
                        })

                        // Генерируем полную схему зала на основе rows и seats_per_row
                        const rows = []
                        for (let rowNum = 1; rowNum <= hall.rows; rowNum++) {
                            const rowSeats = []
                            for (let seatNum = 1; seatNum <= hall.seats_per_row; seatNum++) {
                                const key = `${rowNum}-${seatNum}`
                                const realSeat = seatsMap.get(key)

                                if (realSeat) {
                                    // Есть реальное место в БД
                                    // Доступно, если место не в списке забронированных
                                    // Если availableSeatIds пустой, считаем все места доступными (кроме забронированных)
                                    const availableListEmpty = availableSeatIds.length === 0
                                    const isBooked = bookedSeatIds.includes(realSeat.id)
                                    const isInAvailableList = availableSeatIds.includes(realSeat.id)
                                    const isAvailable = !isBooked && (isInAvailableList || availableListEmpty)
                                    const isSelected = selectedSeats.includes(realSeat.id)
                                    // VIP-места: центральные места в рядах 4-7
                                    // Центральная треть мест в ряду считаются VIP
                                    const isVipRow = rowNum >= 4 && rowNum <= 7
                                    let isVip = false
                                    if (isVipRow && hall.seats_per_row > 0) {
                                        // Вычисляем центральную треть мест
                                        const third = Math.floor(hall.seats_per_row / 3)
                                        const centerStart = third + 1
                                        const centerEnd = hall.seats_per_row - third
                                        isVip = seatNum >= centerStart && seatNum <= centerEnd
                                    }

                                    let seatClass = 'buying-scheme__chair'
                                    if (isSelected) {
                                        seatClass += ' buying-scheme__chair_selected'
                                    } else if (!isAvailable) {
                                        seatClass += ' buying-scheme__chair_taken'
                                    } else if (isVip) {
                                        seatClass += ' buying-scheme__chair_vip'
                                    } else {
                                        seatClass += ' buying-scheme__chair_standart'
                                    }

                                    rowSeats.push(
                                        <button
                                            key={realSeat.id}
                                            className={seatClass}
                                            onClick={() => isAvailable && handleSeatClick(realSeat.id)}
                                            disabled={!isAvailable}
                                            title={`Ряд ${rowNum}, Место ${seatNum}${!isAvailable ? ' (Занято)' : ''}`}
                                            style={{
                                                color: !isAvailable ? '#ccc' : '#000',
                                                ...(!isAvailable && !isSelected ? {
                                                    backgroundColor: '#525252',
                                                    borderColor: '#777',
                                                    opacity: 0.7
                                                } : {})
                                            }}
                                        >
                                            {seatNum}
                                        </button>
                                    )
                                } else {
                                    // Места нет в БД - показываем как disabled (пропуск)
                                    rowSeats.push(
                                        <span
                                            key={`disabled-${rowNum}-${seatNum}`}
                                            className="buying-scheme__chair buying-scheme__chair_disabled"
                                            title={`Ряд ${rowNum}, Место ${seatNum} (Недоступно)`}
                                        />
                                    )
                                }
                            }
                            rows.push(
                                <div key={rowNum} className="buying-scheme__row">
                                    {rowSeats}
                                </div>
                            )
                        }

                        return rows
                    })()}
                </div>
                <div className="buying-scheme__legend">
                    <div className="col">
                        <p className="buying-scheme__legend-price">
                            <span className="buying-scheme__chair buying-scheme__chair_standart"></span>
                            {' '}Свободно ({seance?.price_standard || 0} руб)
                        </p>
                        <p className="buying-scheme__legend-price">
                            <span className="buying-scheme__chair buying-scheme__chair_vip"></span>
                            {' '}Свободно VIP ({seance?.price_vip || 0} руб)
                        </p>
                    </div>
                    <div className="col">
                        <p className="buying-scheme__legend-price">
                            <span className="buying-scheme__chair buying-scheme__chair_taken"></span>
                            {' '}Занято
                        </p>
                        <p className="buying-scheme__legend-price">
                            <span className="buying-scheme__chair buying-scheme__chair_selected"></span>
                            {' '}Выбрано
                        </p>
                    </div>
                </div>
            </div>

            {bookingMessage && (
                <div style={{
                    padding: '1rem',
                    margin: '1rem 0',
                    backgroundColor: bookingMessage.includes('✅') ? '#4caf50' : '#ff9800',
                    color: '#fff',
                    borderRadius: '4px',
                    textAlign: 'center',
                    fontSize: '1rem',
                    fontWeight: 'bold'
                }}>
                    {bookingMessage}
                </div>
            )}

            <button
                type="button"
                className="acceptin-button"
                onClick={handleBooking}
                disabled={selectedSeats.length === 0 || isBooking}
            >
                {isBooking ? 'Бронирование...'
                    : selectedSeats.length > 0
                        ? `Забронировать ${selectedSeats.length} ${selectedSeats.length === 1 ? 'место' : 'мест'}`
                        : 'Забронировать'
                }
            </button>
        </div>
    )
}

export default Hall

