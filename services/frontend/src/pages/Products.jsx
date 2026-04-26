import { useState, useEffect } from 'react'
import { listProducts, createProduct } from '../api/products.js'

export default function Products() {
  const [products, setProducts] = useState([])
  const [name, setName] = useState('')
  const [price, setPrice] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadProducts()
  }, [])

  async function loadProducts() {
    try {
      const data = await listProducts()
      setProducts(data)
    } catch {
      setError('Failed to load products')
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    setError('')
    try {
      await createProduct(name, parseFloat(price))
      setName('')
      setPrice('')
      loadProducts()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create product')
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: 24 }}>
      <h2>Products</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: 24 }}>
        <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} required style={{ marginRight: 8 }} />
        <input placeholder="Price" type="number" step="0.01" value={price} onChange={e => setPrice(e.target.value)} required style={{ marginRight: 8 }} />
        <button type="submit">Add Product</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr><th>ID</th><th>Name</th><th>Price</th></tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id}><td>{p.id}</td><td>{p.name}</td><td>${p.price}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
