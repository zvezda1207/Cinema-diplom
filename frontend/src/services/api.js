// В development используем относительный путь через Vite proxy
// В production используем переменную окружения или полный URL
const API_BASE_URL = import.meta.env.VITE_API_URL ||
    (import.meta.env.DEV ? '' : 'http://localhost:8000')

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL
        this.token = localStorage.getItem('token')
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'x-token': this.token }),
                ...options.headers,
            },
        }

        // Добавляем body только для POST, PATCH, PUT
        if (options.body && ['POST', 'PATCH', 'PUT'].includes(config.method)) {
            config.body = options.body
        }

        try {
            const requestStart = Date.now()
            console.log(`[API] ${config.method} ${url} - START`)
            const response = await fetch(url, config)
            const requestTime = Date.now() - requestStart
            console.log(`[API] ${config.method} ${url} - ${response.status} (${requestTime}ms)`)

            // Клонируем response для чтения ошибки, чтобы не потерять оригинал
            const responseClone = response.clone()

            if (!response.ok) {
                // Пытаемся получить детали ошибки от сервера
                let errorMessage = `HTTP error! status: ${response.status}`
                try {
                    const errorData = await responseClone.json()
                    console.error('API Error Response:', errorData)
                    errorMessage = errorData.detail || errorData.message || errorMessage
                } catch {
                    try {
                        const errorText = await responseClone.text()
                        console.error('API Error Text:', errorText)
                        errorMessage = errorText || errorMessage
                    } catch {
                        // Если не удалось прочитать body, используем дефолтное сообщение
                        console.error('API Error: Could not read error response body')
                    }
                }
                const error = new Error(errorMessage)
                error.status = response.status
                error.response = response
                throw error
            }
            return await response.json()
        } catch (error) {
            // Если это уже наша ошибка, просто пробрасываем дальше
            if (error.status) {
                console.error('API request failed:', {
                    url,
                    method: config.method,
                    error: error.message,
                    status: error.status
                })
                throw error
            }
            // Если это сетевая ошибка или другая
            console.error('API request failed:', {
                url,
                method: config.method,
                error: error.message,
                status: undefined
            })
            throw error
        }
    }

    // Публичные методы (без авторизации)
    async getFilms() {
        return this.request('/api/v1/film')
    }

    async getFilm(filmId) {
        return this.request(`/api/v1/film/${filmId}`)
    }

    async getHalls() {
        return this.request('/api/v1/hall')
    }

    async getSeats(params = {}) {
        // Формируем query параметры
        const queryParams = new URLSearchParams()
        if (params.hall_id) queryParams.append('hall_id', params.hall_id)
        if (params.row_number) queryParams.append('row_number', params.row_number)
        if (params.seat_number) queryParams.append('seat_number', params.seat_number)
        if (params.seat_type) queryParams.append('seat_type', params.seat_type)

        const queryString = queryParams.toString()
        const endpoint = queryString ? `/api/v1/seat?${queryString}` : '/api/v1/seat'
        return this.request(endpoint)
    }

    async getSeance(seanceId) {
        return this.request(`/api/v1/seance/${seanceId}`)
    }

    async getSeances() {
        return this.request('/api/v1/seance')
    }

    async getTicket(ticketId) {
        return this.request(`/api/v1/ticket/${ticketId}`)
    }

    async getPrices() {
        return this.request('/api/v1/price')
    }

    async getAvailableSeats(seanceId) {
        return this.request(`/api/v1/seance/${seanceId}/available-seats`)
    }

    async bookTicket(booking) {
        return this.request('/api/v1/ticket/booking', {
            method: 'POST',
            body: JSON.stringify(booking)
        })
    }

    async createUser(userData) {
        return this.request('/api/v1/user', {
            method: 'POST',
            body: JSON.stringify(userData)
        })
    }

    // Админ методы (с авторизацией)
    async updateUser(userId, userData) {
        return this.request(`/api/v1/user/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify(userData)
        })
    }

    async getUser(userId) {
        return this.request(`/api/v1/user/${userId}`)
    }

    async getUsers() {
        return this.request('/api/v1/user')
    }

    async deleteUser(userId) {
        return this.request(`/api/v1/user/${userId}`, { method: 'DELETE' })
    }

    async login(email, password) {
        const response = await this.request('/api/v1/user/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        })
        this.token = response.token
        localStorage.setItem('token', this.token)
        return response
    }

    async createHall(hallData) {
        return this.request('/api/v1/hall', {
            method: 'POST',
            body: JSON.stringify(hallData)
        })
    }

    async updateHall(hallId, hallData) {
        return this.request(`/api/v1/hall/${hallId}`, {
            method: 'PATCH',
            body: JSON.stringify(hallData)
        })
    }

    async getHall(hallId) {
        return this.request(`/api/v1/hall/${hallId}`)
    }

    async deleteHall(hallId) {
        return this.request(`/api/v1/hall/${hallId}`, { method: 'DELETE' })
    }

    async createSeat(seatData) {
        return this.request('/api/v1/seat', {
            method: 'POST',
            body: JSON.stringify(seatData)
        })
    }

    async updateSeat(seatId, seatData) {
        return this.request(`/api/v1/seat/${seatId}`, {
            method: 'PATCH',
            body: JSON.stringify(seatData)
        })
    }

    async deleteSeat(seatId) {
        return this.request(`/api/v1/seat/${seatId}`, { method: 'DELETE' })
    }

    async getSeat(seatId) {
        return this.request(`/api/v1/seat/${seatId}`)
    }

    async createFilm(filmData) {
        return this.request('/api/v1/film', {
            method: 'POST',
            body: JSON.stringify(filmData)
        })
    }

    async updateFilm(filmId, filmData) {
        return this.request(`/api/v1/film/${filmId}`, {
            method: 'PATCH',
            body: JSON.stringify(filmData)
        })
    }

    async deletefilm(filmId) {
        return this.request(`/api/v1/film/${filmId}`, { method: 'DELETE' })
    }

    async createSeance(seanceData) {
        return this.request('/api/v1/seance', {
            method: 'POST',
            body: JSON.stringify(seanceData)
        })
    }

    async updateSeance(seanceId, seanceData) {
        return this.request(`/api/v1/seance/${seanceId}`, {
            method: 'PATCH',
            body: JSON.stringify(seanceData)
        })
    }

    async deleteSeance(seanceId) {
        return this.request(`/api/v1/seance/${seanceId}`, { method: 'DELETE' })
    }

    async createTicket(ticketData) {
        return this.request('/api/v1/ticket', {
            method: 'POST',
            body: JSON.stringify(ticketData)
        })
    }

    async updateTicket(ticketId, ticketData) {
        return this.request(`/api/v1/ticket/${ticketId}`, {
            method: 'PATCH',
            body: JSON.stringify(ticketData)
        })
    }

    async deleteTicket(ticketId) {
        return this.request(`/api/v1/ticket/${ticketId}`, { method: 'DELETE' })
    }

    async setTicketArchived(ticketId, archived) {
        return this.request(`/api/v1/ticket/${ticketId}/archive`, {
            method: 'PATCH',
            body: JSON.stringify({ archived })
        })
    }

    async createPrice(priceData) {
        return this.request('/api/v1/price', {
            method: 'POST',
            body: JSON.stringify(priceData)
        })
    }

    async updatePrice(priceId, priceData) {
        return this.request(`/api/v1/price/${priceId}`, {
            method: 'PATCH',
            body: JSON.stringify(priceData)
        })
    }

    async getPrice(priceId) {
        return this.request(`/api/v1/price/${priceId}`)
    }

    async deletePrice(priceId) {
        return this.request(`/api/v1/price/${priceId}`, { method: 'DELETE' })
    }

    async getAllBookings(params = {}) {
        const queryParams = new URLSearchParams()
        if (params.include_archived !== undefined) {
            queryParams.set('include_archived', params.include_archived ? 'true' : 'false')
        }
        if (params.archived !== undefined && params.archived !== null) {
            queryParams.set('archived', params.archived ? 'true' : 'false')
        }
        const queryString = queryParams.toString()
        const endpoint = queryString ? `/api/v1/tickets?${queryString}` : '/api/v1/tickets'
        return this.request(endpoint)
    }
}

export default new ApiService()