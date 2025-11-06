import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ClientLayout from './layouts/ClientLayout'
import AdminLayout from './layouts/AdminLayout'
import Home from './pages/Home'
import Admin from './pages/Admin'
import Hall from './pages/Hall'
import './App.css'
import './index.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route element={<ClientLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/hall/:seanceId" element={<Hall />} />
          </Route>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<Admin />} />
          </Route>
        </Routes>
      </div>
    </Router>
  )
}

export default App
