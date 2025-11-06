import { Outlet } from 'react-router-dom'
import Header from '../components/Header'
import '../assets/layouts/client/css/normalize.css'
import '../assets/layouts/client/css/styles.css'
import './ClientLayout.css'

function ClientLayout() {
    return (
        <div className="client-page">
            <Header />
            <main>
                <Outlet />
            </main>
        </div>
    )
}

export default ClientLayout

