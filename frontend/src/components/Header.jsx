import { Link } from 'react-router-dom'
import './Header.css'

function Header() {
    return (
        <header className="page-header">
            <h1 className="page-header__title">
                <Link to="/" className="page-header__title-link">
                    Идём<span>в</span>кино
                </Link>
            </h1>
        </header>
    )
}

export default Header