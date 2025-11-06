import { useState, useEffect } from 'react'
import api from '../services/api'
import DayNavigation from '../components/DayNavigation'
import FilmCard from '../components/FilmCard'

function Home() {
    const [films, setFilms] = useState([])
    const [seances, setSeances] = useState([])
    const [selectedDate, setSelectedDate] = useState(new Date())
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadData()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        // При изменении даты перезагружаем сеансы
        if (!loading) {
            loadSeances()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedDate])

    const loadData = async () => {
        setLoading(true)
        try {
            await Promise.all([
                loadFilms(),
                loadSeances()
            ])
        } catch (error) {
            console.error('Ошибка загрузки данных:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadFilms = async () => {
        try {
            console.log('Запрос фильмов к:', `${api.baseURL}/api/v1/film`)
            const response = await api.getFilms()
            console.log('API ответ для фильмов:', response)
            // API возвращает {films: [...]}
            const filmsData = response.films || response || []
            console.log('Загружено фильмов:', filmsData.length)
            setFilms(filmsData)
        } catch (error) {
            console.error('Ошибка загрузки фильмов:', error)
            console.error('Детали ошибки:', {
                message: error.message,
                status: error.status,
                stack: error.stack
            })
            setFilms([])
        }
    }

    const loadSeances = async () => {
        try {
            console.log('Запрос сеансов к:', `${api.baseURL}/api/v1/seance`)
            const response = await api.getSeances()
            console.log('API ответ для сеансов:', response)
            // API возвращает {seances: [...]}
            const allSeances = response.seances || response || []
            console.log('Всего сеансов загружено:', allSeances.length)

            if (selectedDate) {
                const selectedDateStr = selectedDate.toISOString().split('T')[0]
                console.log('Выбранная дата:', selectedDateStr)

                const filteredSeances = allSeances.filter(seance => {
                    if (!seance.start_time) {
                        console.log('Сеанс без start_time:', seance)
                        return false
                    }
                    const seanceDate = new Date(seance.start_time).toISOString().split('T')[0]
                    console.log('Дата сеанса:', seanceDate, 'Сеанс:', seance)
                    return seanceDate === selectedDateStr
                })
                console.log('Отфильтровано сеансов на выбранную дату:', filteredSeances.length)

                // Если на выбранную дату нет сеансов, показываем все доступные сеансы
                // чтобы пользователь мог увидеть, какие фильмы вообще есть
                if (filteredSeances.length === 0) {
                    console.log('На выбранную дату нет сеансов, показываем все доступные сеансы')
                    setSeances(allSeances)
                } else {
                    setSeances(filteredSeances)
                }
            } else {
                setSeances(allSeances)
            }
        } catch (error) {
            console.error('Ошибка загрузки сеансов:', error)
            console.error('Детали ошибки:', {
                message: error.message,
                status: error.status,
                stack: error.stack
            })
            setSeances([])
        }
    }

    const handleDateChange = (date) => {
        setSelectedDate(date)
    }

    if (loading) {
        return (
            <div className="home">
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    Загрузка...
                </div>
            </div>
        )
    }

    // Фильтруем фильмы, у которых есть сеансы
    console.log('Фильмов всего:', films.length)
    console.log('Сеансов загружено:', seances.length)

    const filmsWithSeances = films.filter(film => {
        const hasSeances = seances.some(seance => seance.film_id === film.id)
        if (hasSeances) {
            console.log('Фильм', film.title, 'имеет сеансы')
        }
        return hasSeances
    })

    console.log('Фильмов с сеансами:', filmsWithSeances.length)

    return (
        <>
            <DayNavigation
                selectedDate={selectedDate}
                onDateChange={handleDateChange}
            />
            {/* Временная отладка */}
            {filmsWithSeances.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <p>На выбранную дату нет доступных сеансов</p>
                    {import.meta.env.DEV && (
                        <details style={{ marginTop: '1rem', textAlign: 'left', display: 'inline-block' }}>
                            <summary>Детали отладки</summary>
                            <pre style={{ background: '#f5f5f5', padding: '1rem', marginTop: '0.5rem' }}>
                                Фильмов загружено: {films.length}
                                Сеансов загружено: {seances.length}
                                Выбранная дата: {selectedDate?.toISOString().split('T')[0]}
                            </pre>
                        </details>
                    )}
                </div>
            ) : (
                filmsWithSeances.map(film => (
                    <FilmCard
                        key={film.id}
                        film={film}
                        seances={seances}
                        selectedDate={selectedDate}
                    />
                ))
            )}
        </>
    )
}

export default Home