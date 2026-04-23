import axios from 'axios'

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api/'
const normalizedBaseUrl = rawBaseUrl.endsWith('/') ? rawBaseUrl : `${rawBaseUrl}/`

const client = axios.create({
  baseURL: normalizedBaseUrl,
  timeout: 10000,
})

export default client
