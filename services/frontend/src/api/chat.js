import { chatClient } from './client.js'

export async function sendMessage(room, text) {
  const { data } = await chatClient.post(`/rooms/${room}/messages`, { text })
  return data
}

export async function getMessages(room, limit = 50) {
  const { data } = await chatClient.get(`/rooms/${room}/messages`, { params: { limit } })
  return data
}
