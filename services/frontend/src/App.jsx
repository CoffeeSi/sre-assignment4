import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Products from './pages/Products.jsx'
import Orders from './pages/Orders.jsx'
import Chat from './pages/Chat.jsx'
import Navbar from './components/Navbar.jsx'
import PrivateRoute from './components/PrivateRoute.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/products"
          element={
            <PrivateRoute>
              <Navbar />
              <Products />
            </PrivateRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <PrivateRoute>
              <Navbar />
              <Orders />
            </PrivateRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <Navbar />
              <Chat />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/products" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
