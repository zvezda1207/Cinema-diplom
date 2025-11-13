import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../services/api'
import './Payment.css'

function Payment() {
    const navigate = useNavigate()
    const { state } = useLocation()
    const { seance, film, seats, total } = state ?? {}

    const hasData = Boolean(seance) && Array.isArray(seats) && seats.length > 0
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')
    const [successMessage, setSuccessMessage] = useState('')

    const seatLabels = hasData
        ? seats
            .map((seat) => {
                const seatNumber = seat?.seat
                const rowNumber = seat?.row
                if (rowNumber && (typeof rowNumber === 'number' || typeof rowNumber === 'string')) {
                    return `Ряд ${rowNumber}, место ${seatNumber}`
                }
                return typeof seatNumber === 'number' || typeof seatNumber === 'string'
                    ? `Место ${seatNumber}`
                    : null
            })
            .filter(Boolean)
            .join(', ')
        : ''

    const hallName = hasData
        ? seance?.hall?.name || `Зал ${seance?.hall_id ?? ''}`.trim()
        : ''

    const startTime = hasData
        ? new Date(seance.start_time).toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
        })
        : ''

    const formattedTotal = Number.isFinite(total) ? total : 0

    const formatSeatForMessage = (seat) => {
        if (!seat) return 'выбранное место'
        const parts = []
        if (seat?.row !== undefined && seat?.row !== null) {
            parts.push(`ряд ${seat.row}`)
        }
        if (seat?.seat !== undefined && seat?.seat !== null) {
            parts.push(`место ${seat.seat}`)
        }
        return parts.length ? parts.join(', ') : 'выбранное место'
    }

    const getFriendlyError = (error, seat) => {
        const message = (error?.message || '').toLowerCase()
        const seatLabel = formatSeatForMessage(seat)
        if (message.includes('seat already booked')) {
            return `Не удалось забронировать ${seatLabel}: место уже занято. Выберите другое.`
        }
        if (message.includes('seat does not belong')) {
            return `Не удалось забронировать ${seatLabel}: место относится к другому залу. Обновите страницу и попробуйте снова.`
        }
        if (message.includes('seat not found') || message.includes('seance not found')) {
            return 'Не удалось найти данные сеанса или места. Обновите страницу и попробуйте снова.'
        }
        if (error?.status === 500) {
            return 'Сервис недоступен. Попробуйте повторить попытку позже.'
        }
        if (error?.status === 429) {
            return 'Слишком много запросов. Подождите пару секунд и попробуйте ещё раз.'
        }
        if (error?.status === 0) {
            return 'Не удалось связаться с сервером. Проверьте соединение и повторите попытку.'
        }
        return error?.message || 'Не удалось забронировать места. Попробуйте ещё раз.'
    }

    const handleConfirm = async () => {
        if (!hasData) {
            navigate('/')
            return
        }

        if (isSubmitting) return

        setErrorMessage('')
        setSuccessMessage('')
        setIsSubmitting(true)

        const timestamp = Date.now()

        try {
            const bookingPromises = seats.map((seat, index) => {
                const bookingPayload = {
                    seance_id: seance.id,
                    seat_id: seat.id,
                    user_name: 'Гость',
                    user_phone: '+70000000000',
                    user_email: `guest_${timestamp}_${seat.id}_${index}@example.com`,
                    qr_code_data: `guest:${timestamp}:seance:${seance.id}:seat:${seat.id}`,
                }

                return api
                    .bookTicket(bookingPayload)
                    .then((response) => ({
                        success: true,
                        response,
                        seat,
                    }))
                    .catch((error) => ({
                        success: false,
                        error,
                        seat,
                    }))
            })

            const results = await Promise.all(bookingPromises)
            const failed = results.filter((item) => !item.success)

            if (failed.length > 0) {
                const friendlyMessages = failed.map((item) => getFriendlyError(item.error, item.seat))
                const uniqueMessages = Array.from(new Set(friendlyMessages.filter(Boolean)))
                const combinedMessage = uniqueMessages.length
                    ? uniqueMessages.join(' ')
                    : 'Не удалось забронировать выбранные места. Попробуйте ещё раз.'
                setErrorMessage(combinedMessage)
                setIsSubmitting(false)
                return
            }

            const bookingDetails = results.map((item) => ({
                seat: item.seat,
                booking_code: item.response?.booking_code,
                ticket_id: item.response?.ticket_id || item.response?.id,
                qr_code_path: item.response?.qr_code_path,
                price: item.response?.price,
            }))

            setSuccessMessage('Бронирование подтверждено. Открываем электронный билет…')
            await new Promise((resolve) => setTimeout(resolve, 1800))

            navigate('/ticket', {
                state: {
                    seance,
                    film,
                    seats,
                    total: formattedTotal,
                    bookings: bookingDetails,
                },
            })
        } catch (error) {
            setErrorMessage(error?.message || 'Не удалось выполнить бронирование. Попробуйте ещё раз.')
        } finally {
            setIsSubmitting(false)
        }
    }

    if (!hasData) {
        return (
            <section className="ticket ticket--payment">
                <header className="tichet__check">
                    <h2 className="ticket__check-title">Вы выбрали билеты:</h2>
                </header>
                <div className="ticket__info-wrapper ticket__info-wrapper_empty">
                    <p className="ticket__info">Данные бронирования не найдены.</p>
                    <button className="acceptin-button" onClick={() => navigate('/')}>
                        На главную
                    </button>
                </div>
            </section>
        )
    }

    return (
        <section className="ticket ticket--payment">
            <header className="tichet__check">
                <h2 className="ticket__check-title">Вы выбрали билеты:</h2>
            </header>

            <div className="ticket__info-wrapper">
                <p className="ticket__info">
                    На фильм:{' '}
                    <span className="ticket__details ticket__title">
                        {film?.title || seance.film?.title || '—'}
                    </span>
                </p>
                <p className="ticket__info">
                    Места:{' '}
                    <span className="ticket__details ticket__chairs">{seatLabels || '—'}</span>
                </p>
                <p className="ticket__info">
                    В зале:{' '}
                    <span className="ticket__details ticket__hall">{hallName || '—'}</span>
                </p>
                <p className="ticket__info">
                    Начало сеанса:{' '}
                    <span className="ticket__details ticket__start">{startTime || '—:—'}</span>
                </p>
                <p className="ticket__info">
                    Стоимость:{' '}
                    <span className="ticket__details ticket__cost">{formattedTotal}</span> рублей
                </p>

                {errorMessage && (
                    <p className="ticket__hint ticket__hint_error">{errorMessage}</p>
                )}
                {successMessage && (
                    <p className="ticket__hint ticket__hint_success">{successMessage}</p>
                )}

                <button
                    className="acceptin-button"
                    onClick={handleConfirm}
                    disabled={isSubmitting}
                >
                    Получить код бронирования
                </button>

                <p className="ticket__hint">
                    После оплаты билет будет доступен в этом окне, а также придёт вам на почту.
                    Покажите QR-код нашему контроллёру у входа в зал.
                </p>
                <p className="ticket__hint">Приятного просмотра!</p>
            </div>
        </section>
    )
}

export default Payment