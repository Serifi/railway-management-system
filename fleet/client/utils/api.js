import axios from 'axios'

// Axios instance with a base URL and Headers
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor to include the authorization token
apiClient.interceptors.request.use(
    (config) => {
        if (typeof window !== 'undefined') {
            // Get token from local storage
            const token = localStorage.getItem('auth_token')
            // Attach token to headers
            if (token) config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor to handle Unauthorized errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            if (typeof window !== 'undefined') {
                localStorage.removeItem('auth_token') // Remove token
                window.location.href = '/' // Redirect to the login page
            }
        }
        return Promise.reject(error)
    }
)

// Export the Axios instance
export default apiClient