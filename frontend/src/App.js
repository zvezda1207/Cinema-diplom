import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1>Cinema Booking System</h1>
                </header>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/admin" element={<Admin />} />
                </Routes>
            </div>
        </Router>
    );
}

function Home() {
    return (
        <div>
            <h2>Добро пожаловать в систему бронирования билетов</h2>
            <p>Выберите сеанс и забронируйте билет</p>
        </div>
    );
}

function Admin() {
    return (
        <div>
            <h2>Административная панель</h2>
            <p>Управление залами, сеансами и бронированиями</p>
        </div>
    );
}

export default App;



