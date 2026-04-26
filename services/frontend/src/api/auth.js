import { authClient } from './client.js'

export async function login(email, password) {
  const { data } = await authClient.post('/login', { email, password })
  return data
}

export async function register(email, password) {
  const { data } = await authClient.post('/register', { email, password })
  return data
}

export async function verifyToken(token) {
  const { data } = await authClient.get('/auth/verify', { params: { token } })
  return data
}
