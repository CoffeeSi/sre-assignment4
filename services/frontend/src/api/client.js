import axios from 'axios'

const host_ip = import.meta.env.VITE_HOST_IP || 'localhost'

const BACKEND_URL = `http://${host_ip}:8080`

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

export const authClient = makeClient(BACKEND_URL+'/auth')
export const userClient = makeClient(BACKEND_URL+'/users')
export const productClient = makeClient(BACKEND_URL+'/products')
export const orderClient = makeClient(BACKEND_URL+'/orders')
export const chatClient = makeClient(BACKEND_URL+'/chat')
