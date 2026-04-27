import { useState, useEffect } from 'react'
import { createOrder, getAllOrders } from '../api/orders.js'

export default function Orders() {
  const [productId, setProductId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [order, setOrder] = useState(null)
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    loadOrders()
  }, [])

  async function loadOrders() {
    try {
      const data = await getAllOrders()
      setOrders(data.orders)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load orders')
      setOrders([])
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    setOrder(null)
    try {
      const data = await createOrder(parseInt(productId), parseInt(quantity))
      setOrder(data)
      setProductId('')
      setQuantity('')
      loadOrders()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create order')
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: 24 }}>
      <h2>Create Order</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: 24 }}>
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
        <div style={{ marginBottom: 24, padding: 12, background: '#e8f5e9' }}>
          <h4>Order Created</h4>
          <p>Order ID: {order.id}</p>
          <p>Total Price: ${order.total_price}</p>
        </div>
      )}
      <h3>All Orders</h3>
      <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr><th>ID</th><th>User ID</th><th>Product ID</th><th>Quantity</th><th>Total Price</th><th>Created At</th></tr>
        </thead>
        <tbody>
          {orders.length === 0 && (
            <tr><td colSpan="6" style={{ textAlign: 'center', color: '#aaa' }}>No orders yet.</td></tr>
          )}
          {orders.map(o => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{o.user_id}</td>
              <td>{o.product_id}</td>
              <td>{o.quantity}</td>
              <td>${o.total_price}</td>
              <td>{new Date(o.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
