import { productClient } from './client.js'

export async function listProducts() {
  const { data } = await productClient.get('/products')
  return data
}

export async function createProduct(name, price) {
  const { data } = await productClient.post('/products', { name, price })
  return data
}
