import { Link } from 'react-router-dom'

// eslint-disable-next-line no-unused-vars
function FilmCard({ film, seances, selectedDate }) {
    // ВРЕМЕННО: Фильтруем сеансы только по фильму, без фильтрации по дате
    // Это нужно для тестирования, когда на выбранную дату нет сеансов
    // TODO: Вернуть фильтрацию по дате после тестирования (использовать selectedDate)
    const filmSeances = seances.filter(seance => {
        if (seance.film_id !== film.id) return false
        // Временно убрана фильтрация по дате
        // if (!selectedDate) return true
        // const seanceDate = new Date(seance.start_time).toISOString().split('T')[0]
        // const selectedDateStr = selectedDate.toISOString().split('T')[0]
        // return seanceDate === selectedDateStr
        return true
    })

    // Группируем сеансы по залам
    const seancesByHall = {}
    filmSeances.forEach(seance => {
        const hallName = seance.hall?.name || `Зал ${seance.hall_id}`
        if (!seancesByHall[hallName]) {
            seancesByHall[hallName] = []
        }
        seancesByHall[hallName].push(seance)
    })

    // Форматируем время для отображения (HH:MM)
    const formatTime = (dateTime) => {
        const date = new Date(dateTime)
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${hours}:${minutes}`
    }

    // Если нет сеансов, не показываем фильм
    if (filmSeances.length === 0) return null

    return (
        <section className="movie">
            <div className="movie__info">
                <div className="movie__poster">
                    <img
                        className="movie__poster-image"
                        alt={`${film.title} постер`}
                        src={film.poster_url || '/src/assets/layouts/client/i/poster1.jpg'}
                        onError={(e) => {
                            e.target.src = '/src/assets/layouts/client/i/poster1.jpg'
                        }}
                    />
                </div>
                <div className="movie__description">
                    <h2 className="movie__title">{film.title}</h2>
                    {film.description && (
                        <p className="movie__synopsis">{film.description}</p>
                    )}
                    <p className="movie__data">
                        <span className="movie__data-duration">{film.duration} минут</span>
                    </p>
                </div>
            </div>

            {Object.entries(seancesByHall).map(([hallName, hallSeances]) => (
                <div key={hallName} className="movie-seances__hall">
                    <h3 className="movie-seances__hall-title">{hallName}</h3>
                    <ul className="movie-seances__list">
                        {hallSeances.map(seance => (
                            <li key={seance.id} className="movie-seances__time-block">
                                <Link
                                    to={`/hall/${seance.id}`}
                                    className="movie-seances__time"
                                >
                                    {formatTime(seance.start_time)}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </section>
    )
}

export default FilmCard

