import { Outlet } from 'react-router-dom'
import Header from '../components/Header'
import '../assets/layouts/admin/CSS/normalize.css'
import '../assets/layouts/admin/CSS/styles.css'
import './AdminLayout.css'

function AdminLayout() {
    return (
        <div className="admin-page">
            <Header />
            <main>
                <Outlet />
            </main>
        </div>
    )
}

export default AdminLayout

