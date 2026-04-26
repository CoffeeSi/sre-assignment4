import { orderClient } from './client.js'

export async function createOrder(user_id, product_id, quantity) {
  const { data } = await orderClient.post('/orders', { user_id, product_id, quantity })
  return data
}

export async function getOrder(order_id) {
  const { data } = await orderClient.get(`/orders/${order_id}`)
  return data
}
