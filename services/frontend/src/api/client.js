import axios from 'axios'

const AUTH_URL = 'http://localhost:8000'
const USER_URL = 'http://localhost:8001'
const PRODUCT_URL = 'http://localhost:8002'
const ORDER_URL = 'http://localhost:8003'
const CHAT_URL = 'http://localhost:8005'

function makeClient(baseURL) {
  const client = axios.create({ baseURL })
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })
  return client
}

export const authClient = makeClient(AUTH_URL)
export const userClient = makeClient(USER_URL)
export const productClient = makeClient(PRODUCT_URL)
export const orderClient = makeClient(ORDER_URL)
export const chatClient = makeClient(CHAT_URL)
