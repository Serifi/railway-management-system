import axios from 'axios'

// Erstellen der Axios-Instanz
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    headers: {
        'Content-Type': 'application/json'
    }
})

apiClient.interceptors.request.use(
    (config) => {
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('auth_token')
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            if (typeof window !== 'undefined') { // Sicherstellen, dass wir auf der Client-Seite sind
                // Token entfernen und Benutzer zur Login-Seite umleiten
                localStorage.removeItem('auth_token')
                window.location.href = '/'
            }
        }
        return Promise.reject(error)
    }
)

export default apiClient
