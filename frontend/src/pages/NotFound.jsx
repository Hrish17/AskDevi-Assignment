import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/NotFound.css';

const NotFound = () => {
    return (
        <div className="notfound-body">
            <div className="notfound-container">
                <h1 className="notfound-title">404</h1>
                <p className="notfound-message">Oops! The page you’re looking for doesn’t exist.</p>
                <Link to="/" className="home-button">Go Back Home</Link>
            </div>
        </div >
    );
};

export default NotFound;
