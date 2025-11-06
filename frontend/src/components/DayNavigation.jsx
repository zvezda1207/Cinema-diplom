import { Link } from 'react-router-dom'

function DayNavigation({ selectedDate, onDateChange }) {
    // Генерируем 7 дней (сегодня + 6 дней вперед)
    const days = []
    const today = new Date()

    for (let i = 0; i < 7; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)

        const dayOfWeek = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'][date.getDay()]
        const dayNumber = date.getDate()
        const isWeekend = date.getDay() === 0 || date.getDay() === 6
        const isToday = i === 0
        const isSelected = selectedDate &&
            date.toISOString().split('T')[0] === selectedDate.toISOString().split('T')[0]

        days.push({
            date,
            dayOfWeek,
            dayNumber,
            isWeekend,
            isToday,
            isSelected
        })
    }

    // Форматируем дату для API (YYYY-MM-DD)
    const formatDateForAPI = (date) => {
        return date.toISOString().split('T')[0]
    }

    return (
        <nav className="page-nav">
            {days.map((day, index) => {
                const dateStr = formatDateForAPI(day.date)
                const classes = [
                    'page-nav__day',
                    day.isToday && 'page-nav__day_today',
                    day.isSelected && 'page-nav__day_chosen',
                    day.isWeekend && 'page-nav__day_weekend'
                ].filter(Boolean).join(' ')

                return (
                    <a
                        key={index}
                        href="#"
                        className={classes}
                        onClick={(e) => {
                            e.preventDefault()
                            onDateChange(day.date)
                        }}
                    >
                        <span className="page-nav__day-week">{day.dayOfWeek}</span>
                        <span className="page-nav__day-number">{day.dayNumber}</span>
                    </a>
                )
            })}
            <a className="page-nav__day page-nav__day_next" href="#"></a>
        </nav>
    )
}

export default DayNavigation

