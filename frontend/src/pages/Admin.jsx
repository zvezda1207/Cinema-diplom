import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import './Admin.css'
import posterPlaceholder from '../assets/layouts/admin/i/poster.png'

const seatTypeCycle = ['standart', 'vip', 'disabled']
const seatTypeClassMap = {
    standart: 'conf-step__chair_standart',
    vip: 'conf-step__chair_vip',
    disabled: 'conf-step__chair_disabled',
}

const fallbackPoster = posterPlaceholder

const MOVIE_COLORS = [
    '#caff85',
    '#85ff89',
    '#85ffd3',
    '#85e2ff',
    '#8599ff',
    '#ba85ff',
    '#ff85fb',
    '#ff85b1',
    '#ffa285',
]

const normalizeIsActive = (value) => {
    if (typeof value === 'boolean') return value
    if (typeof value === 'number') return value === 1
    if (typeof value === 'string') {
        const normalized = value.trim().toLowerCase()
        return normalized === 'true' || normalized === '1'
    }
    return false
}

const formatBookingDate = (value) => {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    })
}

const formatTime = (value) => {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '--:--'
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const MIN_BLOCK_WIDTH = 40
const TIMELINE_WIDTH = 720

function Admin() {
    const navigate = useNavigate()
    const showTestCredentials = import.meta.env.DEV

    const [loading, setLoading] = useState(true)
    const [dataLoading, setDataLoading] = useState(false)
    const [isAuthenticated, setIsAuthenticated] = useState(false)

    const [loginForm, setLoginForm] = useState({
        email: '',
        password: '',
    })
    const [loginError, setLoginError] = useState('')

    const [halls, setHalls] = useState([])
    const [films, setFilms] = useState([])
    const [seances, setSeances] = useState([])
    const [bookings, setBookings] = useState([])
    const [bookingsLimit, setBookingsLimit] = useState(12)
    const [bookingsFilter, setBookingsFilter] = useState('active')
    const [archivingTicketIds, setArchivingTicketIds] = useState([])

    const [sectionsOpen, setSectionsOpen] = useState({
        halls: true,
        hallConfig: true,
        prices: true,
        seances: true,
        sales: true,
    })

    const [hallForm, setHallForm] = useState({
        name: '',
        rows: 10,
        seats_per_row: 10,
        is_active: false,
    })
    const [filmForm, setFilmForm] = useState({
        title: '',
        description: '',
        duration: 120,
        poster_url: '',
    })
    const [hallConfigForm, setHallConfigForm] = useState({
        rows: '',
        seats_per_row: '',
    })
    const [priceForm, setPriceForm] = useState({
        standard: '',
        vip: '',
    })

    const [selectedConfigHallId, setSelectedConfigHallId] = useState(null)
    const [selectedPriceHallId, setSelectedPriceHallId] = useState(null)
    const [showHallForm, setShowHallForm] = useState(false)
    const [showFilmForm, setShowFilmForm] = useState(false)
    const [showSeanceForm, setShowSeanceForm] = useState(false)
    const [seanceFormError, setSeanceFormError] = useState('')
    const [seanceForm, setSeanceForm] = useState({
        film_id: '',
        hall_id: '',
        start_time: '',
        price_standard: '',
        price_vip: '',
    })

    const [hallSeats, setHallSeats] = useState([])
    const hallSeatsCacheRef = useState(() => new Map())[0]

    const [feedback, setFeedback] = useState('')
    const [salesStatus, setSalesStatus] = useState(null)

    const allHallsActive = useMemo(
        () => halls.length > 0 && halls.every((hall) => normalizeIsActive(hall.is_active)),
        [halls]
    )

    const toggleSection = (key) => {
        setSectionsOpen((prev) => ({
            ...prev,
            [key]: !prev[key],
        }))
    }

    const checkAuth = useCallback(() => {
        const token = localStorage.getItem('token')
        if (token) {
            api.token = token
            setIsAuthenticated(true)
        }
        setLoading(false)
    }, [])

    const loadHallSeats = useCallback(async (hallId, force = false) => {
        if (!hallId) return
        if (!force && hallSeatsCacheRef.has(hallId)) {
            setHallSeats(hallSeatsCacheRef.get(hallId) || [])
            return
        }

        try {
            const response = await api.getSeats({ hall_id: hallId })
            const seatsData = response?.seats || []
            hallSeatsCacheRef.set(hallId, seatsData)
            setHallSeats(seatsData)
        } catch (error) {
            console.error('Не удалось загрузить места зала:', error)
            setFeedback(`Не удалось загрузить места: ${error.message}`)
        }
    }, [hallSeatsCacheRef])

    const loadAllData = useCallback(async () => {
        setDataLoading(true)
        setFeedback('')
        try {
            const [hallsResponse, filmsResponse, seancesResponse, bookingsResponse] =
                await Promise.all([
                    api.getHalls(),
                    api.getFilms(),
                    api.getSeances(),
                    api
                        .getAllBookings({ include_archived: true })
                        .catch((error) => {
                            console.warn('Не удалось загрузить бронирования:', error)
                            return { tickets: [] }
                        }),
                ])

            const hallsData = hallsResponse?.halls || []
            const filmsData = filmsResponse?.films || []
            const seancesData = seancesResponse?.seances || []
            const bookingsData = bookingsResponse?.tickets || []

            setHalls(hallsData)
            setFilms(filmsData)
            setSeances(seancesData)
            setBookings(bookingsData)
            setArchivingTicketIds([])
        } catch (error) {
            console.error('Ошибка загрузки данных администратора:', error)
            setFeedback(`Ошибка загрузки данных: ${error.message}`)
        } finally {
            setDataLoading(false)
        }
    }, [])

    useEffect(() => {
        checkAuth()
    }, [checkAuth])

    useEffect(() => {
        if (isAuthenticated) {
            loadAllData()
        }
    }, [isAuthenticated, loadAllData])

    useEffect(() => {
        if (!halls.length) return

        setSelectedConfigHallId((prev) => prev ?? halls[0].id)
        setSelectedPriceHallId((prev) => prev ?? halls[0].id)
    }, [halls])

    useEffect(() => {
        if (!selectedConfigHallId) return
        const hall = halls.find((h) => h.id === selectedConfigHallId)
        if (hall) {
            setHallConfigForm((prev) => {
                if (
                    prev.rows === String(hall.rows) &&
                    prev.seats_per_row === String(hall.seats_per_row)
                ) {
                    return prev
                }
                return {
                    rows: String(hall.rows),
                    seats_per_row: String(hall.seats_per_row),
                }
            })
            loadHallSeats(selectedConfigHallId)
        }
    }, [selectedConfigHallId, halls, loadHallSeats])

    useEffect(() => {
        if (!selectedPriceHallId) return
        const hallSeances = seances.filter((s) => s.hall_id === selectedPriceHallId)
        if (hallSeances.length > 0) {
            const { price_standard, price_vip } = hallSeances[0]
            setPriceForm((prev) => {
                if (
                    prev.standard === String(price_standard ?? '') &&
                    prev.vip === String(price_vip ?? '')
                ) {
                    return prev
                }
                return {
                    standard: String(price_standard ?? ''),
                    vip: String(price_vip ?? ''),
                }
            })
        } else {
            setPriceForm((prev) => {
                if (prev.standard === '' && prev.vip === '') {
                    return prev
                }
                return { standard: '', vip: '' }
            })
        }
    }, [selectedPriceHallId, seances])

    const handleLogin = async (event) => {
        event.preventDefault()
        setLoginError('')
        try {
            const response = await api.login(loginForm.email, loginForm.password)
            if (response?.token) {
                localStorage.setItem('token', response.token)
                api.token = response.token
                setIsAuthenticated(true)
            } else {
                setLoginError('Не получен токен от сервера')
            }
        } catch (error) {
            console.error('Ошибка входа администратора:', error)
            setLoginError(error.message || 'Ошибка входа. Проверьте email и пароль.')
        }
    }

    const handleLogout = () => {
        localStorage.removeItem('token')
        api.token = null
        setIsAuthenticated(false)
        navigate('/')
    }

    const handleCreateHall = async (event) => {
        event.preventDefault()
        try {
            await api.createHall({
                ...hallForm,
                rows: Number(hallForm.rows),
                seats_per_row: Number(hallForm.seats_per_row),
            })
            setShowHallForm(false)
            setHallForm({ name: '', rows: 10, seats_per_row: 10, is_active: false })
            hallSeatsCacheRef.clear()
            loadAllData()
        } catch (error) {
            console.error('Ошибка создания зала:', error)
            setFeedback(`Ошибка создания зала: ${error.message}`)
        }
    }

    const handleHallDelete = async (hallId) => {
        if (!confirm('Удалить зал вместе с его сеансами?')) return
        try {
            await api.deleteHall(hallId)
            hallSeatsCacheRef.delete(hallId)
            loadAllData()
        } catch (error) {
            console.error('Ошибка удаления зала:', error)
            setFeedback(`Ошибка удаления: ${error.message}`)
        }
    }

    const handleHallConfigSave = async (event) => {
        event.preventDefault()
        if (!selectedConfigHallId) return
        try {
            await api.updateHall(selectedConfigHallId, {
                rows: Number(hallConfigForm.rows),
                seats_per_row: Number(hallConfigForm.seats_per_row),
            })
            hallSeatsCacheRef.delete(selectedConfigHallId)
            await loadHallSeats(selectedConfigHallId, true)
            loadAllData()
            setFeedback('Настройки зала сохранены')
        } catch (error) {
            console.error('Ошибка обновления зала:', error)
            setFeedback(`Ошибка обновления зала: ${error.message}`)
        }
    }

    const handleSeatToggle = async (seat) => {
        if (!seat) return
        const currentType = (seat.seat_type || 'standart').toLowerCase()
        const currentIndex = seatTypeCycle.indexOf(currentType)
        const nextType = seatTypeCycle[(currentIndex + 1) % seatTypeCycle.length]
        try {
            await api.updateSeat(seat.id, { seat_type: nextType })
            setHallSeats((prev) =>
                prev.map((item) =>
                    item.id === seat.id ? { ...item, seat_type: nextType } : item
                )
            )
            hallSeatsCacheRef.set(selectedConfigHallId, (hallSeatsCacheRef.get(selectedConfigHallId) || []).map((item) =>
                item.id === seat.id ? { ...item, seat_type: nextType } : item
            ))
        } catch (error) {
            console.error('Ошибка изменения типа кресла:', error)
            setFeedback(`Ошибка обновления места: ${error.message}`)
        }
    }

    const handlePriceSave = async (event) => {
        event.preventDefault()
        if (!selectedPriceHallId) return
        try {
            const hallSeances = seances.filter(
                (seance) => seance.hall_id === selectedPriceHallId
            )
            await Promise.all(
                hallSeances.map((seance) =>
                    api.updateSeance(seance.id, {
                        price_standard: Number(priceForm.standard),
                        price_vip: Number(priceForm.vip),
                    })
                )
            )
            loadAllData()
            setFeedback('Цены обновлены для всех сеансов зала')
        } catch (error) {
            console.error('Ошибка сохранения цен:', error)
            setFeedback(`Ошибка сохранения цен: ${error.message}`)
        }
    }

    const handleCreateFilm = async (event) => {
        event.preventDefault()
        try {
            await api.createFilm({
                ...filmForm,
                poster_url: filmForm.poster_url?.trim() || '',
            })
            setShowFilmForm(false)
            setFilmForm({
                title: '',
                description: '',
                duration: 120,
                poster_url: '',
            })
            await loadAllData()
        } catch (error) {
            console.error('Ошибка создания фильма:', error)
            setFeedback(`Ошибка создания фильма: ${error.message}`)
        }
    }

    const handleFilmDelete = async (filmId) => {
        if (!confirm('Удалить фильм?')) return
        try {
            await api.deletefilm(filmId)
            await loadAllData()
        } catch (error) {
            console.error('Ошибка удаления фильма:', error)
            setFeedback(`Ошибка удаления фильма: ${error.message}`)
        }
    }

    const handleCreateSeance = async (event) => {
        event.preventDefault()
        setSeanceFormError('')
        setFeedback('')
        if (!seanceForm.film_id || !seanceForm.hall_id || !seanceForm.start_time) {
            setSeanceFormError('Укажите фильм, зал и время начала сеанса.')
            return
        }

        const parsedStart = new Date(seanceForm.start_time)
        if (Number.isNaN(parsedStart.getTime())) {
            setFeedback('Введите дату и время сеанса в формате ГГГГ-ММ-ДДTчч:мм.')
            return
        }

        const hallIdNumber = Number(seanceForm.hall_id)
        const basePrices = seances.find((seance) => seance.hall_id === hallIdNumber)

        const payload = {
            film_id: Number(seanceForm.film_id),
            hall_id: hallIdNumber,
            start_time: seanceForm.start_time,
            price_standard:
                seanceForm.price_standard !== ''
                    ? Number(seanceForm.price_standard)
                    : basePrices?.price_standard ?? 0,
            price_vip:
                seanceForm.price_vip !== ''
                    ? Number(seanceForm.price_vip)
                    : basePrices?.price_vip ?? 0,
        }

        try {
            const createdSeance = await api.createSeance(payload)
            const newSeance = {
                id: createdSeance.id,
                ...payload,
                start_time: payload.start_time,
            }
            setSeances((prev) => [...prev, newSeance])
            setShowSeanceForm(false)
            setSeanceForm({
                film_id: '',
                hall_id: '',
                start_time: '',
                price_standard: '',
                price_vip: '',
            })
            setFeedback('Новый сеанс создан. Расписание обновлено.')
            await loadAllData()
        } catch (error) {
            console.error('Ошибка создания сеанса:', error)
            setSeanceFormError(error.message || 'Не удалось создать сеанс. Попробуйте ещё раз.')
        }
    }

    const handleSeanceDelete = async (seanceId) => {
        if (!confirm('Удалить сеанс?')) return
        try {
            await api.deleteSeance(seanceId)
            await loadAllData()
        } catch (error) {
            console.error('Ошибка удаления сеанса:', error)
            setFeedback(`Ошибка удаления сеанса: ${error.message}`)
        }
    }

    const handleArchiveToggle = async (ticketId, nextArchived) => {
        setArchivingTicketIds((prev) =>
            prev.includes(ticketId) ? prev : [...prev, ticketId]
        )
        try {
            await api.setTicketArchived(ticketId, nextArchived)
            setBookings((prev) =>
                prev.map((booking) =>
                    booking.id === ticketId
                        ? { ...booking, archived: nextArchived }
                        : booking
                )
            )
            setFeedback(
                nextArchived
                    ? 'Бронирование перенесено в архив.'
                    : 'Бронирование восстановлено из архива.'
            )
        } catch (error) {
            console.error('Не удалось изменить статус архивации бронирования:', error)
            setFeedback(
                error.message ||
                'Не удалось обновить статус бронирования. Попробуйте ещё раз.'
            )
        } finally {
            setArchivingTicketIds((prev) => prev.filter((id) => id !== ticketId))
        }
    }

    const handleOpenSales = async () => {
        const issues = []
        if (!halls.length) {
            issues.push('Создайте хотя бы один зал.')
        }
        const invalidConfigs = halls
            .filter(
                (hall) =>
                    !Number.isFinite(hall.rows) ||
                    hall.rows <= 0 ||
                    !Number.isFinite(hall.seats_per_row) ||
                    hall.seats_per_row <= 0
            )
            .map((hall) => hall.name)
        if (invalidConfigs.length) {
            issues.push(
                `Проверьте конфигурацию рядов и мест: ${invalidConfigs.join(', ')}.`
            )
        }
        if (!seances.length) {
            issues.push('Добавьте хотя бы один сеанс.')
        }

        if (issues.length) {
            setSalesStatus({
                type: 'error',
                message: issues.join(' '),
            })
            return
        }

        const nextState = !allHallsActive

        try {
            const responses = await Promise.all(
                halls.map((hall) =>
                    api.updateHall(hall.id, {
                        name: hall.name,
                        rows: hall.rows,
                        seats_per_row: hall.seats_per_row,
                        is_active: nextState,
                    })
                )
            )

            console.log('[Admin] Ответы обновления залов:', responses)

            console.log(
                `[Admin] Изменили статус залов на ${nextState ? 'активный' : 'неактивный'}`
            )

            setHalls((prev) => {
                const updated = prev.map((hall) => ({
                    ...hall,
                    is_active: nextState,
                }))
                console.log('[Admin] Состояние залов после переключения:', updated)
                return updated
            })

            setSalesStatus({
                type: 'success',
                message: nextState
                    ? 'Продажа открыта! Проверьте бронирования ниже или откройте пользовательскую страницу.'
                    : 'Продажа приостановлена. Вернуться к настройке можно в любое время.',
            })

            await loadAllData()
        } catch (error) {
            console.error('Не удалось изменить статус залов:', error)
            setSalesStatus({
                type: 'error',
                message: error?.message || 'Не удалось изменить статус продаж. Попробуйте ещё раз.',
            })
        }
    }

    const seatMap = useMemo(() => {
        const map = new Map()
        hallSeats.forEach((seat) => {
            map.set(`${seat.row_number}-${seat.seat_number}`, seat)
        })
        return map
    }, [hallSeats])

    const seatGrid = useMemo(() => {
        const rowsCount = Number(hallConfigForm.rows) || 0
        const seatsPerRow = Number(hallConfigForm.seats_per_row) || 0
        return Array.from({ length: rowsCount }, (_, rowIndex) =>
            Array.from({ length: seatsPerRow }, (_, seatIndex) => {
                const key = `${rowIndex + 1}-${seatIndex + 1}`
                return seatMap.get(key) || null
            })
        )
    }, [hallConfigForm.rows, hallConfigForm.seats_per_row, seatMap])

    const filmsById = useMemo(() => {
        const map = new Map()
        films.forEach((film) => map.set(film.id, film))
        return map
    }, [films])

    const hallsById = useMemo(() => {
        const map = new Map()
        halls.forEach((hall) => map.set(hall.id, hall))
        return map
    }, [halls])

    const colorsByFilmId = useMemo(() => {
        const map = new Map()
        films.forEach((film, index) => {
            map.set(film.id, MOVIE_COLORS[index % MOVIE_COLORS.length])
        })
        return map
    }, [films])

    const todayKey = useMemo(
        () => new Date().toISOString().slice(0, 10),
        []
    )

    const timelineBlocksByHall = useMemo(() => {
        const map = new Map()
        halls.forEach((hall) => {
            map.set(hall.id, [])
        })

        seances.forEach((seance) => {
            const dateKey = new Date(seance.start_time).toISOString().slice(0, 10)
            if (dateKey !== todayKey) {
                return
            }

            const film = filmsById.get(seance.film_id)
            const duration = film?.duration ?? 90
            const startDate = new Date(seance.start_time)
            const startMinutes = startDate.getHours() * 60 + startDate.getMinutes()
            const width = Math.max(
                MIN_BLOCK_WIDTH,
                (duration / (24 * 60)) * TIMELINE_WIDTH
            )
            const left = Math.min(
                TIMELINE_WIDTH - width,
                (startMinutes / (24 * 60)) * TIMELINE_WIDTH
            )
            const color = colorsByFilmId.get(seance.film_id)
            const block = {
                id: seance.id,
                title: film?.title || `Сеанс #${seance.id}`,
                startLabel: formatTime(seance.start_time),
                width,
                left,
                color,
            }
            const hallBlocks = map.get(seance.hall_id)
            if (hallBlocks) {
                hallBlocks.push(block)
            } else {
                map.set(seance.hall_id, [block])
            }
        })

        map.forEach((blocks) =>
            blocks.sort((a, b) => {
                if (a.left === b.left) {
                    return a.width - b.width
                }
                return a.left - b.left
            })
        )

        return map
    }, [halls, seances, filmsById, colorsByFilmId, todayKey])

    const bookingsSorted = useMemo(() => {
        return [...bookings].sort((a, b) => {
            const bTime = Date.parse(b.created_at || '') || 0
            const aTime = Date.parse(a.created_at || '') || 0
            return bTime - aTime
        })
    }, [bookings])

    const activeBookingsCount = useMemo(
        () => bookingsSorted.filter((booking) => !booking.archived).length,
        [bookingsSorted]
    )

    const archivedBookingsCount = useMemo(
        () => bookingsSorted.filter((booking) => booking.archived).length,
        [bookingsSorted]
    )

    const filteredBookings = useMemo(() => {
        if (bookingsFilter === 'active') {
            return bookingsSorted.filter((booking) => !booking.archived)
        }
        if (bookingsFilter === 'archived') {
            return bookingsSorted.filter((booking) => booking.archived)
        }
        return bookingsSorted
    }, [bookingsSorted, bookingsFilter])

    const bookingsToShow = useMemo(() => {
        const limit = Math.min(filteredBookings.length, bookingsLimit)
        return filteredBookings.slice(0, limit)
    }, [filteredBookings, bookingsLimit])

    const bookingsTotal = filteredBookings.length

    const isShowingAll = bookingsLimit >= filteredBookings.length
    const isLimited = filteredBookings.length > bookingsToShow.length

    const bookingsEmptyMessage = useMemo(() => {
        if (bookingsFilter === 'archived') {
            return 'Архив пуст. Проверьте активные бронирования.'
        }
        if (bookingsFilter === 'all') {
            return 'Нет бронирований.'
        }
        return 'Пока ещё никто не забронировал билеты.'
    }, [bookingsFilter])

    useEffect(() => {
        setBookingsLimit(12)
    }, [bookingsFilter])

    const formatSeatLabel = useCallback((booking) => {
        const seatInfo = booking?.seat_info
        if (seatInfo?.row_number && seatInfo?.seat_number) {
            return `Ряд ${seatInfo.row_number}, место ${seatInfo.seat_number}`
        }
        return `Место ${booking.seat_id}`
    }, [])

    const formatSeanceLabel = useCallback(
        (booking) => {
            const info = booking?.seance_info
            if (!info) {
                return `Сеанс ${booking.seance_id}`
            }
            const filmTitle =
                filmsById.get(info.film_id)?.title || `Фильм ${info.film_id}`
            const hallName =
                hallsById.get(info.hall_id)?.name || `Зал ${info.hall_id}`
            const startLabel = info.start_time
                ? formatBookingDate(info.start_time)
                : '—'
            return `${filmTitle} • ${hallName} • ${startLabel}`
        },
        [filmsById, hallsById]
    )

    if (loading) {
        return <div className="admin-loading">Загрузка...</div>
    }

    if (!isAuthenticated) {
        return (
            <>
                <header className="page-header">
                    <h1 className="page-header__title">
                        Идём<span>в</span>кино
                    </h1>
                    <span className="page-header__subtitle">Администраторррская</span>
                </header>

                <main>
                    <section className="login">
                        <header className="login__header">
                            <h2 className="login__title">Авторизация</h2>
                        </header>
                        <div className="login__wrapper">
                            <form className="login__form" onSubmit={handleLogin}>
                                <label className="login__label">
                                    E-mail
                                    <input
                                        className="login__input"
                                        type="email"
                                        value={loginForm.email}
                                        onChange={(event) =>
                                            setLoginForm((prev) => ({
                                                ...prev,
                                                email: event.target.value,
                                            }))
                                        }
                                        placeholder="example@domain.xyz"
                                        required
                                    />
                                </label>
                                <label className="login__label">
                                    Пароль
                                    <input
                                        className="login__input"
                                        type="password"
                                        value={loginForm.password}
                                        onChange={(event) =>
                                            setLoginForm((prev) => ({
                                                ...prev,
                                                password: event.target.value,
                                            }))
                                        }
                                        placeholder=""
                                        required
                                    />
                                </label>

                                {loginError && (
                                    <div className="login__error">{loginError}</div>
                                )}

                                <div className="text-center">
                                    <button type="submit" className="login__button">
                                        Авторизоваться
                                    </button>
                                </div>
                            </form>

                            {showTestCredentials && (
                                <div className="login__hint">
                                    <strong>Тестовые данные</strong>
                                    <span>Email: admin@example.com</span>
                                    <span>Пароль: admin123</span>
                                </div>
                            )}
                        </div>
                    </section>
                </main>
            </>
        )
    }

    return (
        <div className="admin-page">
            <header className="page-header">
                <h1 className="page-header__title">
                    Идём<span>в</span>кино
                </h1>
                <span className="page-header__subtitle">Администраторррская</span>
                <button className="logout-btn" onClick={handleLogout}>
                    Выйти
                </button>
            </header>

            {feedback && (
                <div className="admin-feedback" role="alert">
                    {feedback}
                </div>
            )}

            <main className="conf-steps">
                <section className="conf-step">
                    <header
                        className={`conf-step__header ${sectionsOpen.halls
                            ? 'conf-step__header_opened'
                            : 'conf-step__header_closed'
                            }`}
                        onClick={() => toggleSection('halls')}
                    >
                        <h2 className="conf-step__title">Управление залами</h2>
                    </header>
                    {sectionsOpen.halls && (
                        <div className="conf-step__wrapper">
                            <p className="conf-step__paragraph">Доступные залы:</p>
                            <ul className="conf-step__list">
                                {halls.map((hall) => (
                                    <li key={hall.id} className="conf-step__hall-item">
                                        <div className="conf-step__hall-info">
                                            <span className="conf-step__hall-title">{hall.name}</span>
                                            <span className="conf-step__hall-id">ID: {hall.id}</span>
                                        </div>
                                        <button
                                            className="conf-step__button conf-step__button-trash"
                                            onClick={() => handleHallDelete(hall.id)}
                                        />
                                    </li>
                                ))}
                            </ul>
                            <button
                                className="conf-step__button conf-step__button-accent"
                                onClick={() => setShowHallForm((prev) => !prev)}
                            >
                                {showHallForm ? 'Отмена' : 'Создать зал'}
                            </button>

                            {showHallForm && (
                                <form className="admin-form conf-step__form" onSubmit={handleCreateHall}>
                                    <div>
                                        <label className="conf-step__label">
                                            Название зала
                                            <input
                                                className="conf-step__input"
                                                type="text"
                                                value={hallForm.name}
                                                onChange={(event) =>
                                                    setHallForm((prev) => ({
                                                        ...prev,
                                                        name: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </div>
                                    <div className="conf-step__legend">
                                        <label className="conf-step__label">
                                            Рядов, шт
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="1"
                                                value={hallForm.rows}
                                                onChange={(event) =>
                                                    setHallForm((prev) => ({
                                                        ...prev,
                                                        rows: Number(event.target.value),
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                        <span className="multiplier">x</span>
                                        <label className="conf-step__label">
                                            Мест, шт
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="1"
                                                value={hallForm.seats_per_row}
                                                onChange={(event) =>
                                                    setHallForm((prev) => ({
                                                        ...prev,
                                                        seats_per_row: Number(event.target.value),
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </div>
                                    <fieldset className="conf-step__buttons text-center">
                                        <button
                                            className="conf-step__button conf-step__button-regular"
                                            type="button"
                                            onClick={() => {
                                                setShowHallForm(false)
                                                setHallForm({
                                                    name: '',
                                                    rows: 10,
                                                    seats_per_row: 10,
                                                    is_active: false,
                                                })
                                            }}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            className="conf-step__button conf-step__button-accent"
                                            type="submit"
                                        >
                                            Сохранить
                                        </button>
                                    </fieldset>
                                </form>
                            )}
                        </div>
                    )}
                </section>

                <section className="conf-step">
                    <header
                        className={`conf-step__header ${sectionsOpen.hallConfig
                            ? 'conf-step__header_opened'
                            : 'conf-step__header_closed'
                            }`}
                        onClick={() => toggleSection('hallConfig')}
                    >
                        <h2 className="conf-step__title">Конфигурация залов</h2>
                    </header>
                    {sectionsOpen.hallConfig && (
                        <div className="conf-step__wrapper">
                            <p className="conf-step__paragraph">
                                Выберите зал для конфигурации:
                            </p>
                            <ul className="conf-step__selectors-box">
                                {halls.map((hall) => (
                                    <li key={hall.id}>
                                        <input
                                            type="radio"
                                            className="conf-step__radio"
                                            name="chairs-hall"
                                            value={hall.id}
                                            checked={hall.id === selectedConfigHallId}
                                            onChange={() => setSelectedConfigHallId(hall.id)}
                                        />
                                        <span className="conf-step__selector">
                                            {hall.name} (ID: {hall.id})
                                        </span>
                                    </li>
                                ))}
                            </ul>

                            {selectedConfigHallId && (
                                <>
                                    <p className="conf-step__paragraph">
                                        Укажите количество рядов и максимальное количество кресел в
                                        ряду:
                                    </p>
                                    <form className="conf-step__legend" onSubmit={handleHallConfigSave}>
                                        <label className="conf-step__label">
                                            Рядов, шт
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="1"
                                                value={hallConfigForm.rows}
                                                onChange={(event) =>
                                                    setHallConfigForm((prev) => ({
                                                        ...prev,
                                                        rows: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                        <span className="multiplier">x</span>
                                        <label className="conf-step__label">
                                            Мест, шт
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="1"
                                                value={hallConfigForm.seats_per_row}
                                                onChange={(event) =>
                                                    setHallConfigForm((prev) => ({
                                                        ...prev,
                                                        seats_per_row: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </form>

                                    <p className="conf-step__paragraph">
                                        Теперь вы можете указать типы кресел на схеме зала:
                                    </p>
                                    <div className="conf-step__legend">
                                        <span className="conf-step__chair conf-step__chair_standart"></span>{' '}
                                        — обычные кресла
                                        <span className="conf-step__chair conf-step__chair_vip"></span>{' '}
                                        — VIP кресла
                                        <span className="conf-step__chair conf-step__chair_disabled"></span>{' '}
                                        — заблокированные (нет кресла)
                                        <p className="conf-step__hint">
                                            Чтобы изменить вид кресла, нажмите по нему левой кнопкой
                                            мыши
                                        </p>
                                    </div>

                                    <div className="conf-step__hall">
                                        <div className="conf-step__hall-wrapper">
                                            {seatGrid.length === 0 && (
                                                <p className="conf-step__hint">
                                                    Для выбранного зала нет загруженных мест. Используйте
                                                    скрипт генерации мест или задайте данные вручную.
                                                </p>
                                            )}
                                            {seatGrid.map((row, rowIndex) => (
                                                <div className="conf-step__row" key={`row-${rowIndex}`}>
                                                    {row.map((seat, seatIndex) => {
                                                        const type = (seat?.seat_type || 'standart').toLowerCase()
                                                        const className = `conf-step__chair ${seatTypeClassMap[type] || seatTypeClassMap.standart
                                                            }`
                                                        return (
                                                            <span
                                                                key={`seat-${rowIndex}-${seatIndex}`}
                                                                className={className}
                                                                onClick={() => seat && handleSeatToggle(seat)}
                                                            />
                                                        )
                                                    })}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <fieldset className="conf-step__buttons text-center">
                                        <button
                                            className="conf-step__button conf-step__button-regular"
                                            type="button"
                                            onClick={() => {
                                                setShowHallForm(false)
                                                setHallForm({
                                                    name: '',
                                                    rows: 10,
                                                    seats_per_row: 10,
                                                    is_active: false,
                                                })
                                            }}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            className="conf-step__button conf-step__button-accent"
                                            type="submit"
                                        >
                                            Сохранить
                                        </button>
                                    </fieldset>
                                </>
                            )}
                        </div>
                    )}
                </section>

                <section className="conf-step">
                    <header
                        className={`conf-step__header ${sectionsOpen.prices
                            ? 'conf-step__header_opened'
                            : 'conf-step__header_closed'
                            }`}
                        onClick={() => toggleSection('prices')}
                    >
                        <h2 className="conf-step__title">Конфигурация цен</h2>
                    </header>
                    {sectionsOpen.prices && (
                        <div className="conf-step__wrapper">
                            <p className="conf-step__paragraph">
                                Выберите зал для конфигурации:
                            </p>
                            <ul className="conf-step__selectors-box">
                                {halls.map((hall) => (
                                    <li key={hall.id}>
                                        <input
                                            type="radio"
                                            className="conf-step__radio"
                                            name="prices-hall"
                                            value={hall.id}
                                            checked={hall.id === selectedPriceHallId}
                                            onChange={() => setSelectedPriceHallId(hall.id)}
                                        />
                                        <span className="conf-step__selector">
                                            {hall.name} (ID: {hall.id})
                                        </span>
                                    </li>
                                ))}
                            </ul>

                            {selectedPriceHallId && (
                                <form onSubmit={handlePriceSave}>
                                    <p className="conf-step__paragraph">
                                        Установите цены для типов кресел:
                                    </p>
                                    <div className="conf-step__legend">
                                        <label className="conf-step__label">
                                            Цена, рублей
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="0"
                                                step="1"
                                                value={priceForm.standard}
                                                onChange={(event) =>
                                                    setPriceForm((prev) => ({
                                                        ...prev,
                                                        standard: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                        за{' '}
                                        <span className="conf-step__chair conf-step__chair_standart"></span>{' '}
                                        обычные кресла
                                    </div>
                                    <div className="conf-step__legend">
                                        <label className="conf-step__label">
                                            Цена, рублей
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="0"
                                                step="1"
                                                value={priceForm.vip}
                                                onChange={(event) =>
                                                    setPriceForm((prev) => ({
                                                        ...prev,
                                                        vip: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                        за{' '}
                                        <span className="conf-step__chair conf-step__chair_vip"></span>{' '}
                                        VIP кресла
                                    </div>
                                    <fieldset className="conf-step__buttons text-center">
                                        <button
                                            className="conf-step__button conf-step__button-regular"
                                            type="button"
                                            onClick={() => {
                                                const hallSeances = seances.filter(
                                                    (seance) => seance.hall_id === selectedPriceHallId
                                                )
                                                if (hallSeances.length > 0) {
                                                    setPriceForm({
                                                        standard: String(hallSeances[0].price_standard ?? ''),
                                                        vip: String(hallSeances[0].price_vip ?? ''),
                                                    })
                                                }
                                            }}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            className="conf-step__button conf-step__button-accent"
                                            type="submit"
                                        >
                                            Сохранить
                                        </button>
                                    </fieldset>
                                </form>
                            )}
                        </div>
                    )}
                </section>

                <section className="conf-step">
                    <header
                        className={`conf-step__header ${sectionsOpen.seances
                            ? 'conf-step__header_opened'
                            : 'conf-step__header_closed'
                            }`}
                        onClick={() => toggleSection('seances')}
                    >
                        <h2 className="conf-step__title">Сетка сеансов</h2>
                    </header>
                    {sectionsOpen.seances && (
                        <div className="conf-step__wrapper">
                            <p className="conf-step__paragraph">
                                <button
                                    className="conf-step__button conf-step__button-accent"
                                    onClick={() => setShowFilmForm((prev) => !prev)}
                                >
                                    {showFilmForm ? 'Закрыть форму' : 'Добавить фильм'}
                                </button>
                            </p>

                            {showFilmForm && (
                                <form className="admin-form conf-step__form" onSubmit={handleCreateFilm}>
                                    <div>
                                        <label className="conf-step__label">
                                            Название фильма
                                            <input
                                                className="conf-step__input"
                                                type="text"
                                                value={filmForm.title}
                                                onChange={(event) =>
                                                    setFilmForm((prev) => ({
                                                        ...prev,
                                                        title: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </div>
                                    <div>
                                        <label className="conf-step__label">
                                            Длительность (минуты)
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="1"
                                                value={filmForm.duration}
                                                onChange={(event) =>
                                                    setFilmForm((prev) => ({
                                                        ...prev,
                                                        duration: Number(event.target.value),
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </div>
                                    <div>
                                        <label className="conf-step__label">
                                            Описание
                                            <textarea
                                                className="conf-step__textarea"
                                                value={filmForm.description}
                                                onChange={(event) =>
                                                    setFilmForm((prev) => ({
                                                        ...prev,
                                                        description: event.target.value,
                                                    }))
                                                }
                                                rows={3}
                                            />
                                        </label>
                                    </div>
                                    <div>
                                        <label className="conf-step__label">
                                            URL постера
                                            <input
                                                className="conf-step__input"
                                                type="url"
                                                value={filmForm.poster_url}
                                                onChange={(event) =>
                                                    setFilmForm((prev) => ({
                                                        ...prev,
                                                        poster_url: event.target.value,
                                                    }))
                                                }
                                            />
                                        </label>
                                    </div>
                                    <fieldset className="conf-step__buttons text-center">
                                        <button
                                            className="conf-step__button conf-step__button-regular"
                                            type="button"
                                            onClick={() => {
                                                setShowFilmForm(false)
                                                setFilmForm({
                                                    title: '',
                                                    description: '',
                                                    duration: 120,
                                                    poster_url: '',
                                                })
                                            }}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            className="conf-step__button conf-step__button-accent"
                                            type="submit"
                                        >
                                            Сохранить
                                        </button>
                                    </fieldset>
                                </form>
                            )}

                            <div className="conf-step__movies">
                                {films.map((film) => {
                                    const posterSrc =
                                        film.poster_url && film.poster_url.trim() !== ''
                                            ? film.poster_url.trim()
                                            : fallbackPoster
                                    return (
                                        <div className="conf-step__movie" key={film.id}>
                                            <img
                                                className="conf-step__movie-poster"
                                                alt={film.title}
                                                src={posterSrc}
                                                onError={(event) => {
                                                    event.currentTarget.src = fallbackPoster
                                                    event.currentTarget.onerror = null
                                                }}
                                            />
                                            <h3 className="conf-step__movie-title">{film.title}</h3>
                                            <p className="conf-step__movie-duration">
                                                {film.duration} минут
                                            </p>
                                            <button
                                                className="conf-step__button conf-step__button-trash"
                                                onClick={() => handleFilmDelete(film.id)}
                                                title="Удалить фильм"
                                            ></button>
                                        </div>
                                    )
                                })}
                                {films.length === 0 && (
                                    <p className="conf-step__hint">
                                        Добавьте фильмы, чтобы формировать расписание.
                                    </p>
                                )}
                            </div>

                            <div className="conf-step__seances">
                                {halls.map((hall) => {
                                    const blocks =
                                        timelineBlocksByHall.get(hall.id) || []
                                    return (
                                        <div
                                            className="conf-step__seances-hall"
                                            key={`timeline-hall-${hall.id}`}
                                        >
                                            <h3 className="conf-step__seances-title">
                                                {hall.name}
                                            </h3>
                                            <div className="conf-step__seances-timeline">
                                                {blocks.map((block) => (
                                                    <div
                                                        key={block.id}
                                                        className="conf-step__seances-movie"
                                                        style={{
                                                            width: `${block.width}px`,
                                                            left: `${block.left}px`,
                                                            backgroundColor:
                                                                block.color ||
                                                                '#caff85',
                                                        }}
                                                    >
                                                        <p className="conf-step__seances-movie-title">
                                                            {block.title}
                                                        </p>
                                                        <p className="conf-step__seances-movie-start">
                                                            {block.startLabel}
                                                        </p>
                                                    </div>
                                                ))}
                                                {blocks.length === 0 && (
                                                    <p className="conf-step__hint">
                                                        В этом зале пока нет сеансов. Добавьте новый сеанс ниже.
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>

                            <button
                                className="conf-step__button conf-step__button-accent"
                                onClick={() => {
                                    setSeanceFormError('')
                                    setShowSeanceForm((prev) => !prev)
                                }}
                            >
                                {showSeanceForm ? 'Закрыть форму сеанса' : 'Добавить сеанс'}
                            </button>
                            {seanceFormError && !showSeanceForm && (
                                <p
                                    className="conf-step__form-error"
                                    role="alert"
                                    aria-live="assertive"
                                >
                                    {seanceFormError}
                                </p>
                            )}

                            {showSeanceForm && (
                                <form className="admin-form conf-step__form" onSubmit={handleCreateSeance}>
                                    <div>
                                        <label className="conf-step__label">
                                            Фильм
                                            <select
                                                className="conf-step__input"
                                                value={seanceForm.film_id}
                                                onChange={(event) =>
                                                    setSeanceForm((prev) => ({
                                                        ...prev,
                                                        film_id: event.target.value,
                                                    }))
                                                }
                                                required
                                            >
                                                <option value="">Выберите фильм</option>
                                                {films.map((film) => (
                                                    <option key={film.id} value={film.id}>
                                                        {film.title}
                                                    </option>
                                                ))}
                                            </select>
                                        </label>
                                    </div>
                                    <div>
                                        <label className="conf-step__label">
                                            Зал
                                            <select
                                                className="conf-step__input"
                                                value={seanceForm.hall_id}
                                                onChange={(event) =>
                                                    setSeanceForm((prev) => ({
                                                        ...prev,
                                                        hall_id: event.target.value,
                                                    }))
                                                }
                                                required
                                            >
                                                <option value="">Выберите зал</option>
                                                {halls.map((hall) => (
                                                    <option key={hall.id} value={hall.id}>
                                                        {hall.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </label>
                                    </div>
                                    <div>
                                        <label className="conf-step__label">
                                            Дата и время начала
                                            <input
                                                className="conf-step__input"
                                                type="datetime-local"
                                                value={seanceForm.start_time}
                                                onChange={(event) =>
                                                    setSeanceForm((prev) => ({
                                                        ...prev,
                                                        start_time: event.target.value,
                                                    }))
                                                }
                                                required
                                            />
                                        </label>
                                    </div>
                                    <div className="conf-step__legend">
                                        <label className="conf-step__label">
                                            Цена стандарт
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="0"
                                                step="1"
                                                value={seanceForm.price_standard}
                                                onChange={(event) =>
                                                    setSeanceForm((prev) => ({
                                                        ...prev,
                                                        price_standard: event.target.value,
                                                    }))
                                                }
                                                placeholder="По умолчанию, как в зале"
                                            />
                                        </label>
                                        <label className="conf-step__label">
                                            Цена VIP
                                            <input
                                                className="conf-step__input"
                                                type="number"
                                                min="0"
                                                step="1"
                                                value={seanceForm.price_vip}
                                                onChange={(event) =>
                                                    setSeanceForm((prev) => ({
                                                        ...prev,
                                                        price_vip: event.target.value,
                                                    }))
                                                }
                                                placeholder="По умолчанию, как в зале"
                                            />
                                        </label>
                                    </div>
                                    {seanceFormError && (
                                        <div
                                            className="conf-step__alert conf-step__alert_error conf-step__form-error"
                                            role="alert"
                                            aria-live="assertive"
                                        >
                                            {seanceFormError}
                                        </div>
                                    )}
                                    <fieldset className="conf-step__buttons text-center">
                                        <button
                                            className="conf-step__button conf-step__button-regular"
                                            type="button"
                                            onClick={() => {
                                                setShowSeanceForm(false)
                                                setSeanceFormError('')
                                                setSeanceForm({
                                                    film_id: '',
                                                    hall_id: '',
                                                    start_time: '',
                                                    price_standard: '',
                                                    price_vip: '',
                                                })
                                            }}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            className="conf-step__button conf-step__button-accent"
                                            type="submit"
                                        >
                                            Сохранить
                                        </button>
                                    </fieldset>
                                </form>
                            )}

                            {seances.length > 0 && (
                                <div className="admin-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>ID</th>
                                                <th>Фильм</th>
                                                <th>Зал</th>
                                                <th>Время</th>
                                                <th>Стандарт</th>
                                                <th>VIP</th>
                                                <th></th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {seances.map((seance) => {
                                                const film = filmsById.get(seance.film_id)
                                                const hall = halls.find((h) => h.id === seance.hall_id)
                                                return (
                                                    <tr key={`seance-row-${seance.id}`}>
                                                        <td>{seance.id}</td>
                                                        <td>{film?.title || `Фильм #${seance.film_id}`}</td>
                                                        <td>{hall?.name || `Зал #${seance.hall_id}`}</td>
                                                        <td>{formatBookingDate(seance.start_time)}</td>
                                                        <td>{seance.price_standard} ₽</td>
                                                        <td>{seance.price_vip} ₽</td>
                                                        <td>
                                                            <button
                                                                className="conf-step__button conf-step__button-trash"
                                                                onClick={() => handleSeanceDelete(seance.id)}
                                                            ></button>
                                                        </td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}
                </section>

                <section className="conf-step">
                    <header
                        className={`conf-step__header ${sectionsOpen.sales
                            ? 'conf-step__header_opened'
                            : 'conf-step__header_closed'
                            }`}
                        onClick={() => toggleSection('sales')}
                    >
                        <h2 className="conf-step__title">Открыть продажи</h2>
                    </header>
                    {sectionsOpen.sales && (
                        <div className="conf-step__wrapper text-center">
                            <p className="conf-step__paragraph">
                                Всё готово, теперь можно:
                            </p>
                            <button
                                className="conf-step__button conf-step__button-accent"
                                onClick={handleOpenSales}
                            >
                                {allHallsActive
                                    ? 'Приостановить продажу билетов'
                                    : 'Открыть продажу билетов'}
                            </button>

                            {salesStatus && (
                                <div
                                    className={`conf-step__alert conf-step__alert_${salesStatus.type}`}
                                >
                                    {salesStatus.message}
                                    {salesStatus.type === 'success' && (
                                        <div className="conf-step__actions">
                                            <button
                                                className="conf-step__button conf-step__button-regular"
                                                onClick={() => navigate('/')}
                                            >
                                                Перейти к бронированию
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="conf-step__bookings">
                                <h3 className="conf-step__bookings-title">
                                    Последние бронирования
                                </h3>
                                <div className="conf-step__bookings-controls">
                                    <span>
                                        {bookingsFilter === 'archived'
                                            ? `Архив: ${archivedBookingsCount}`
                                            : bookingsFilter === 'all'
                                                ? `Всего: ${bookingsSorted.length}`
                                                : `Активные: ${activeBookingsCount}`}
                                    </span>
                                    <div className="conf-step__bookings-tools">
                                        <div className="conf-step__bookings-filters">
                                            <button
                                                type="button"
                                                className={`conf-step__button conf-step__button-regular${bookingsFilter === 'active'
                                                    ? ' conf-step__button-regular--active'
                                                    : ''
                                                    }`}
                                                onClick={() => setBookingsFilter('active')}
                                            >
                                                Активные ({activeBookingsCount})
                                            </button>
                                            <button
                                                type="button"
                                                className={`conf-step__button conf-step__button-regular${bookingsFilter === 'archived'
                                                    ? ' conf-step__button-regular--active'
                                                    : ''
                                                    }`}
                                                onClick={() => setBookingsFilter('archived')}
                                            >
                                                Архив ({archivedBookingsCount})
                                            </button>
                                            <button
                                                type="button"
                                                className={`conf-step__button conf-step__button-regular${bookingsFilter === 'all'
                                                    ? ' conf-step__button-regular--active'
                                                    : ''
                                                    }`}
                                                onClick={() => setBookingsFilter('all')}
                                            >
                                                Все ({bookingsSorted.length})
                                            </button>
                                        </div>
                                        <div className="conf-step__bookings-actions">
                                            {!isShowingAll && (
                                                <button
                                                    className="conf-step__button conf-step__button-regular"
                                                    onClick={() => setBookingsLimit(filteredBookings.length)}
                                                >
                                                    Показать все
                                                </button>
                                            )}
                                            {bookingsLimit > 12 && (
                                                <button
                                                    className="conf-step__button conf-step__button-regular"
                                                    onClick={() => setBookingsLimit(12)}
                                                >
                                                    Свернуть
                                                </button>
                                            )}
                                            <button
                                                className="conf-step__button conf-step__button-regular"
                                                onClick={() => loadAllData()}
                                                disabled={dataLoading}
                                            >
                                                Обновить данные
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                {bookingsToShow.length === 0 ? (
                                    <p className="conf-step__hint">{bookingsEmptyMessage}</p>
                                ) : (
                                    <ul className="conf-step__bookings-list">
                                        {bookingsToShow.map((booking) => {
                                            const isArchiving = archivingTicketIds.includes(
                                                booking.id
                                            )
                                            return (
                                                <li
                                                    key={`booking-${booking.id}`}
                                                    className={`conf-step__bookings-item${booking.archived
                                                        ? ' conf-step__bookings-item_archived'
                                                        : ''
                                                        }`}
                                                >
                                                    <div className="conf-step__bookings-item-info">
                                                        <div className="conf-step__bookings-item-headline">
                                                            <strong>{booking.booking_code}</strong>
                                                            {booking.archived && (
                                                                <span className="conf-step__booking-tag">
                                                                    Архив
                                                                </span>
                                                            )}
                                                        </div>
                                                        <div className="conf-step__bookings-item-details">
                                                            {formatSeanceLabel(booking)} •{' '}
                                                            {formatSeatLabel(booking)} •{' '}
                                                            {formatBookingDate(
                                                                booking.created_at
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="conf-step__bookings-item-actions">
                                                        <button
                                                            type="button"
                                                            className="conf-step__button conf-step__button-regular"
                                                            onClick={() =>
                                                                handleArchiveToggle(
                                                                    booking.id,
                                                                    !booking.archived
                                                                )
                                                            }
                                                            disabled={isArchiving}
                                                        >
                                                            {booking.archived
                                                                ? 'Вернуть'
                                                                : 'В архив'}
                                                        </button>
                                                    </div>
                                                </li>
                                            )
                                        })}
                                    </ul>
                                )}
                                {isLimited && bookingsLimit === 12 && (
                                    <p className="conf-step__hint">
                                        Показаны последние {bookingsToShow.length} из{' '}
                                        {bookingsTotal} бронирований.
                                    </p>
                                )}
                            </div>
                        </div>
                    )}
                </section>
            </main>

            {dataLoading && (
                <div className="admin-loading-inline">Обновляем данные…</div>
            )}
        </div>
    )
}

export default Admin
