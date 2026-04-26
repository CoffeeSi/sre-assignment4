import { chatClient } from './client.js'

export async function sendMessage(room, user_id, text) {
  const { data } = await chatClient.post(`/rooms/${room}/messages`, { user_id, text })
  return data
}

export async function getMessages(room, limit = 50) {
  const { data } = await chatClient.get(`/rooms/${room}/messages`, { params: { limit } })
  return data
}
