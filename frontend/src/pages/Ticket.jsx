import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useRef, useState } from 'react'
import api from '../services/api'
import './Payment.css'

const MAX_QR_RETRIES = 4
const QR_RETRY_DELAY_MS = 1500

const resolveQrUrl = (path) => {
    if (!path) return null
    if (/^https?:\/\//i.test(path)) return path
    const base = api.baseURL || ''
    if (!base) {
        return path.startsWith('/') ? path : `/${path}`
    }
    const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    return `${normalizedBase}${normalizedPath}`
}

function Ticket() {
    const navigate = useNavigate()
    const { state } = useLocation()
    const retryTimeoutRef = useRef()
    const [qrSrc, setQrSrc] = useState(null)
    const [qrAttempts, setQrAttempts] = useState(0)
    const [qrStatus, setQrStatus] = useState('idle')

    const seance = state?.seance
    const film = state?.film
    const seats = state?.seats
    const bookings = state?.bookings

    const seatLabels = useMemo(() => {
        if (!Array.isArray(seats)) return ''
        return seats
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
    }, [seats])

    const hasData = Boolean(seance) && Array.isArray(seats) && seats.length > 0
    const firstBookingWithQr = useMemo(
        () => (Array.isArray(bookings) ? bookings.find((item) => item?.qr_code_path) : null),
        [bookings]
    )
    const baseQrUrl = useMemo(
        () => resolveQrUrl(firstBookingWithQr?.qr_code_path),
        [firstBookingWithQr]
    )

    useEffect(() => {
        return () => {
            if (retryTimeoutRef.current) {
                clearTimeout(retryTimeoutRef.current)
            }
        }
    }, [])

    useEffect(() => {
        if (!baseQrUrl) {
            setQrSrc(null)
            setQrAttempts(0)
            setQrStatus('idle')
            return
        }
        setQrAttempts(0)
        setQrStatus('loading')
        setQrSrc(`${baseQrUrl}?v=${Date.now()}`)
    }, [baseQrUrl])

    const scheduleRetry = () => {
        if (!baseQrUrl) return
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current)
        }
        retryTimeoutRef.current = setTimeout(() => {
            setQrStatus('loading')
            setQrSrc(`${baseQrUrl}?v=${Date.now()}`)
        }, QR_RETRY_DELAY_MS)
    }

    const handleQrError = () => {
        setQrAttempts((prev) => {
            const next = prev + 1
            if (next > MAX_QR_RETRIES) {
                setQrStatus('failed')
                setQrSrc(null)
                return next
            }
            setQrStatus('retry')
            scheduleRetry()
            return next
        })
    }

    const handleQrLoad = () => {
        setQrStatus('success')
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current)
            retryTimeoutRef.current = null
        }
    }

    if (!hasData) {
        return (
            <section className="ticket ticket--payment">
                <header className="tichet__check">
                    <h2 className="ticket__check-title">Электронный билет</h2>
                </header>
                <div className="ticket__info-wrapper ticket__info-wrapper_empty">
                    <p className="ticket__info">Данные бронирования не найдены.</p>
                    <button className="acceptin-button" onClick={() => navigate('/')}>
                        Вернуться на главную
                    </button>
                </div>
            </section>
        )
    }

    const hallName = seance?.hall?.name || `Зал ${seance?.hall_id ?? ''}`.trim()
    const startTime = new Date(seance.start_time).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
    })

    return (
        <section className="ticket ticket--payment">
            <header className="tichet__check">
                <h2 className="ticket__check-title">Электронный билет</h2>
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
                    <span className="ticket__details ticket__chairs">
                        {seatLabels || '—'}
                    </span>
                </p>
                <p className="ticket__info">
                    В зале:{' '}
                    <span className="ticket__details ticket__hall">{hallName || '—'}</span>
                </p>
                <p className="ticket__info">
                    Начало сеанса:{' '}
                    <span className="ticket__details ticket__start">{startTime || '—:—'}</span>
                </p>

                {Array.isArray(bookings) && bookings.length > 0 && (
                    <p className="ticket__info">
                        Код бронирования:{' '}
                        <span className="ticket__details">
                            {bookings.map((item) => item?.booking_code).filter(Boolean).join(', ')}
                        </span>
                    </p>
                )}

                {qrSrc ? (
                    <img
                        className="ticket__info-qr"
                        src={qrSrc}
                        alt="QR-код бронирования"
                        onError={handleQrError}
                        onLoad={handleQrLoad}
                    />
                ) : null}

                {(qrStatus === 'loading' || qrStatus === 'retry') && (
                    <p className="ticket__hint">Готовим QR-код…</p>
                )}
                {qrStatus === 'idle' && !baseQrUrl && (
                    <p className="ticket__hint">Готовим QR-код…</p>
                )}

                {qrStatus === 'failed' && (
                    <p className="ticket__hint ticket__hint_error">
                        QR-код временно недоступен. Сохраните код бронирования.
                    </p>
                )}

                <p className="ticket__hint">
                    Покажите QR-код нашему контроллеру для подтверждения бронирования.
                </p>
                <p className="ticket__hint">Приятного просмотра!</p>

                <button className="acceptin-button" onClick={() => navigate('/')}>
                    Вернуться на главную
                </button>
            </div>
        </section>
    )
}

export default Ticket

