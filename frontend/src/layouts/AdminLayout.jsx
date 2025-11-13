import { Outlet } from 'react-router-dom'
import '../assets/layouts/admin/CSS/normalize.css'
import '../assets/layouts/admin/CSS/styles.css'
import './AdminLayout.css'

function AdminLayout() {
    return (
        <div className="admin-page">
            <Outlet />
        </div>
    )
}

export default AdminLayout