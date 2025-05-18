import { Link } from 'react-router-dom';
import '../styles/Home.css';
import deviImage from '../assets/devi.webp';

const Home = () => {
    return (
        <div className="home-container">
            <header className="navbar">
                <div className="logo gradient-text">Ask Devi</div>
                <nav className="nav-links">
                    <Link to="/chat">Chat Now</Link>
                </nav>
            </header>

            <main className="hero">
                <img src={deviImage} alt="Devi" className="devi-image" />
                <h1 className="gradient-text">Ask Devi</h1>
                <p className="subtitle">Your Personal Vedic Astrologer</p>
                <Link to="/chat" className="chat-button">Chat Now</Link>
            </main>
        </div>
    );
};

export default Home;
