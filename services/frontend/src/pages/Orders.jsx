import { useState } from 'react'
import { createOrder, getOrder } from '../api/orders.js'

export default function Orders() {
  const [userId, setUserId] = useState('')
  const [productId, setProductId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    setOrder(null)
    try {
      const data = await createOrder(parseInt(userId), parseInt(productId), parseInt(quantity))
      setOrder(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create order')
    }
  }

  return (
    <div style={{ maxWidth: 500, margin: '40px auto', padding: 24 }}>
      <h2>Create Order</h2>
      <form onSubmit={handleCreate}>
        <div style={{ marginBottom: 8 }}>
          <label>User ID: </label>
          <input type="number" value={userId} onChange={e => setUserId(e.target.value)} required />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Product ID: </label>
          <input type="number" value={productId} onChange={e => setProductId(e.target.value)} required />
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>Quantity: </label>
          <input type="number" value={quantity} onChange={e => setQuantity(e.target.value)} required />
        </div>
        <button type="submit">Place Order</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {order && (
        <div style={{ marginTop: 16, padding: 12, background: '#e8f5e9' }}>
          <h4>Order Created</h4>
          <p>Order ID: {order.id}</p>
          <p>Total Price: ${order.total_price}</p>
        </div>
      )}
    </div>
  )
}
