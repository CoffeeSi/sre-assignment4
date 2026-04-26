import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <nav style={{ background: '#1976d2', padding: '12px 24px', display: 'flex', gap: 16, alignItems: 'center' }}>
      <Link to="/products" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Products</Link>
      <Link to="/orders" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Orders</Link>
      <Link to="/chat" style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>Chat</Link>
      <span style={{ flex: 1 }} />
      <button onClick={handleLogout} style={{ background: '#fff', color: '#1976d2', border: 'none', padding: '6px 14px', cursor: 'pointer', fontWeight: 'bold' }}>
        Logout
      </button>
    </nav>
  )
}
